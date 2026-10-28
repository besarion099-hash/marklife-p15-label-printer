# -*- coding: utf-8 -*-
"""Verbindung zum Drucker ueber den seriellen Bluetooth-Port.

Windows legt fuer jedes gekoppelte Geraet mit serieller Schnittstelle
COM-Ports an: einen ausgehenden (in der Geraete-ID steht die
Bluetooth-Adresse) und eingehende (Adresse 000000000000). Drucken geht
nur ueber den ausgehenden. Den Geraetenamen schreibt Windows nicht in
die Portbeschreibung; er steht in der Registry unter BTHPORT.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass

_MAC = re.compile(r"&([0-9A-Fa-f]{12})_")
# Geraetenamen der Marklife-/YXQ-Drucker (P15_ZF39F, P12_..., S15...). Solche Ports
# stehen ganz vorn, damit die Vorauswahl nicht auf einem Kopfhoerer landet.
_DRUCKERNAME = re.compile(r"^(P\d|S\d|L1\d|D\d{2,3}|X\d|U\d|Marklife)", re.IGNORECASE)
_GERAETE = r"SYSTEM\CurrentControlSet\Services\BTHPORT\Parameters\Devices"


class AnschlussFehler(Exception):
    """Der Port laesst sich nicht oeffnen oder die Verbindung reisst ab."""


@dataclass(frozen=True)
class Port:
    name: str            # "COM13"
    beschreibung: str    # "P15_ZF39F (COM13)"
    bluetooth: bool


def mac_aus_hwid(hwid: str) -> str | None:
    treffer = _MAC.search(hwid or "")
    if treffer is None or treffer.group(1) == "000000000000":
        return None
    return treffer.group(1).lower()


def bluetooth_name(mac: str) -> str | None:
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, rf"{_GERAETE}\{mac}") as schluessel:
            roh, _ = winreg.QueryValueEx(schluessel, "Name")
    except (ImportError, OSError):
        return None
    if isinstance(roh, bytes):
        roh = roh.split(b"\0", 1)[0].decode("utf-8", "replace")
    return str(roh) or None


def ports(auflisten=None, namen=bluetooth_name) -> list[Port]:
    """Alle COM-Ports, Bluetooth zuerst; eingehende Bluetooth-Ports fehlen."""
    if auflisten is None:
        from serial.tools import list_ports
        auflisten = list_ports.comports
    gefunden = []
    for eintrag in auflisten():
        hwid = getattr(eintrag, "hwid", "") or ""
        if hwid.upper().startswith("BTHENUM"):
            mac = mac_aus_hwid(hwid)
            if mac is None:
                continue
            name = namen(mac) or eintrag.description
            gefunden.append(Port(eintrag.device, f"{name} ({eintrag.device})", True))
        else:
            gefunden.append(Port(eintrag.device, eintrag.description or eintrag.device, False))
    gefunden.sort(key=lambda p: (not _DRUCKERNAME.match(p.beschreibung), not p.bluetooth,
                                 p.beschreibung.lower()))
    return gefunden


def _serial_oeffnen(portname):
    import serial
    return serial.Serial(portname, baudrate=115200, timeout=2, write_timeout=10)


class Verbindung:
    """Port oeffnen, Auftraege in Bloecken schreiben, Port wieder freigeben.

        with Verbindung("COM13") as v:
            v.schreiben(daten)

    serial.SerialException erbt von OSError; deshalb genuegt OSError.
    """

    def __init__(self, portname: str, oeffnen=_serial_oeffnen,
                 nachlauf_s: float = 1.0, schlafen=time.sleep):
        self.portname = portname
        self._oeffnen = oeffnen
        self._nachlauf_s = nachlauf_s
        self._schlafen = schlafen
        self._port = None

    def __enter__(self):
        try:
            self._port = self._oeffnen(self.portname)
        except OSError as fehler:
            raise AnschlussFehler(
                f"Der Port {self.portname} lässt sich nicht öffnen: {fehler}") from fehler
        return self

    def schreiben(self, daten: bytes, blockgroesse: int = 512, pause_ms: int = 20,
                  fortschritt=None) -> None:
        gesamt = len(daten)
        try:
            for start in range(0, gesamt, blockgroesse):
                self._port.write(daten[start:start + blockgroesse])
                if fortschritt is not None:
                    fortschritt(min(start + blockgroesse, gesamt), gesamt)
                if pause_ms:
                    self._schlafen(pause_ms / 1000)
            self._port.flush()
        except OSError as fehler:
            raise AnschlussFehler(
                f"Die Verbindung zu {self.portname} ist abgerissen: {fehler}") from fehler

    def __exit__(self, art, wert, verlauf):
        try:
            if art is None:
                self._schlafen(self._nachlauf_s)   # Drucker den Rest abarbeiten lassen
        finally:
            try:
                self._port.close()
            except OSError:
                pass
        return False
