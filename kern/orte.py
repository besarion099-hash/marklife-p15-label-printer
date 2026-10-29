# -*- coding: utf-8 -*-
"""Wo das Programm seine Dateien findet.

PROGRAMM: mitgelieferte Dateien (Aufkleber-Sammlung). DATEN: was das
Programm schreibt oder der Nutzer ablegt (einstellungen.json, lauf.log,
aufkleber/eigene). Im Quellordner ist beides derselbe Ordner. In der
portablen Fassung (PyInstaller) steckt PROGRAMM in _internal, DATEN ist
der Ordner der EXE - so bleibt alles zusammen und laesst sich mitnehmen.
"""

from __future__ import annotations

import sys
from pathlib import Path


def ordner(eingefroren=None, exe=None, meipass=None):
    """(PROGRAMM, DATEN); die Argumente gibt es nur fuer Tests."""
    if eingefroren is None:
        eingefroren = getattr(sys, "frozen", False)
    if eingefroren:
        exe = Path(exe or sys.executable).resolve().parent
        return Path(meipass or getattr(sys, "_MEIPASS", exe)), exe
    quelle = Path(__file__).resolve().parent.parent
    return quelle, quelle


PROGRAMM, DATEN = ordner()
