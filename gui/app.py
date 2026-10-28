# -*- coding: utf-8 -*-
"""Startpunkt: python.exe gui/app.py (siehe Etikettendrucker.bat)."""

from __future__ import annotations

import sys
import traceback
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
if str(WURZEL) not in sys.path:
    sys.path.insert(0, str(WURZEL))
LOG = WURZEL / "lauf.log"


def konsole_verstecken():
    """Das schwarze Konsolenfenster ausblenden (nur Windows).

    Wo Smart App Control pythonw.exe blockiert, startet die Verknuepfung
    python.exe, und dazu gehoert eine Konsole. Sicherheitsnetz: nur
    ausblenden, wenn die Konsole allein zu uns gehoert
    (GetConsoleProcessList == 1); sonst verschwaende beim Start aus einem
    Terminal dessen Fenster mit.
    """
    if sys.platform != "win32":
        return
    try:
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.windll.kernel32
        fenster = kernel.GetConsoleWindow()
        if not fenster:
            return
        puffer = (wintypes.DWORD * 4)()
        if kernel.GetConsoleProcessList(puffer, 4) == 1:
            ctypes.windll.user32.ShowWindow(fenster, 0)       # 0 = SW_HIDE
    except Exception:
        pass                                                  # Komfort, kein Muss


def _absturz_melden(art, wert, verlauf):
    text = "".join(traceback.format_exception(art, wert, verlauf))
    try:
        with LOG.open("a", encoding="utf-8") as datei:
            datei.write(text + "\n")
    except OSError:
        pass
    try:
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.critical(None, "Etikettendrucker",
                             f"Unerwarteter Fehler:\n{wert}\n\nEinzelheiten in {LOG.name}.")
    except Exception:
        pass


def main() -> int:
    konsole_verstecken()
    sys.excepthook = _absturz_melden
    from PySide6.QtWidgets import QApplication

    from gui.fenster import Hauptfenster
    app = QApplication(sys.argv)
    app.setApplicationName("Etikettendrucker")
    fenster = Hauptfenster()
    fenster.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
