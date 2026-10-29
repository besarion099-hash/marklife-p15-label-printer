# -*- coding: utf-8 -*-
"""Den P15 als Windows-Drucker einrichten (Treiber des Herstellers am
Bluetooth-COM-Port), fuer den Einrichtungs-Assistenten.

Der Etikettendrucker selbst druckt direkt ueber den COM-Port und braucht
das nicht; der Windows-Drucker ist fuer Word & Co. Die Arbeit macht
treiber\\drucker_einrichten.ps1. Fehlt der Treiber noch, laeuft es mit
Administratorrechten (eine Windows-Rueckfrage), sonst ohne.
"""

from __future__ import annotations

import base64
import subprocess
import sys
import tempfile
from pathlib import Path

from kern.orte import DATEN, PROGRAMM

SKRIPT = PROGRAMM / "treiber" / "drucker_einrichten.ps1"
PAKET = DATEN / "treiber" / "p15" / "yxqpor.inf"      # portabel: neben der EXE
DRUCKERNAME = "Marklife P15"
TREIBERNAME = "P15"


class EinrichtungsFehler(Exception):
    pass


def _powershell(befehl: str, zeit=120) -> subprocess.CompletedProcess:
    # Ohne Fortschrittsanzeige schreibt PowerShell keinen CLIXML-Wust nach stderr.
    befehl = "$ProgressPreference = 'SilentlyContinue'; " + befehl
    kodiert = base64.b64encode(befehl.encode("utf-16-le")).decode("ascii")
    ohne_fenster = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    return subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive",
                           "-ExecutionPolicy", "Bypass", "-EncodedCommand", kodiert],
                          capture_output=True, text=True, encoding="oem", errors="replace",
                          timeout=zeit, creationflags=ohne_fenster)


def _zitat(text) -> str:
    """Fuer einen PowerShell-String in einfachen Anfuehrungszeichen."""
    return "'" + str(text).replace("'", "''") + "'"


def treiber_da(ausfuehren=_powershell) -> bool:
    ergebnis = ausfuehren(f"if (Get-PrinterDriver -Name {_zitat(TREIBERNAME)} "
                          "-ErrorAction SilentlyContinue) { 'ja' }", 30)
    return ergebnis.stdout.strip() == "ja"


def windows_drucker_port(ausfuehren=_powershell) -> str | None:
    """Port des Windows-Druckers "Marklife P15" ("COM13"), None wenn es ihn nicht gibt."""
    ergebnis = ausfuehren(f"(Get-Printer -Name {_zitat(DRUCKERNAME)} "
                          "-ErrorAction SilentlyContinue).PortName", 30)
    port = ergebnis.stdout.strip().rstrip(":")
    return port or None


def paket_da(paket: Path = PAKET) -> bool:
    return Path(paket).is_file()


def befehl(port: str, protokoll: Path, als_admin: bool, paket=PAKET, skript=SKRIPT) -> str:
    """Der PowerShell-Befehl, der das Skript startet (mit Admin ueber Start-Process -Verb RunAs)."""
    if als_admin:
        # Start-Process setzt Elemente mit Leerzeichen nicht selbst in Anfuehrungszeichen.
        argumente = (f'-NoProfile -ExecutionPolicy Bypass -File "{skript}" -Inf "{paket}" '
                     f'-Port {port} -Protokoll "{protokoll}"')
        return ("Start-Process powershell.exe -Verb RunAs -Wait -WindowStyle Hidden "
                f"-ArgumentList {_zitat(argumente)}")
    return (f"& {_zitat(skript)} -Inf {_zitat(paket)} -Port {_zitat(port)} "
            f"-Protokoll {_zitat(protokoll)}")


def einrichten(port: str, ausfuehren=_powershell, als_admin=None, paket=PAKET,
               skript=SKRIPT) -> str:
    """Windows-Drucker "Marklife P15" an port anlegen oder umstellen."""
    if sys.platform != "win32" and ausfuehren is _powershell:
        raise EinrichtungsFehler("Geht nur unter Windows.")
    if als_admin is None:
        als_admin = not treiber_da(ausfuehren)
    if als_admin and not paket_da(paket):
        raise EinrichtungsFehler(f"Das Treiberpaket fehlt:\n{paket}")
    with tempfile.TemporaryDirectory() as ordner:
        protokoll = Path(ordner) / "ergebnis.txt"
        ergebnis = ausfuehren(befehl(port, protokoll, als_admin, paket, skript), 300)
        text = (protokoll.read_text(encoding="utf-8-sig").strip()
                if protokoll.is_file() else "")
    if text == "OK":
        return f'Windows-Drucker "{DRUCKERNAME}" ist an {port} eingerichtet.'
    if text:
        raise EinrichtungsFehler(text.removeprefix("FEHLER: "))
    if als_admin:
        raise EinrichtungsFehler("Die Windows-Rückfrage nach Administratorrechten wurde "
                                 "abgelehnt oder ist gescheitert.")
    raise EinrichtungsFehler((ergebnis.stderr or ergebnis.stdout or "Unbekannter Fehler").strip())
