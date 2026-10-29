# -*- coding: utf-8 -*-
"""Den P15 als Windows-Drucker einrichten (Treiber des Herstellers am
Bluetooth-COM-Port), fuer den Einrichtungs-Assistenten.

Der Etikettendrucker selbst druckt direkt ueber den COM-Port und braucht
das nicht; der Windows-Drucker ist fuer Word & Co. Die Arbeit macht
treiber\\drucker_einrichten.ps1.

Fehlt der Treiber, kommt er vom Hersteller: Liegt kein Paket bei
(treiber\\p15, nur in privaten Bauten), wird das offizielle ZIP von
marklifeprinter.com geladen, die Signatur des Installers geprueft und der
Installer mit Administratorrechten gestartet. So verteilt das Programm
selbst keine fremde Software.
"""

from __future__ import annotations

import base64
import io
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

from kern.orte import DATEN, PROGRAMM

SKRIPT = PROGRAMM / "treiber" / "drucker_einrichten.ps1"
PAKET = DATEN / "treiber" / "p15" / "yxqpor.inf"      # portabel: neben der EXE
DRUCKERNAME = "Marklife P15"
TREIBERNAME = "P15"
# Offizieller Download (Seite: marklifeprinter.com/Download.html, "Marklife
# Printer Driver P15 windows"); liefert ein ZIP mit P15_Printer_Driver V1.0.1.exe.
DOWNLOAD = "https://www.marklifeprinter.com/common/down/id/54.html"
DOWNLOAD_SEITE = "https://www.marklifeprinter.com/download/Marklife-Printer-Driver-P15-windows.html"
HERSTELLER = "Yinxiaoqian"           # steht im Signaturzertifikat des Installers
HOECHSTENS = 50_000_000


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


def _laden(adresse: str) -> bytes:
    anfrage = urllib.request.Request(adresse, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(anfrage, timeout=120) as antwort:
        return antwort.read(HOECHSTENS + 1)


def signiert_vom_hersteller(datei: Path, ausfuehren=_powershell) -> bool:
    ergebnis = ausfuehren(f"$s = Get-AuthenticodeSignature -LiteralPath {_zitat(datei)}; "
                          "\"$($s.Status)|$($s.SignerCertificate.Subject)\"", 60)
    status, _, inhaber = ergebnis.stdout.strip().partition("|")
    return status == "Valid" and HERSTELLER.lower() in inhaber.lower()


def installer_herunterladen(ordner: Path, laden=_laden, pruefen=signiert_vom_hersteller) -> Path:
    """Offizielles ZIP laden, den Installer auspacken und seine Signatur pruefen."""
    try:
        daten = laden(DOWNLOAD)
    except OSError as fehler:
        raise EinrichtungsFehler(f"Download vom Hersteller ging nicht ({fehler}).\n"
                                 f"Von Hand: {DOWNLOAD_SEITE}") from fehler
    if len(daten) > HOECHSTENS:
        raise EinrichtungsFehler("Der Download ist unerwartet groß.")
    try:
        archiv = zipfile.ZipFile(io.BytesIO(daten))
        eintrag = next(e for e in archiv.infolist()
                       if e.filename.lower().endswith(".exe") and not e.is_dir())
    except (zipfile.BadZipFile, StopIteration):
        raise EinrichtungsFehler("Der Download enthält keinen Treiber-Installer. "
                                 f"Von Hand: {DOWNLOAD_SEITE}") from None
    ziel = Path(ordner) / Path(eintrag.filename).name        # ohne Pfadteile aus dem ZIP
    ziel.write_bytes(archiv.read(eintrag))
    if not pruefen(ziel):
        ziel.unlink(missing_ok=True)
        raise EinrichtungsFehler("Der geladene Installer ist nicht vom Hersteller signiert "
                                 "und wurde nicht gestartet.")
    return ziel


def installer_ausfuehren(installer: Path, ausfuehren=_powershell):
    """Den Installer des Herstellers mit Administratorrechten starten und warten."""
    ergebnis = ausfuehren(f"Start-Process -FilePath {_zitat(installer)} -Verb RunAs -Wait", 900)
    if ergebnis.returncode != 0:
        raise EinrichtungsFehler("Der Treiber-Installer wurde abgebrochen oder die "
                                 "Rückfrage nach Administratorrechten abgelehnt.")


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
               skript=SKRIPT, laden=_laden, pruefen=None) -> str:
    """Windows-Drucker "Marklife P15" an port anlegen oder umstellen.

    Fehlt der Treiber: beiliegendes Paket per Skript mit Adminrechten, sonst
    Installer vom Hersteller laden und ausfuehren, danach das Skript ohne."""
    if sys.platform != "win32" and ausfuehren is _powershell:
        raise EinrichtungsFehler("Geht nur unter Windows.")
    if als_admin is None:
        als_admin = not treiber_da(ausfuehren)
    if als_admin and not paket_da(paket):
        with tempfile.TemporaryDirectory() as ordner:
            installer = installer_herunterladen(
                Path(ordner), laden,
                pruefen or (lambda datei: signiert_vom_hersteller(datei, ausfuehren)))
            installer_ausfuehren(installer, ausfuehren)
        als_admin = False                     # Paket liegt jetzt im Treiberspeicher
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
