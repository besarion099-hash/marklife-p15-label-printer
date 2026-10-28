# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path

import pytest

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(scope="session")
def qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture(autouse=True)
def frische_verbindungszeit():
    """Jeder Test startet ohne Zeitmarke eines vorher geschlossenen Ports."""
    from kern.anschluss import Verbindung
    Verbindung._zuletzt_geschlossen.clear()
    yield
    Verbindung._zuletzt_geschlossen.clear()
