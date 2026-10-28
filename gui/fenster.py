# -*- coding: utf-8 -*-
"""Hauptfenster: Druckerleiste oben, Werkzeuge links, Etikett Mitte, Eigenschaften rechts."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QFileDialog, QInputDialog, QMainWindow, QMessageBox, QScrollArea,
                               QSplitter, QToolBar, QVBoxLayout, QWidget)

from gui.arbeiter import im_hintergrund
from gui.bilder import bild_lesen, startordner
from gui.druckleiste import Druckleiste
from gui.eigenschaften import Eigenschaften
from gui.flaeche import Flaeche
from gui.seriendruck import SerienDialog
from kern import anschluss, druck, einstellungen
from kern import etikett as et

FILTER = "Etikett-Vorlagen (*.etikett.json)"
BILDER = "Bilder (*.png *.jpg *.jpeg *.bmp *.gif)"
WERKZEUGE = [("text", "Text"), ("qr", "QR-Code"), ("barcode", "Barcode"), ("bild", "Bild …"),
             ("rahmen", "Rahmen"), ("linie", "Linie")]


class Hauptfenster(QMainWindow):
    def __init__(self, einstellungen_pfad=einstellungen.STANDARD_PFAD,
                 port_quelle=anschluss.ports, verbinden=anschluss.Verbindung):
        super().__init__()
        self._e_pfad = Path(einstellungen_pfad)
        self.e = einstellungen.laden(self._e_pfad)
        self._verbinden = verbinden
        self.pfad = None
        self._faden = self._arbeiter = None
        self.melden = lambda titel, text: QMessageBox.warning(self, titel, text)
        self.leiste = Druckleiste(self.e, port_quelle)
        self.flaeche = Flaeche()
        self.flaeche.rand_ende_mm = self.e.rand_ende_mm
        self.eigenschaften = Eigenschaften()
        self._aufbauen()
        self._menue()
        breite, hoehe = self.leiste.groesse_mm()
        self.flaeche.setze_etikett(et.Etikett(breite, hoehe))
        self._titel()
        self.resize(1150, 560)

    @property
    def etikett(self):
        return self.flaeche.etikett

    def _aufbauen(self):
        werkzeuge = QToolBar("Werkzeuge")
        werkzeuge.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        for art, text in WERKZEUGE:
            aktion = QAction(text, self)
            aktion.triggered.connect(lambda *_, a=art: self.neues_element(a))
            werkzeuge.addAction(aktion)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, werkzeuge)
        rechts = QScrollArea()
        rechts.setWidget(self.eigenschaften)
        rechts.setWidgetResizable(True)
        rechts.setMinimumWidth(300)
        teiler = QSplitter()
        teiler.addWidget(self.flaeche)
        teiler.addWidget(rechts)
        teiler.setStretchFactor(0, 1)
        mitte = QWidget()
        spalte = QVBoxLayout(mitte)
        spalte.setContentsMargins(0, 0, 0, 0)
        spalte.addWidget(self.leiste)
        spalte.addWidget(teiler, 1)
        self.setCentralWidget(mitte)
        self.statusBar()
        self.flaeche.auswahl_geaendert.connect(self._auswahl)
        self.flaeche.geaendert.connect(self.eigenschaften.aktualisieren)
        self.eigenschaften.geaendert.connect(self.flaeche.neu_zeichnen)
        self.eigenschaften.loeschen_gewuenscht.connect(self.flaeche.loeschen)
        self.leiste.geaendert.connect(self._leiste_geaendert)
        self.leiste.drucken.connect(self.drucken)

    def _menue(self):
        datei = self.menuBar().addMenu("&Datei")
        self._eintrag(datei, "&Neu", self.neu, QKeySequence.StandardKey.New)
        self._eintrag(datei, "Ö&ffnen …", self.oeffnen, QKeySequence.StandardKey.Open)
        self._eintrag(datei, "&Speichern", self.speichern, QKeySequence.StandardKey.Save)
        self._eintrag(datei, "Speichern &unter …", self.speichern_unter,
                      QKeySequence.StandardKey.SaveAs)
        datei.addSeparator()
        self._eintrag(datei, "Se&rien-Druck …", self.serien_druck)
        datei.addSeparator()
        self._eintrag(datei, "&Beenden", self.close)
        drucker = self.menuBar().addMenu("D&rucker")
        self._eintrag(drucker, "&Ausrichtung testen …", self.ausrichtung_testen)
        self._eintrag(drucker, "Drucker &neu suchen", self.leiste.ports_neu)

    def _eintrag(self, menue, text, funktion, kurz=None):
        aktion = QAction(text, self)
        if kurz is not None:
            aktion.setShortcut(QKeySequence(kurz))
        aktion.triggered.connect(lambda *_: funktion())
        menue.addAction(aktion)

    def _auswahl(self, index):
        elemente = self.etikett.elemente
        self.eigenschaften.zeige(elemente[index] if 0 <= index < len(elemente) else None)

    def _leiste_geaendert(self):
        breite, hoehe = self.leiste.groesse_mm()
        if (breite, hoehe) != (self.etikett.breite_mm, self.etikett.hoehe_mm):
            self.etikett.breite_mm, self.etikett.hoehe_mm = breite, hoehe
            self.flaeche.neu_zeichnen()
        self._einstellungen_sichern()

    def neues_element(self, art):
        b = self.etikett.breite_mm - self.e.rand_ende_mm      # nur der bedruckbare Teil
        h = self.etikett.hoehe_mm
        if art == "text":
            element = et.Text(x_mm=1, y_mm=1, breite_mm=b - 2, hoehe_mm=h - 2)
        elif art == "qr":
            element = et.QRCode(x_mm=b - (h - 2) - 1, y_mm=1, breite_mm=h - 2, hoehe_mm=h - 2)   # rechts, neben Text
        elif art == "barcode":
            element = et.Barcode(x_mm=1, y_mm=1, breite_mm=b - 2, hoehe_mm=h - 2)
        elif art == "bild":
            pfad, _ = QFileDialog.getOpenFileName(self, "Bild wählen", startordner(self.e), BILDER)
            daten = bild_lesen(pfad, self) if pfad else None
            if daten is None:
                return
            self.e.letzter_ordner = str(Path(pfad).parent)
            element = et.Bild(x_mm=1, y_mm=1, breite_mm=h - 2, hoehe_mm=h - 2, daten=daten)
        elif art == "rahmen":
            element = et.Rahmen(x_mm=0, y_mm=0, breite_mm=b, hoehe_mm=h)
        else:
            element = et.Linie(x_mm=1, y_mm=h / 2 - 0.5, breite_mm=b - 2, hoehe_mm=1)
        self.etikett.elemente.append(element)
        self.flaeche.neu_zeichnen()
        self.flaeche.waehle(len(self.etikett.elemente) - 1)

    def neu(self):
        if self.etikett.elemente and QMessageBox.question(
                self, "Neu", "Das aktuelle Etikett verwerfen?") != QMessageBox.StandardButton.Yes:
            return
        self.flaeche.setze_etikett(et.Etikett(*self.leiste.groesse_mm()))
        self.pfad = None
        self._titel()

    def oeffnen(self):
        pfad, _ = QFileDialog.getOpenFileName(self, "Vorlage öffnen", startordner(self.e), FILTER)
        if pfad:
            self.oeffnen_pfad(Path(pfad))

    def oeffnen_pfad(self, pfad):
        try:
            etikett = et.laden(pfad)
        except et.VorlagenFehler as fehler:
            self.melden("Vorlage öffnen", str(fehler))
            return
        self.leiste.setze_groesse(etikett.breite_mm, etikett.hoehe_mm)
        self.flaeche.setze_etikett(etikett)
        self.pfad = Path(pfad)
        self.e.letzter_ordner = str(self.pfad.parent)
        self._titel()

    def speichern(self):
        if self.pfad is None:
            self.speichern_unter()
        else:
            self.speichern_pfad(self.pfad)

    def speichern_unter(self):
        pfad, _ = QFileDialog.getSaveFileName(self, "Vorlage speichern", startordner(self.e), FILTER)
        if not pfad:
            return
        if not pfad.endswith(".etikett.json"):
            pfad = pfad.removesuffix(".json") + ".etikett.json"
        self.speichern_pfad(Path(pfad))

    def speichern_pfad(self, pfad):
        try:
            et.speichern(self.etikett, pfad)
        except OSError as fehler:
            self.melden("Vorlage speichern", f"Speichern ging nicht:\n{fehler}")
            return
        self.pfad = Path(pfad)
        self.e.letzter_ordner = str(self.pfad.parent)
        self._titel()

    def _titel(self):
        name = self.pfad.name if self.pfad else "neues Etikett"
        self.setWindowTitle(f"Etikettendrucker – {name}")

    def drucken(self):
        self.leiste.uebernehmen()
        self._einstellungen_sichern()
        etikett, e, kopien, verbinden = self.etikett, self.e, self.leiste.kopien.value(), self._verbinden
        self._im_hintergrund(
            lambda fort, ab: druck.drucken(etikett, [{}], kopien, e, verbinden, fort, ab), "Drucke")

    def ausrichtung_testen(self):
        if QMessageBox.question(
                self, "Ausrichtung testen",
                "Es werden vier Etiketten gedruckt, je eines mit 0°, 90°, 180° und 270° "
                "Drehung. Danach fragt das Programm, welches den Pfeil nach oben zeigt "
                "und lesbar ist.\n\nWeiter?") != QMessageBox.StandardButton.Yes:
            return
        self.leiste.uebernehmen()
        breite, hoehe = self.leiste.groesse_mm()
        e, verbinden = self.e, self._verbinden
        self._im_hintergrund(
            lambda fort, ab: druck.ausrichtung_testen(e, breite, hoehe, verbinden, fort, ab),
            "Testdruck", danach=self._ausrichtung_waehlen)

    def _ausrichtung_waehlen(self):
        moeglich = [f"{grad}°" for grad in druck.TESTDREHUNGEN]
        jetzt = moeglich.index(f"{self.e.drehung_grad}°")
        wahl, ok = QInputDialog.getItem(self, "Ausrichtung",
                                        "Welches Etikett zeigt den Pfeil nach oben?",
                                        moeglich, jetzt, False)
        if ok:
            self.e.drehung_grad = int(wahl.rstrip("°"))
            self._einstellungen_sichern()
            self.statusBar().showMessage(f"Drehung {wahl} gespeichert.", 8000)

    def _im_hintergrund(self, aufgabe, was, danach=None):
        if self._faden is not None and self._faden.isRunning():
            return
        self.leiste.setze_druckt(True)
        self.statusBar().showMessage(f"{was} …")

        def fertig(anzahl):
            self.leiste.setze_druckt(False)
            self.statusBar().showMessage(f"{anzahl} Etikett(en) gesendet.", 8000)
            if danach is not None:
                danach()

        def fehler(meldung, anzahl):
            self.leiste.setze_druckt(False)
            self.statusBar().clearMessage()
            self.melden("Drucken", f"{meldung}\n\n{anzahl} Etikett(en) waren schon gesendet.")

        self._faden, self._arbeiter = im_hintergrund(
            aufgabe, self,
            fortschritt=lambda a, g: self.statusBar().showMessage(f"{was}: {a} von {g}"),
            fertig=fertig, fehler=fehler)

    def serien_druck(self):
        self.leiste.uebernehmen()
        SerienDialog(self.etikett, self.e, self, self._verbinden).exec()
        self._einstellungen_sichern()

    def _einstellungen_sichern(self):
        try:
            einstellungen.speichern(self.e, self._e_pfad)
        except OSError:
            pass                 # Einstellungen sind Komfort; Drucken geht auch ohne

    def closeEvent(self, ereignis):
        self.leiste.uebernehmen()
        self._einstellungen_sichern()
        if self._faden is not None and self._faden.isRunning():
            self._arbeiter.abbrechen()
            self._faden.wait(15000)
        super().closeEvent(ereignis)
