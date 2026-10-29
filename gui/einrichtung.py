# -*- coding: utf-8 -*-
"""Einrichtungs-Assistent: P15 per Bluetooth koppeln, auf Wunsch als
Windows-Drucker einrichten, Port uebernehmen."""

from __future__ import annotations

import os

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (QCheckBox, QLabel, QPushButton, QVBoxLayout, QWizard,
                               QWizardPage)

from kern import anschluss, einrichtung

KOPPELN = (
    "<ol>"
    "<li>Den P15 einschalten. Ist ein Handy mit ihm verbunden, dort Bluetooth "
    "ausschalten oder die Marklife-App schließen.</li>"
    "<li>Auf <b>„Bluetooth-Einstellungen öffnen“</b> klicken, dann "
    "<b>Gerät hinzufügen › Bluetooth</b>.</li>"
    "<li>Den Eintrag <b>P15_…</b> wählen, <i>nicht</i> den mit <b>_BLE</b> am Ende. "
    "Fragt Windows nach einer PIN, ist es meist 0000.</li>"
    "</ol>"
    "<p>Sobald Windows den Drucker gekoppelt hat, erscheint er unten.</p>")


def bluetooth_oeffnen():
    os.startfile("ms-settings:bluetooth")         # nur Windows


class KoppelnSeite(QWizardPage):
    def __init__(self, port_quelle, oeffnen):
        super().__init__()
        self.setTitle("1. Drucker per Bluetooth koppeln")
        self._port_quelle = port_quelle
        self.port = None
        text = QLabel(KOPPELN)
        text.setWordWrap(True)
        knopf = QPushButton("Bluetooth-Einstellungen öffnen")
        knopf.setAutoDefault(False)              # Enter bedeutet "Weiter"
        knopf.clicked.connect(lambda *_: oeffnen())
        self.status = QLabel()
        self.status.setWordWrap(True)
        spalte = QVBoxLayout(self)
        spalte.addWidget(text)
        spalte.addWidget(knopf, 0, Qt.AlignmentFlag.AlignLeft)
        spalte.addSpacing(12)
        spalte.addWidget(self.status)
        spalte.addStretch(1)
        self.uhr = QTimer(self)
        self.uhr.setInterval(2000)
        self.uhr.timeout.connect(self.suchen)

    def initializePage(self):
        self.suchen()
        self.uhr.start()

    def cleanupPage(self):
        self.uhr.stop()

    def suchen(self):
        try:
            gefunden = self._port_quelle()
        except Exception:
            gefunden = []
        port = anschluss.drucker_port(gefunden)
        if port != self.port:
            self.port = port
            self.completeChanged.emit()
        if port is None:
            self.status.setText("<span style='color:#a05a00'>⏳ Noch kein P15 gekoppelt – "
                                "suche alle 2 Sekunden …</span>")
        else:
            self.status.setText(f"<span style='color:#11772d'><b>✔ Gefunden: "
                                f"{port.beschreibung}</b></span>")

    def isComplete(self):
        return self.port is not None


class WindowsDruckerSeite(QWizardPage):
    """Optional: Windows-Drucker mit dem Treiber des Herstellers anlegen."""

    def __init__(self, koppeln, werkzeug):
        super().__init__()
        self.setTitle("2. Als Windows-Drucker einrichten (freiwillig)")
        self._koppeln = koppeln
        self._werkzeug = werkzeug
        text = QLabel(
            "Der Etikettendrucker braucht das nicht, er druckt direkt. Wer aber auch "
            "aus Word, dem Browser oder anderen Programmen auf den P15 drucken will, "
            "richtet hier den Windows-Drucker <b>„Marklife P15“</b> mit dem Treiber des "
            "Herstellers ein. Fehlt der Treiber noch, fragt Windows einmal nach "
            "Administratorrechten.")
        text.setWordWrap(True)
        self.wahl = QCheckBox("Windows-Drucker „Marklife P15“ einrichten")
        self.knopf = QPushButton("Jetzt einrichten")
        self.knopf.setAutoDefault(False)
        self.knopf.clicked.connect(lambda *_: self.einrichten())
        self.status = QLabel()
        self.status.setWordWrap(True)
        self.status.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        spalte = QVBoxLayout(self)
        spalte.addWidget(text)
        spalte.addSpacing(8)
        spalte.addWidget(self.wahl)
        spalte.addWidget(self.knopf, 0, Qt.AlignmentFlag.AlignLeft)
        spalte.addSpacing(8)
        spalte.addWidget(self.status)
        spalte.addStretch(1)
        self.wahl.toggled.connect(self.knopf.setEnabled)

    def initializePage(self):
        port = self._koppeln.port.name
        vorhanden = self._werkzeug.windows_drucker_port()
        if vorhanden == port:
            self.wahl.setChecked(False)
            self.knopf.setEnabled(False)
            self.status.setText(f"<span style='color:#11772d'>✔ Schon eingerichtet: "
                                f"„{einrichtung.DRUCKERNAME}“ an {port}.</span>")
        else:
            self.wahl.setChecked(True)
            self.knopf.setEnabled(True)
            hinweis = f" (bisher an {vorhanden})" if vorhanden else ""
            text = f"Wird an {port} eingerichtet{hinweis}."
            if not self._werkzeug.treiber_da() and not self._werkzeug.paket_da():
                text += ("<br>Der Treiber kommt vom Hersteller: Das Programm lädt ihn von "
                         "marklifeprinter.com (ca. 6 MB), prüft die Signatur und startet "
                         "das Installationsprogramm des Herstellers. Dort einfach "
                         "durchklicken.")
            self.status.setText(text)

    def einrichten(self) -> bool:
        QGuiApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            meldung = self._werkzeug.einrichten(self._koppeln.port.name)
        except einrichtung.EinrichtungsFehler as fehler:
            self.status.setText(f"<span style='color:#c00000'>Hat nicht geklappt: {fehler}"
                                "<br>Haken entfernen, um ohne Windows-Drucker weiterzugehen."
                                "</span>")
            return False
        finally:
            QGuiApplication.restoreOverrideCursor()
        self.status.setText(f"<span style='color:#11772d'><b>✔ {meldung}</b></span>")
        self.wahl.setChecked(False)
        return True

    def validatePage(self):
        """Weiter mit Haken, aber ohne "Jetzt einrichten": dann jetzt einrichten."""
        return not self.wahl.isChecked() or self.einrichten()


class FertigSeite(QWizardPage):
    def __init__(self, koppeln):
        super().__init__()
        self.setTitle("3. Fertig")
        self._koppeln = koppeln
        self.text = QLabel()
        self.text.setWordWrap(True)
        QVBoxLayout(self).addWidget(self.text)

    def initializePage(self):
        self.text.setText(
            f"Der Etikettendrucker druckt jetzt auf <b>{self._koppeln.port.beschreibung}</b>."
            "<br><br>Tipp: Sitzt der Druck nicht ganz auf dem Etikett, hilft "
            "<b>Drucker › Lage feinjustieren</b>.")


class _Werkzeug:
    """Die Windows-Schritte; im Test ersetzbar."""
    treiber_da = staticmethod(einrichtung.treiber_da)
    paket_da = staticmethod(einrichtung.paket_da)
    windows_drucker_port = staticmethod(einrichtung.windows_drucker_port)
    einrichten = staticmethod(einrichtung.einrichten)


class EinrichtungsAssistent(QWizard):
    def __init__(self, port_quelle=anschluss.ports, werkzeug=None, oeffnen=bluetooth_oeffnen,
                 eltern=None):
        super().__init__(eltern)
        self.setWindowTitle("Drucker einrichten")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setButtonText(QWizard.WizardButton.NextButton, "Weiter >")
        self.setButtonText(QWizard.WizardButton.BackButton, "< Zurück")
        self.setButtonText(QWizard.WizardButton.FinishButton, "Fertig")
        self.setButtonText(QWizard.WizardButton.CancelButton, "Abbrechen")
        self.koppeln = KoppelnSeite(port_quelle, oeffnen)
        self.windows = WindowsDruckerSeite(self.koppeln, werkzeug or _Werkzeug())
        self.addPage(self.koppeln)
        self.addPage(self.windows)
        self.addPage(FertigSeite(self.koppeln))
        self.resize(620, 460)

    @property
    def port(self):
        return self.koppeln.port
