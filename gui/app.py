# -*- coding: utf-8 -*-
"""Startpunkt: python.exe gui/app.py (siehe Etikettendrucker.bat)."""

from __future__ import annotations

import sys
import traceback
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
if str(WURZEL) not in sys.path:
    sys.path.insert(0, str(WURZEL))

from kern.orte import DATEN  # noqa: E402  (braucht den Pfad oben)

LOG = DATEN / "lauf.log"
SYMBOL = WURZEL / "gui" / "symbol.ico"
APP_ID = "Marklife.Etikettendrucker"


def venv_einbinden():
    """Pakete der venv auch dann finden, wenn die Basis-Python startet.

    Der Startmenue-Eintrag startet direkt die Basis-Python statt
    venv\\Scripts\\python.exe. Der venv-Starter ist unter Windows nur ein
    Weiterleiter, der einen zweiten Prozess erzeugt; dann gehoert das
    Fenster einem anderen Prozess, und die Konsole laesst sich nicht
    ausblenden, weil zwei Prozesse an ihr haengen.
    """
    if sys.prefix != sys.base_prefix or getattr(sys, "frozen", False):
        return                                    # laeuft schon in der venv oder als EXE
    pakete = WURZEL / "venv" / "Lib" / "site-packages"
    if pakete.is_dir():
        import site
        site.addsitedir(str(pakete))


venv_einbinden()


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


def eigene_app_id():
    """Eigene AppUserModelID (nur Windows): sonst gruppiert die Taskleiste das
    Fenster unter python.exe und zeigt dessen Symbol statt unseres."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
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
        from kern.sprache import t
        QMessageBox.critical(None, t("Etikettendrucker"),
                             t("Unerwarteter Fehler:\n{fehler}\n\nEinzelheiten in {datei}.",
                               fehler=wert, datei=LOG.name))
    except Exception:
        pass


def main() -> int:
    konsole_verstecken()
    eigene_app_id()
    sys.excepthook = _absturz_melden
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication

    from gui import aussehen
    from gui.fenster import Hauptfenster
    from gui.sprachwahl import qt_uebersetzen, sprache_fragen
    from gui.ueber import VERSION
    from kern import einstellungen, sprache
    app = QApplication(sys.argv)
    app.setApplicationName("Etikettendrucker")
    app.setApplicationVersion(VERSION)
    app.setWindowIcon(QIcon(str(SYMBOL)))
    aussehen.anwenden(app)

    pfad = einstellungen.STANDARD_PFAD
    neuer_pc = not pfad.exists()
    e = einstellungen.laden(pfad)
    if not e.sprache:                                # erster Start: Sprache fragen
        e.sprache = sprache_fragen(sprache.system_sprache())
        try:
            einstellungen.speichern(e, pfad)
        except OSError:
            pass
    sprache.setze(e.sprache)
    qt_uebersetzen(app, e.sprache)

    fenster = Hauptfenster()
    fenster.erster_start = neuer_pc
    offen = [fenster]                                # das jeweils aktuelle Fenster

    def sprache_gewechselt():
        alt = offen[0]
        qt_uebersetzen(app, sprache.aktuell())
        neu = Hauptfenster()                         # alle Texte in der neuen Sprache
        neu.uebernehmen_von(alt)
        neu.sprache_gewechselt.connect(sprache_gewechselt)
        offen[0] = neu
        neu.show()
        alt.close()
        alt.deleteLater()

    fenster.sprache_gewechselt.connect(sprache_gewechselt)
    fenster.show()
    if fenster.erster_start_ohne_drucker():
        from PySide6.QtCore import QTimer
        QTimer.singleShot(400, fenster.einrichten)       # neuer PC: gleich beim Koppeln helfen
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
