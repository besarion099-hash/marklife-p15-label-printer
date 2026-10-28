# -*- coding: utf-8 -*-
"""Dialog Serien-Druck: Tabelle waehlen, Vorschau je Zeile, Bereich drucken."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import (QAbstractItemView, QDialog, QFileDialog, QGridLayout, QHBoxLayout,
                               QLabel, QMessageBox, QProgressBar, QPushButton, QSpinBox,
                               QTableWidget, QTableWidgetItem, QVBoxLayout)

from gui.arbeiter import im_hintergrund
from gui.bilder import startordner, zu_qimage
from kern import anschluss, druck, platzhalter, serie, zeichnen


class SerienDialog(QDialog):
    def __init__(self, etikett, einstellungen, eltern=None, verbinden=anschluss.Verbindung):
        super().__init__(eltern)
        self.setWindowTitle("Serien-Druck")
        self.resize(920, 540)
        self.etikett = etikett
        self.einstellungen = einstellungen
        self._verbinden = verbinden
        self.tabelle = None
        self._faden = self._arbeiter = None
        self._kopien = 1
        self._von_start = 1
        self.melden = lambda titel, text: QMessageBox.warning(self, titel, text)

        waehlen = QPushButton("Tabelle wählen …")
        self.datei = QLabel("Noch keine Datei gewählt (CSV oder Excel).")
        self.ansicht = QTableWidget()
        self.ansicht.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.ansicht.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.vorschau = QLabel()
        self.vorschau.setMinimumSize(280, 140)
        self.vorschau.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hinweis = QLabel()
        self.hinweis.setStyleSheet("color: #c00000")
        self.hinweis.setWordWrap(True)
        self.von, self.bis, self.kopien = QSpinBox(), QSpinBox(), QSpinBox()
        for feld in (self.von, self.bis):
            feld.setEnabled(False)            # erst nach dem Laden einer Tabelle
        self.kopien.setRange(1, 99)
        self.balken = QProgressBar()
        self.drucken_knopf = QPushButton("Drucken")
        self.drucken_knopf.setEnabled(False)
        self.abbrechen_knopf = QPushButton("Abbrechen")
        self.abbrechen_knopf.setEnabled(False)
        schliessen = QPushButton("Schließen")

        oben = QHBoxLayout()
        oben.addWidget(waehlen)
        oben.addWidget(self.datei, 1)
        mitte = QHBoxLayout()
        mitte.addWidget(self.ansicht, 2)
        rechts = QVBoxLayout()
        rechts.addWidget(self.vorschau)
        rechts.addWidget(self.hinweis)
        rechts.addStretch(1)
        mitte.addLayout(rechts, 1)
        unten = QGridLayout()
        for spalte, (text, feld) in enumerate((("Zeilen von", self.von), ("bis", self.bis),
                                                ("Kopien je Zeile", self.kopien))):
            unten.addWidget(QLabel(text), 0, 2 * spalte)
            unten.addWidget(feld, 0, 2 * spalte + 1)
        unten.addWidget(self.balken, 1, 0, 1, 6)
        knoepfe = QHBoxLayout()
        knoepfe.addStretch(1)
        for knopf in (self.drucken_knopf, self.abbrechen_knopf, schliessen):
            knoepfe.addWidget(knopf)
        aussen = QVBoxLayout(self)
        for teil in (oben, mitte, unten, knoepfe):
            aussen.addLayout(teil)

        waehlen.clicked.connect(self._waehlen)
        self.ansicht.currentCellChanged.connect(lambda zeile, *_: self._vorschau(zeile))
        self.drucken_knopf.clicked.connect(self.starte_druck)
        self.abbrechen_knopf.clicked.connect(self._abbrechen)
        schliessen.clicked.connect(self.reject)

    def _waehlen(self):
        pfad, _ = QFileDialog.getOpenFileName(self, "Tabelle wählen",
                                              startordner(self.einstellungen),
                                              "Tabellen (*.csv *.xlsx)")
        if pfad:
            self.einstellungen.letzter_ordner = str(Path(pfad).parent)
            self.lade(pfad)

    def lade(self, pfad) -> bool:
        try:
            tabelle = serie.lesen(pfad)
        except serie.TabellenFehler as fehler:
            self.melden("Serien-Druck", str(fehler))
            return False
        self.tabelle = tabelle
        self.datei.setText(Path(pfad).name)
        fehlend = platzhalter.fehlende(self.etikett, tabelle.spalten)
        self.ansicht.clear()
        self.ansicht.setColumnCount(len(tabelle.spalten))
        self.ansicht.setHorizontalHeaderLabels(tabelle.spalten)
        self.ansicht.setRowCount(len(tabelle.zeilen))
        for zeile, werte in enumerate(tabelle.zeilen):
            for spalte, name in enumerate(tabelle.spalten):
                eintrag = QTableWidgetItem(werte[name])
                if fehlend:
                    eintrag.setBackground(QColor("#ffd0d0"))
                self.ansicht.setItem(zeile, spalte, eintrag)
        self.hinweis.setText(
            "Diese Platzhalter haben keine Spalte: "
            + ", ".join("{{%s}}" % name for name in fehlend) if fehlend else "")
        anzahl = len(tabelle.zeilen)
        for feld in (self.von, self.bis):
            feld.setRange(1, max(1, anzahl))
            feld.setEnabled(anzahl > 0)
        self.von.setValue(1)
        self.bis.setValue(max(1, anzahl))
        self.drucken_knopf.setEnabled(anzahl > 0 and bool(self.einstellungen.port))
        if anzahl:
            self.ansicht.selectRow(0)
            self._vorschau(0)
        return True

    def _vorschau(self, zeile):
        if self.tabelle is None or not 0 <= zeile < len(self.tabelle.zeilen):
            return
        qbild = zu_qimage(zeichnen.zeichnen(self.etikett, self.tabelle.zeilen[zeile]))
        faktor = max(1, min(3, 280 // max(1, qbild.width())))
        self.vorschau.setPixmap(QPixmap.fromImage(qbild.scaled(
            qbild.width() * faktor, qbild.height() * faktor,
            Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.FastTransformation)))

    def starte_druck(self):
        if self.tabelle is None or (self._faden is not None and self._faden.isRunning()):
            return
        zeilen = self.tabelle.zeilen[self.von.value() - 1:self.bis.value()]
        if not zeilen:
            return
        self._kopien = self.kopien.value()
        self._von_start = self.von.value()
        etikett, einstellungen, kopien = self.etikett, self.einstellungen, self._kopien
        verbinden = self._verbinden

        def aufgabe(fortschritt, abbrechen):
            return druck.drucken(etikett, zeilen, kopien, einstellungen, verbinden,
                                 fortschritt, abbrechen)

        self.balken.setRange(0, len(zeilen) * kopien)
        self.balken.setValue(0)
        self._knoepfe(druckt=True)
        self._faden, self._arbeiter = im_hintergrund(
            aufgabe, self, fortschritt=lambda fertig, gesamt: self.balken.setValue(fertig),
            fertig=self._fertig, fehler=self._fehler)

    def _knoepfe(self, druckt):
        self.drucken_knopf.setEnabled(not druckt)
        self.abbrechen_knopf.setEnabled(druckt)

    def _fertig(self, anzahl):
        self._knoepfe(druckt=False)
        self.balken.setValue(anzahl)

    def _fehler(self, meldung, fertig):
        self._knoepfe(druckt=False)
        weiter = self._von_start + fertig // self._kopien
        if weiter <= self.bis.value():
            self.von.setValue(weiter)
        self.melden("Serien-Druck",
                    f"{meldung}\n\n{fertig} Etikett(en) sind fertig. „Zeilen von“ steht jetzt "
                    f"auf {self.von.value()}, damit es dort weitergeht.")

    def _abbrechen(self):
        if self._arbeiter is not None:
            self._arbeiter.abbrechen()

    def reject(self):
        if self._faden is not None and self._faden.isRunning():
            self._arbeiter.abbrechen()
            self._faden.wait(15000)
        super().reject()
