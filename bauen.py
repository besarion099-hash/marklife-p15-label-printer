# -*- coding: utf-8 -*-
"""Baut die portable Fassung zum Weitergeben.

Ergebnis: dist\\Etikettendrucker\\ (Etikettendrucker.exe + _internal) und
dist\\Etikettendrucker-<Version>-portabel.zip. Auf dem Ziel-PC entpacken und
die EXE starten, ohne Python. Einstellungen, lauf.log und eigene Aufkleber
landen neben der EXE (kern.orte).

Aufruf (einmalig vorher: venv\\Scripts\\python.exe -m pip install -r requirements-bau.txt):
    venv\\Scripts\\python.exe bauen.py

Mit hinein kommen nur die freien Tabler Icons (MIT), nicht die Aufkleber
aus der Marklife-App (aufkleber\\marklife) - die gehoeren dem Hersteller.
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

LIESMICH = f"""Etikettendrucker {VERSION} (portabel) - Etiketten für den Marklife P15

Start: {NAME}.exe doppelklicken. Python ist nicht nötig.

Erster Start auf einem neuen PC:
  1. Den P15 einschalten und in Windows unter Einstellungen > Bluetooth
     koppeln (Handy vorher trennen).
  2. Im Programm oben bei "Drucker" den P15 wählen.

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


def main() -> int:
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
        "--exclude-module", "tkinter", "--exclude-module", "pytest",
        "--distpath", str(DIST), "--workpath", str(BAU), "--specpath", str(BAU),
        str(HIER / "gui" / "app.py"),
    ])
    ordner = DIST / NAME
    (ordner / "aufkleber" / "eigene").mkdir(parents=True, exist_ok=True)
    (ordner / "LIESMICH.txt").write_text(LIESMICH, encoding="utf-8")
    shutil.copy2(HIER / "Anleitung.txt", ordner / "Anleitung.txt")
    archiv = shutil.make_archive(str(DIST / f"{NAME}-{VERSION}-portabel"), "zip", DIST, NAME)
    groesse = Path(archiv).stat().st_size / 1e6
    print(f"\nFertig: {ordner}\n        {archiv} ({groesse:.0f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
