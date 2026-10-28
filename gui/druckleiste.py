# -*- coding: utf-8 -*-
"""Leiste oben: Drucker, Groesse, Papier, Dichte, Kopien, Drucken."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QComboBox, QDoubleSpinBox, QHBoxLayout, QLabel, QPushButton,
                               QSpinBox, QToolButton, QWidget)

from kern import anschluss
from kern.etikett import GROESSEN

EIGENE = "Eigene Größe"
PAPIERE = [(2, "Etiketten mit Lücke"), (1, "Endlospapier"), (3, "Etiketten mit schwarzer Marke")]
DICHTEN = [(1, "hell"), (2, "normal"), (3, "dunkel")]


class Druckleiste(QWidget):
    geaendert = Signal()
    drucken = Signal()

    def __init__(self, einstellungen, port_quelle=anschluss.ports, eltern=None):
        super().__init__(eltern)
        self.einstellungen = einstellungen
        self._port_quelle = port_quelle
        self._druckt = False

        self.port = QComboBox()
        self.port.setMinimumWidth(230)
        neu = QToolButton()
        neu.setText("↻")
        neu.setToolTip("Drucker neu suchen")
        self.groesse = QComboBox()
        for name, _, _ in GROESSEN:
            self.groesse.addItem(name)
        self.groesse.addItem(EIGENE)
        self.eigene_b = self._mm(einstellungen.eigene_breite_mm)
        self.eigene_h = self._mm(einstellungen.eigene_hoehe_mm)
        self.papier = self._liste(PAPIERE, einstellungen.papiertyp)
        self.dichte = self._liste(DICHTEN, einstellungen.dichte)
        self.kopien = QSpinBox()
        self.kopien.setRange(1, 99)
        self.knopf = QPushButton("Drucken")

        zeile = QHBoxLayout(self)
        zeile.setContentsMargins(6, 4, 6, 4)
        for beschriftung, feld in (("Drucker:", self.port), (None, neu),
                                   ("Größe:", self.groesse), (None, self.eigene_b),
                                   (None, self.eigene_h), ("Papier:", self.papier),
                                   ("Dichte:", self.dichte), ("Kopien:", self.kopien)):
            if beschriftung:
                zeile.addWidget(QLabel(beschriftung))
            zeile.addWidget(feld)
        zeile.addStretch(1)
        zeile.addWidget(self.knopf)

        index = self.groesse.findText(einstellungen.groesse)
        self.groesse.setCurrentIndex(index if index >= 0 else self.groesse.findText("30 x 15 mm"))
        self.ports_neu()
        self._sichtbarkeit()

        neu.clicked.connect(self.ports_neu)
        self.knopf.clicked.connect(self.drucken.emit)
        for feld in (self.port, self.groesse, self.papier, self.dichte):
            feld.currentIndexChanged.connect(self._geaendert)
        for feld in (self.eigene_b, self.eigene_h):
            feld.valueChanged.connect(self._geaendert)

    @staticmethod
    def _mm(wert):
        feld = QDoubleSpinBox()
        feld.setRange(5.0, 100.0)
        feld.setDecimals(1)
        feld.setSuffix(" mm")
        feld.setValue(wert)
        return feld

    @staticmethod
    def _liste(moeglich, aktuell):
        feld = QComboBox()
        for wert, text in moeglich:
            feld.addItem(text, wert)
        feld.setCurrentIndex(max(0, feld.findData(aktuell)))
        return feld

    def ports_neu(self):
        try:
            gefunden = self._port_quelle()
        except Exception:                 # pyserial fehlt oder Windows-Schnittstelle streikt
            gefunden = []
        self.port.blockSignals(True)
        self.port.clear()
        for port in gefunden:
            self.port.addItem(port.beschreibung, port.name)
        if not gefunden:
            self.port.addItem("Kein Drucker gefunden – einschalten und in Windows koppeln", "")
        self.port.setCurrentIndex(max(0, self.port.findData(self.einstellungen.port)))
        self.port.blockSignals(False)
        self._knopf_pruefen()

    def _knopf_pruefen(self):
        self.knopf.setEnabled(bool(self.port.currentData()) and not self._druckt)

    def setze_druckt(self, druckt: bool):
        self._druckt = druckt
        self._knopf_pruefen()

    def groesse_mm(self):
        name = self.groesse.currentText()
        for eintrag, breite, hoehe in GROESSEN:
            if eintrag == name:
                return breite, hoehe
        return self.eigene_b.value(), self.eigene_h.value()

    def setze_groesse(self, breite, hoehe):
        for name, b, h in GROESSEN:
            if (b, h) == (breite, hoehe):
                self.groesse.setCurrentText(name)
                return
        self.eigene_b.setValue(breite)
        self.eigene_h.setValue(hoehe)
        self.groesse.setCurrentText(EIGENE)

    def uebernehmen(self):
        e = self.einstellungen
        e.port = self.port.currentData() or ""
        e.groesse = self.groesse.currentText()
        e.eigene_breite_mm = self.eigene_b.value()
        e.eigene_hoehe_mm = self.eigene_h.value()
        e.papiertyp = self.papier.currentData()
        e.dichte = self.dichte.currentData()

    def _sichtbarkeit(self):
        eigene = self.groesse.currentText() == EIGENE
        self.eigene_b.setVisible(eigene)
        self.eigene_h.setVisible(eigene)

    def _geaendert(self, *_):
        self._sichtbarkeit()
        self._knopf_pruefen()
        self.uebernehmen()
        self.geaendert.emit()
