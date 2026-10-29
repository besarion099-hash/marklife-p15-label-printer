# -*- coding: utf-8 -*-
import re
import subprocess
from pathlib import Path

import pytest

from kern import anschluss, einrichtung
from kern.anschluss import Port

P15 = Port("COM13", "P15_ZF39F (COM13)", True)
KOPFHOERER = Port("COM7", "JBL Flip (COM7)", True)
USB = Port("COM3", "USB-SERIAL CH340 (COM3)", False)


class FalschesPowershell:
    """Spielt PowerShell: merkt sich Befehle, schreibt das Protokoll wie das Skript."""

    def __init__(self, treiber=True, ergebnis="OK"):
        self.treiber, self.ergebnis, self.befehle = treiber, ergebnis, []

    def __call__(self, befehl, zeit=0):
        self.befehle.append(befehl)
        ausgabe = ""
        if "Get-PrinterDriver" in befehl and "-Protokoll" not in befehl:
            ausgabe = "ja" if self.treiber else ""
        treffer = re.search(r"""-Protokoll ['"]([^'"]+)['"]""", befehl)
        if treffer and self.ergebnis is not None:
            Path(treffer.group(1)).write_text(self.ergebnis, encoding="utf-8")
        return subprocess.CompletedProcess([], 0, ausgabe, "")


def test_drucker_port_nimmt_nur_den_gekoppelten_drucker():
    assert anschluss.drucker_port([KOPFHOERER, USB, P15]) == P15
    assert anschluss.drucker_port([KOPFHOERER, USB]) is None


def test_admin_befehl_setzt_pfade_mit_leerzeichen_in_anfuehrungszeichen(tmp_path):
    skript = Path(r"C:\Mein Ordner\treiber\drucker_einrichten.ps1")
    paket = Path(r"C:\Mein Ordner\treiber\p15\yxqpor.inf")
    befehl = einrichtung.befehl("COM5", tmp_path / "e.txt", True, paket, skript)
    assert "-Verb RunAs" in befehl
    assert f'-File "{skript}"' in befehl and f'-Inf "{paket}"' in befehl


def test_einrichten_ohne_admin_wenn_treiber_da(tmp_path):
    ps = FalschesPowershell(treiber=True)
    meldung = einrichtung.einrichten("COM5", ps, paket=tmp_path / "fehlt.inf")
    assert "COM5" in meldung
    assert "RunAs" not in ps.befehle[-1]


def test_einrichten_mit_admin_wenn_treiber_fehlt(tmp_path):
    paket = tmp_path / "yxqpor.inf"
    paket.write_text("x")
    ps = FalschesPowershell(treiber=False)
    einrichtung.einrichten("COM5", ps, paket=paket)
    assert "-Verb RunAs" in ps.befehle[-1]


def test_ohne_treiber_und_ohne_paket_kommt_klare_meldung(tmp_path):
    with pytest.raises(einrichtung.EinrichtungsFehler, match="Treiberpaket fehlt"):
        einrichtung.einrichten("COM5", FalschesPowershell(treiber=False),
                               paket=tmp_path / "fehlt.inf")


def test_fehler_des_skripts_wird_weitergegeben(tmp_path):
    ps = FalschesPowershell(ergebnis="FEHLER: Zugriff verweigert")
    with pytest.raises(einrichtung.EinrichtungsFehler, match="^Zugriff verweigert$"):
        einrichtung.einrichten("COM5", ps)


def test_abgelehnte_rueckfrage(tmp_path):
    paket = tmp_path / "yxqpor.inf"
    paket.write_text("x")
    ps = FalschesPowershell(treiber=False, ergebnis=None)
    with pytest.raises(einrichtung.EinrichtungsFehler, match="Administratorrechten"):
        einrichtung.einrichten("COM5", ps, paket=paket)


def test_skript_ist_gueltiges_powershell():
    befehl = ("$f=$null;$e=$null;[void][System.Management.Automation.Language.Parser]::ParseFile("
              f"'{einrichtung.SKRIPT}',[ref]$f,[ref]$e);$e.Count")
    ergebnis = subprocess.run(["powershell.exe", "-NoProfile", "-Command", befehl],
                              capture_output=True, text=True, timeout=60)
    assert ergebnis.stdout.strip() == "0", ergebnis.stdout + ergebnis.stderr


# --- Assistent -------------------------------------------------------------------

class FalschesWerkzeug:
    def __init__(self, vorhanden=None, treiber=True, paket=True, fehler=None):
        self.vorhanden, self.treiber, self.paket, self.fehler = vorhanden, treiber, paket, fehler
        self.eingerichtet = []

    def treiber_da(self):
        return self.treiber

    def paket_da(self):
        return self.paket

    def windows_drucker_port(self):
        return self.vorhanden

    def einrichten(self, port):
        if self.fehler:
            raise einrichtung.EinrichtungsFehler(self.fehler)
        self.eingerichtet.append(port)
        return "eingerichtet"


def _assistent(gefunden, werkzeug=None):
    from gui.einrichtung import EinrichtungsAssistent
    geoeffnet = []
    assistent = EinrichtungsAssistent(lambda: list(gefunden), werkzeug or FalschesWerkzeug(),
                                      lambda: geoeffnet.append(True))
    return assistent, geoeffnet


def test_koppeln_wartet_auf_den_p15(qapp):
    gefunden = [KOPFHOERER]
    assistent, _ = _assistent(gefunden)
    seite = assistent.koppeln
    seite.initializePage()
    assert not seite.isComplete()
    gefunden.append(P15)                   # Windows hat gekoppelt
    seite.suchen()
    assert seite.isComplete() and assistent.port == P15
    seite.cleanupPage()


def test_windows_drucker_wird_beim_weiter_eingerichtet(qapp):
    werkzeug = FalschesWerkzeug()
    assistent, _ = _assistent([P15], werkzeug)
    assistent.koppeln.suchen()
    seite = assistent.windows
    seite.initializePage()
    assert seite.wahl.isChecked()
    assert seite.validatePage()
    assert werkzeug.eingerichtet == ["COM13"]


def test_schon_eingerichtet_fragt_nicht_nach_admin(qapp):
    werkzeug = FalschesWerkzeug(vorhanden="COM13")
    assistent, _ = _assistent([P15], werkzeug)
    assistent.koppeln.suchen()
    assistent.windows.initializePage()
    assert not assistent.windows.wahl.isChecked()
    assert assistent.windows.validatePage() and werkzeug.eingerichtet == []


def test_ohne_treiberpaket_laesst_sich_ueberspringen(qapp):
    assistent, _ = _assistent([P15], FalschesWerkzeug(treiber=False, paket=False))
    assistent.koppeln.suchen()
    assistent.windows.initializePage()
    assert not assistent.windows.wahl.isEnabled() and assistent.windows.validatePage()


def test_fehlschlag_haelt_an(qapp):
    assistent, _ = _assistent([P15], FalschesWerkzeug(fehler="kaputt"))
    assistent.koppeln.suchen()
    assistent.windows.initializePage()
    assert not assistent.windows.validatePage()
    assert "kaputt" in assistent.windows.status.text()
