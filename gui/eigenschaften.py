# -*- coding: utf-8 -*-
"""Rechte Leiste: die Felder des gewaehlten Elements.

Je Elementart eine Liste von Feldern. Jedes Feld schreibt beim Aendern
direkt in das Element und meldet geaendert; das Fenster zeichnet dann
neu.
"""

from __future__ import annotations

from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDoubleSpinBox, QFileDialog, QFormLayout,
                               QLabel, QLineEdit, QPlainTextEdit, QPushButton, QVBoxLayout,
                               QWidget)

from gui import formen
from gui.bilder import bild_lesen
from kern.etikett import Barcode, Bild, Linie, QRCode, Rahmen, Text
from kern import stile
from kern.stile import LINIENSTILE, RAHMENSTILE
from kern.sprache import N_, t
from kern.zeichnen import SCHRIFTEN

NAMEN = {Text: N_("Text"), QRCode: N_("QR-Code"), Barcode: N_("Barcode"), Bild: N_("Bild"),
         Rahmen: N_("Rahmen"), Linie: N_("Linie")}
_AUSRICHTUNG = [("links", N_("links")), ("mitte", N_("Mitte")), ("rechts", N_("rechts"))]
_BARCODES = [("code128", "Code 128"), ("ean13", "EAN-13")]
_VERFAHREN = [("schwelle", N_("Schwelle (Grafik, Logo)")),
              ("fehlerverteilung", N_("Fehlerverteilung (Foto)"))]
_DREHUNG = [(0, "0°"), (90, "90°"), (180, "180°"), (270, "270°")]


class Eigenschaften(QWidget):
    geaendert = Signal()
    loeschen_gewuenscht = Signal()

    def __init__(self, eltern=None):
        super().__init__(eltern)
        self.element = None
        self.felder = {}
        self.form_waehlen = formen.form_waehlen     # im Test ersetzbar
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
            form.addRow(QLabel(t("Kein Element gewählt.\n\nLinks ein Werkzeug anklicken\n"
                                 "oder ein Element auf dem Etikett.")))
            return
        form.addRow(QLabel(f"<b>{t(NAMEN[type(element)])}</b>"))
        self._eigene_felder(form, element)
        self._zahl(form, "x_mm", t("Links (mm)"), -50, 200)
        self._zahl(form, "y_mm", t("Oben (mm)"), -50, 200)
        self._zahl(form, "breite_mm", t("Breite (mm)"), 0.125, 200)
        self._zahl(form, "hoehe_mm", t("Höhe (mm)"), 0.125, 200)
        self._auswahl(form, "drehung", t("Drehung"), _DREHUNG)
        knopf = QPushButton(t("Element löschen"))
        knopf.clicked.connect(self.loeschen_gewuenscht.emit)
        form.addRow(knopf)

    def _eigene_felder(self, form, element):
        if isinstance(element, Text):
            self._mehrzeilig(form, "inhalt", t("Text"))
            self._auswahl(form, "schrift", t("Schrift"), [(name, name) for name in SCHRIFTEN])
            self._zahl(form, "groesse_pt", t("Größe (pt)"), 4, 96, 0.5)
            self._haken(form, "fett", t("fett"))
            self._auswahl(form, "ausrichtung", t("Ausrichtung"), _AUSRICHTUNG)
        elif isinstance(element, QRCode):
            self._zeile(form, "inhalt", t("Inhalt"))
        elif isinstance(element, Barcode):
            self._zeile(form, "inhalt", t("Inhalt"))
            self._auswahl(form, "art", t("Art"), _BARCODES)
            self._haken(form, "klartext", t("Klartext darunter"))
        elif isinstance(element, Bild):
            self._auswahl(form, "verfahren", t("Umwandlung"), _VERFAHREN)
            knopf = QPushButton(t("Anderes Bild …"))
            knopf.clicked.connect(self._bild_waehlen)
            form.addRow(knopf)
        elif isinstance(element, Rahmen):
            self._form(form, "rahmen", RAHMENSTILE)
            self._zahl(form, "strich_mm", t("Strich (mm)"), 0.25, 5)
            self._zahl(form, "ecken_mm", t("Ecken (mm)"), 0, 20)
        elif isinstance(element, Linie):
            self._form(form, "linie", LINIENSTILE)
            self._zahl(form, "strich_mm", t("Strich (mm)"), 0.25, 5)

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
            feld.addItem(t(text), wert)
        feld.setCurrentIndex(max(0, feld.findData(getattr(self.element, name))))
        feld.currentIndexChanged.connect(
            lambda i, n=name, f=feld: self._setzen(n, f.itemData(i)))
        form.addRow(beschriftung, feld)
        self.felder[name] = feld

    def _form(self, form, art, moeglich):
        """Knopf mit Vorschau der aktuellen Form; Klick oeffnet die Galerie."""
        namen = dict(moeglich)
        knopf = QPushButton(t(namen.get(self.element.stil, self.element.stil)) + " …")
        knopf.setIcon(QIcon(QPixmap.fromImage(formen.vorschau(art, self.element.stil))))
        knopf.setIconSize(QSize(72, 24))
        knopf.setToolTip(t("Andere Form aus der Galerie wählen"))

        def waehlen():
            stil = self.form_waehlen(art, self.element.stil, self)
            if stil is not None and stil != self.element.stil:
                if art == "linie":                    # Zierlinien brauchen Hoehe
                    soll = stile.LINIE_HOEHE_MM.get(stil, 1.0)
                    if self.element.hoehe_mm < soll:
                        self.element.y_mm -= (soll - self.element.hoehe_mm) / 2
                        self.element.hoehe_mm = soll
                self._setzen("stil", stil)
                self.zeige(self.element)              # Knopf mit neuer Vorschau
        knopf.clicked.connect(waehlen)
        form.addRow(t("Form"), knopf)
        self.felder["stil"] = knopf

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
        pfad, _ = QFileDialog.getOpenFileName(self, t("Bild wählen"), "",
                                              t("Bilder (*.png *.jpg *.jpeg *.bmp *.gif)"))
        if not pfad:
            return
        daten = bild_lesen(pfad, self)
        if daten is not None:
            self._setzen("daten", daten)
