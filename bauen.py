# -*- coding: utf-8 -*-
"""Baut die portable Fassung zum Weitergeben.

Ergebnis: dist\\Etikettendrucker\\ (Etikettendrucker.exe + _internal) und
dist\\Etikettendrucker-<Version>-portabel.zip. Auf dem Ziel-PC entpacken und
die EXE starten, ohne Python. Einstellungen, lauf.log und eigene Aufkleber
landen neben der EXE (kern.orte).

Aufruf (einmalig vorher: venv\\Scripts\\python.exe -m pip install -r requirements-bau.txt):
    venv\\Scripts\\python.exe bauen.py                  zum Veroeffentlichen
    venv\\Scripts\\python.exe bauen.py --mit-treiber    nur fuer eigene PCs

Mit hinein kommen nur die freien Tabler Icons (MIT), nicht die Aufkleber
aus der Marklife-App (aufkleber\\marklife) - die gehoeren dem Hersteller.

Den Windows-Treiber des P15 laedt der Einrichtungs-Assistent beim
Hersteller. Nur mit --mit-treiber kommt das Treiberpaket (YinXiaoQian,
signiert, darf nicht oeffentlich verteilt werden) nach treiber\\p15 neben
die EXE, dann geht die Einrichtung auch ohne Internet. Fehlt es im
Quellordner, holt bauen.py es aus dem Windows-Treiberspeicher dieses PCs.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))

from gui.ueber import AUTOR, VERSION  # noqa: E402

NAME = "Etikettendrucker"
BAU = HIER / "build"
DIST = HIER / "dist"
TABLER = HIER / "aufkleber" / "tabler"
TREIBER = HIER / "treiber" / "p15"
SPEICHER = Path(os.environ.get("WINDIR", r"C:\Windows")) / "System32" / "DriverStore" / "FileRepository"
PAKETDATEIEN = ["yxqpor.inf", "YinXiaoQian.cat", "P15x.GPD", "P15.INI", "amd64"]

LIESMICH = f"""Etikettendrucker {VERSION} (portabel) - Etiketten für den Marklife P15

Start: {NAME}.exe doppelklicken. Python ist nicht nötig.
(English: README.txt)

Erster Start auf einem neuen PC:
  Zuerst fragt das Programm nach der Sprache (Deutsch oder Englisch;
  später im Menü "Sprache / Language" änderbar).
  Ist noch kein P15 gekoppelt, öffnet sich der Einrichtungs-Assistent
  (später auch über Drucker > Einrichten):
  1. Bluetooth: Er öffnet die Windows-Einstellungen und meldet, sobald
     der P15 gekoppelt ist (Handy vorher trennen).
  2. Freiwillig: Er richtet den Windows-Drucker "Marklife P15" mit dem
     Treiber des Herstellers ein, damit man auch aus Word & Co. drucken
     kann. Den Treiber lädt er von marklifeprinter.com, prüft die
     Signatur und startet das Installationsprogramm des Herstellers.
     Windows fragt dafür einmal nach Administratorrechten.
  3. Fertig: Das Programm druckt auf den gefundenen P15.

Warnt Windows beim ersten Start ("Der Computer wurde durch Windows
geschützt"): auf "Weitere Informationen" und "Trotzdem ausführen" klicken.
Das Programm ist nicht digital signiert.

Ist "Intelligente App-Steuerung" (Smart App Control) eingeschaltet,
startet die EXE gar nicht. Dann den Weg mit install.bat aus dem
Quellordner nehmen.

Der Ordner lässt sich verschieben oder auf einen USB-Stick kopieren.
Einstellungen (einstellungen.json) und Fehlerprotokoll (lauf.log) liegen
hier neben der EXE, eigene Aufkleber-Grafiken in aufkleber\\eigene.

Mehr in Anleitung.txt.
"""

README = f"""Label Printer {VERSION} (portable) - labels for the Marklife P15

Start: double-click {NAME}.exe. Python is not needed.
(Deutsch: LIESMICH.txt)

First start on a new PC:
  The program first asks for the language (German or English; can be
  changed later in the "Sprache / Language" menu).
  If no P15 is paired yet, the setup assistant opens
  (later also via Printer > Setup):
  1. Bluetooth: it opens the Windows settings and reports as soon as the
     P15 is paired (disconnect your phone first).
  2. Optional: it sets up the Windows printer "Marklife P15" with the
     manufacturer's driver, so you can also print from Word and other
     programs. It downloads the driver from marklifeprinter.com, checks
     its signature and starts the manufacturer's installer. Windows asks
     once for administrator rights.
  3. Done: the program prints to the P15 it found.

If Windows warns on first start ("Windows protected your PC"): click
"More info" and "Run anyway". The program is not digitally signed.

If "Smart App Control" is switched on, the EXE does not start at all.
Then use install.bat from the source code instead.

The folder can be moved or copied to a USB stick. Settings
(einstellungen.json) and the error log (lauf.log) are stored next to the
EXE, your own sticker graphics go into aufkleber\\eigene.

More in Manual.txt.
"""

VERSIONSDATEI = """VSVersionInfo(
  ffi=FixedFileInfo(filevers={zahlen}, prodvers={zahlen}),
  kids=[StringFileInfo([StringTable('040704B0', [
    StringStruct('CompanyName', '{autor}'),
    StringStruct('FileDescription', 'Etiketten gestalten und auf dem Marklife P15 drucken'),
    StringStruct('FileVersion', '{version}'),
    StringStruct('ProductName', '{name}'),
    StringStruct('ProductVersion', '{version}'),
    StringStruct('LegalCopyright', '{autor}')])]),
    VarFileInfo([VarStruct('Translation', [0x0407, 1200])])])
"""


def versionsdatei() -> Path:
    teile = [int(t) for t in VERSION.split(".")]
    zahlen = tuple((teile + [0, 0, 0, 0])[:4])
    pfad = BAU / "version.txt"
    pfad.write_text(VERSIONSDATEI.format(zahlen=zahlen, autor=AUTOR, version=VERSION, name=NAME),
                    encoding="utf-8")
    return pfad


def daten(quelle: Path, ziel: str) -> list:
    return ["--add-data", f"{quelle}{os.pathsep}{ziel}"]


def treiberpaket() -> Path | None:
    """treiber\\p15 im Quellordner, sonst aus dem Treiberspeicher dieses PCs kopiert."""
    if (TREIBER / "yxqpor.inf").is_file():
        return TREIBER
    funde = sorted(SPEICHER.glob("yxqpor.inf_amd64_*"), key=lambda p: p.stat().st_mtime)
    if not funde:
        return None
    TREIBER.mkdir(parents=True, exist_ok=True)
    for name in PAKETDATEIEN:
        quelle = funde[-1] / name
        if quelle.is_dir():
            shutil.copytree(quelle, TREIBER / name, dirs_exist_ok=True)
        else:
            shutil.copy2(quelle, TREIBER / name)
    return TREIBER


def main(argumente=None) -> int:
    mit_treiber = "--mit-treiber" in (sys.argv[1:] if argumente is None else argumente)
    if not (TABLER / "icons.json").is_file():
        print("aufkleber\\tabler fehlt - erst install.bat oder aufkleber_holen.py ausführen.")
        return 1
    import PyInstaller.__main__
    BAU.mkdir(exist_ok=True)
    PyInstaller.__main__.run([
        "--noconfirm", "--clean", "--windowed", "--name", NAME,
        "--icon", str(HIER / "gui" / "symbol.ico"),
        "--version-file", str(versionsdatei()),
        "--paths", str(HIER),
        *daten(HIER / "gui" / "symbol.png", "gui"),
        *daten(HIER / "gui" / "symbol.ico", "gui"),
        *daten(TABLER, "aufkleber/tabler"),
        *daten(HIER / "treiber" / "drucker_einrichten.ps1", "treiber"),
        "--exclude-module", "tkinter", "--exclude-module", "pytest",
        "--distpath", str(DIST), "--workpath", str(BAU), "--specpath", str(BAU),
        str(HIER / "gui" / "app.py"),
    ])
    ordner = DIST / NAME
    (ordner / "aufkleber" / "eigene").mkdir(parents=True, exist_ok=True)
    (ordner / "LIESMICH.txt").write_text(LIESMICH, encoding="utf-8")
    (ordner / "README.txt").write_text(README, encoding="utf-8")
    for anleitung in ("Anleitung.txt", "Manual.txt"):
        shutil.copy2(HIER / anleitung, ordner / anleitung)
    zusatz = ""
    if mit_treiber:
        paket = treiberpaket()
        if paket is None:
            print("Hinweis: kein P15-Treiberpaket gefunden - der Assistent lädt ihn "
                  "dann beim Hersteller.")
        else:
            shutil.copytree(paket, ordner / "treiber" / "p15", dirs_exist_ok=True)
            zusatz = "-mit-treiber"                # nicht veroeffentlichen
    archiv = shutil.make_archive(str(DIST / f"{NAME}-{VERSION}-portabel{zusatz}"), "zip",
                                 DIST, NAME)
    groesse = Path(archiv).stat().st_size / 1e6
    print(f"\nFertig: {ordner}\n        {archiv} ({groesse:.0f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
