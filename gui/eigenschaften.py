# -*- coding: utf-8 -*-
"""Rechte Leiste: die Felder des gewaehlten Elements.

Je Elementart eine Liste von Feldern. Jedes Feld schreibt beim Aendern
direkt in das Element und meldet geaendert; das Fenster zeichnet dann
neu.
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDoubleSpinBox, QFileDialog, QFormLayout,
                               QLabel, QLineEdit, QPlainTextEdit, QPushButton, QVBoxLayout,
                               QWidget)

from gui.bilder import bild_lesen
from kern.etikett import Barcode, Bild, Linie, QRCode, Rahmen, Text
from kern.stile import LINIENSTILE, RAHMENSTILE
from kern.zeichnen import SCHRIFTEN

NAMEN = {Text: "Text", QRCode: "QR-Code", Barcode: "Barcode", Bild: "Bild",
         Rahmen: "Rahmen", Linie: "Linie"}
_AUSRICHTUNG = [("links", "links"), ("mitte", "Mitte"), ("rechts", "rechts")]
_BARCODES = [("code128", "Code 128"), ("ean13", "EAN-13")]
_VERFAHREN = [("schwelle", "Schwelle (Grafik, Logo)"),
              ("fehlerverteilung", "Fehlerverteilung (Foto)")]
_DREHUNG = [(0, "0°"), (90, "90°"), (180, "180°"), (270, "270°")]


class Eigenschaften(QWidget):
    geaendert = Signal()
    loeschen_gewuenscht = Signal()

    def __init__(self, eltern=None):
        super().__init__(eltern)
        self.element = None
        self.felder = {}
        self._aussen = QVBoxLayout(self)
        self._aussen.addStretch(1)
        self._inhalt = None
        self.setMinimumWidth(250)
        self.zeige(None)

    def zeige(self, element):
        self.element = element
        self.felder = {}
        if self._inhalt is not None:
            self._aussen.removeWidget(self._inhalt)
            self._inhalt.deleteLater()
        self._inhalt = QWidget(self)
        form = QFormLayout(self._inhalt)
        self._aussen.insertWidget(0, self._inhalt)
        if element is None:
            form.addRow(QLabel("Kein Element gewählt.\n\nLinks ein Werkzeug anklicken\n"
                               "oder ein Element auf dem Etikett."))
            return
        form.addRow(QLabel(f"<b>{NAMEN[type(element)]}</b>"))
        self._eigene_felder(form, element)
        self._zahl(form, "x_mm", "Links (mm)", -50, 200)
        self._zahl(form, "y_mm", "Oben (mm)", -50, 200)
        self._zahl(form, "breite_mm", "Breite (mm)", 0.125, 200)
        self._zahl(form, "hoehe_mm", "Höhe (mm)", 0.125, 200)
        self._auswahl(form, "drehung", "Drehung", _DREHUNG)
        knopf = QPushButton("Element löschen")
        knopf.clicked.connect(self.loeschen_gewuenscht.emit)
        form.addRow(knopf)

    def _eigene_felder(self, form, element):
        if isinstance(element, Text):
            self._mehrzeilig(form, "inhalt", "Text")
            self._auswahl(form, "schrift", "Schrift", [(name, name) for name in SCHRIFTEN])
            self._zahl(form, "groesse_pt", "Größe (pt)", 4, 96, 0.5)
            self._haken(form, "fett", "fett")
            self._auswahl(form, "ausrichtung", "Ausrichtung", _AUSRICHTUNG)
        elif isinstance(element, QRCode):
            self._zeile(form, "inhalt", "Inhalt")
        elif isinstance(element, Barcode):
            self._zeile(form, "inhalt", "Inhalt")
            self._auswahl(form, "art", "Art", _BARCODES)
            self._haken(form, "klartext", "Klartext darunter")
        elif isinstance(element, Bild):
            self._auswahl(form, "verfahren", "Umwandlung", _VERFAHREN)
            knopf = QPushButton("Anderes Bild …")
            knopf.clicked.connect(self._bild_waehlen)
            form.addRow(knopf)
        elif isinstance(element, Rahmen):
            self._auswahl(form, "stil", "Stil", RAHMENSTILE)
            self._zahl(form, "strich_mm", "Strich (mm)", 0.25, 5)
            self._zahl(form, "ecken_mm", "Ecken (mm)", 0, 20)
        elif isinstance(element, Linie):
            self._auswahl(form, "stil", "Stil", LINIENSTILE)
            self._zahl(form, "strich_mm", "Strich (mm)", 0.25, 5)

    def _setzen(self, name, wert):
        setattr(self.element, name, wert)
        self.geaendert.emit()

    def _zahl(self, form, name, beschriftung, kleinste, groesste, schritt=0.125):
        feld = QDoubleSpinBox()
        feld.setDecimals(3)
        feld.setRange(kleinste, groesste)
        feld.setSingleStep(schritt)
        feld.setValue(float(getattr(self.element, name)))
        feld.valueChanged.connect(lambda wert, n=name: self._setzen(n, float(wert)))
        form.addRow(beschriftung, feld)
        self.felder[name] = feld

    def _zeile(self, form, name, beschriftung):
        feld = QLineEdit(getattr(self.element, name))
        feld.textChanged.connect(lambda text, n=name: self._setzen(n, text))
        form.addRow(beschriftung, feld)
        self.felder[name] = feld

    def _mehrzeilig(self, form, name, beschriftung):
        feld = QPlainTextEdit(getattr(self.element, name))
        feld.setFixedHeight(70)
        feld.textChanged.connect(lambda n=name, f=feld: self._setzen(n, f.toPlainText()))
        form.addRow(beschriftung, feld)
        self.felder[name] = feld

    def _haken(self, form, name, beschriftung):
        feld = QCheckBox(beschriftung)
        feld.setChecked(bool(getattr(self.element, name)))
        feld.toggled.connect(lambda an, n=name: self._setzen(n, bool(an)))
        form.addRow("", feld)
        self.felder[name] = feld

    def _auswahl(self, form, name, beschriftung, moeglich):
        feld = QComboBox()
        for wert, text in moeglich:
            feld.addItem(text, wert)
        feld.setCurrentIndex(max(0, feld.findData(getattr(self.element, name))))
        feld.currentIndexChanged.connect(
            lambda i, n=name, f=feld: self._setzen(n, f.itemData(i)))
        form.addRow(beschriftung, feld)
        self.felder[name] = feld

    def aktualisieren(self):
        """Lage und Groesse nach dem Ziehen nachfuehren, ohne neu aufzubauen."""
        if self.element is None:
            return
        for name in ("x_mm", "y_mm", "breite_mm", "hoehe_mm"):
            feld = self.felder.get(name)
            if feld is not None:
                feld.blockSignals(True)
                feld.setValue(float(getattr(self.element, name)))
                feld.blockSignals(False)

    def _bild_waehlen(self):
        pfad, _ = QFileDialog.getOpenFileName(self, "Bild wählen", "",
                                              "Bilder (*.png *.jpg *.jpeg *.bmp *.gif)")
        if not pfad:
            return
        daten = bild_lesen(pfad, self)
        if daten is not None:
            self._setzen("daten", daten)
