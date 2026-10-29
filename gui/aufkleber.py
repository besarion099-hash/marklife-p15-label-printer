# -*- coding: utf-8 -*-
"""Dialog Aufkleber: links die Kategorien wie in der Marklife-App, rechts
das Raster der Grafiken, oben eine Suche. Ein Klick waehlt und schliesst.

SVG-Aufkleber (Tabler) werden hier mit Qt gerendert; kern bleibt ohne Qt.
Eingefuegt wird ein PNG in Druckaufloesung als gewoehnliches Bild-Element.
"""

from __future__ import annotations

from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QSize, Qt
from PySide6.QtGui import QIcon, QImage, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QLineEdit, QListView, QListWidget,
                               QListWidgetItem, QVBoxLayout)

from kern import aufkleber as ak
from kern.sprache import t

VORSCHAU_PX = 64


def _svg_renderer(pfad):
    # Tabler zeichnet mit "currentColor"; Qt kennt dafuer keine Farbe -> Schwarz.
    text = pfad.read_text(encoding="utf-8").replace("currentColor", "#000000")
    return QSvgRenderer(QByteArray(text.encode("utf-8")))


def als_bild(eintrag, px: int) -> QImage:
    """Aufkleber als quadratisches Bild mit durchsichtigem Hintergrund."""
    bild = QImage(px, px, QImage.Format.Format_ARGB32)
    bild.fill(Qt.GlobalColor.transparent)
    if eintrag.pfad.suffix.lower() == ".svg":
        maler = QPainter(bild)
        maler.setRenderHint(QPainter.RenderHint.Antialiasing)
        _svg_renderer(eintrag.pfad).render(maler)
        maler.end()
        return bild
    geladen = QImage(str(eintrag.pfad))
    if geladen.isNull():
        return bild
    skaliert = geladen.scaled(px, px, Qt.AspectRatioMode.KeepAspectRatio,
                              Qt.TransformationMode.SmoothTransformation)
    maler = QPainter(bild)
    maler.drawImage((px - skaliert.width()) // 2, (px - skaliert.height()) // 2, skaliert)
    maler.end()
    return bild


def als_png(eintrag, px: int = 320) -> bytes:
    """PNG-Bytes fuer das Bild-Element (320 Punkte = 40 mm bei 203 dpi reichen)."""
    puffer = QBuffer()
    puffer.open(QIODevice.OpenModeFlag.WriteOnly)
    als_bild(eintrag, px).save(puffer, "PNG")
    return bytes(puffer.data())


class AufkleberDialog(QDialog):
    def __init__(self, katalog: dict, eltern=None):
        super().__init__(eltern)
        self.setWindowTitle(t("Aufkleber"))
        self.resize(820, 560)
        self.katalog = katalog
        self.gewaehlt = None
        self._symbole = {}

        self.suche = QLineEdit()
        self.suche.setPlaceholderText(t("Suchen (englische Stichwörter, z. B. heart, flower, cake) …"))
        self.kategorien = QListWidget()
        self.kategorien.setFixedWidth(220)
        for name in katalog:                  # Name zur Anzeige uebersetzt, Schluessel bleibt
            punkt = QListWidgetItem(t(name))
            punkt.setData(Qt.ItemDataRole.UserRole, name)
            self.kategorien.addItem(punkt)
        self.raster = QListWidget()
        self.raster.setViewMode(QListView.ViewMode.IconMode)
        self.raster.setIconSize(QSize(VORSCHAU_PX, VORSCHAU_PX))
        self.raster.setGridSize(QSize(VORSCHAU_PX + 24, VORSCHAU_PX + 24))
        self.raster.setResizeMode(QListView.ResizeMode.Adjust)
        self.raster.setMovement(QListView.Movement.Static)
        self.raster.setUniformItemSizes(True)
        self.hinweis = QLabel()

        mitte = QHBoxLayout()
        mitte.addWidget(self.kategorien)
        mitte.addWidget(self.raster, 1)
        aussen = QVBoxLayout(self)
        aussen.addWidget(self.suche)
        aussen.addLayout(mitte, 1)
        aussen.addWidget(self.hinweis)

        self.kategorien.currentItemChanged.connect(
            lambda punkt, *_: self._zeige_kategorie(self._schluessel(punkt)))
        self.suche.textChanged.connect(self._suchen)
        self.raster.itemClicked.connect(self._gewaehlt)
        if katalog:
            self.kategorien.setCurrentRow(0)
        else:
            self.hinweis.setText(t("Keine Aufkleber gefunden. install.bat lädt die freie Sammlung; "
                                   "eigene Grafiken in den Ordner aufkleber\\eigene legen."))

    def _symbol(self, eintrag) -> QIcon:
        if eintrag.pfad not in self._symbole:
            self._symbole[eintrag.pfad] = QIcon(QPixmap.fromImage(als_bild(eintrag, VORSCHAU_PX)))
        return self._symbole[eintrag.pfad]

    def zeige(self, liste):
        self.raster.clear()
        for eintrag in liste:
            punkt = QListWidgetItem(self._symbol(eintrag), "")
            punkt.setToolTip(eintrag.name)
            punkt.setData(Qt.ItemDataRole.UserRole, eintrag)
            self.raster.addItem(punkt)
        self.hinweis.setText(t("{anzahl} Aufkleber", anzahl=len(liste)))

    def _zeige_kategorie(self, name):
        if name and not self.suche.text().strip():
            self.zeige(self.katalog.get(name, []))

    def _suchen(self, text):
        if text.strip():
            self.zeige(ak.suchen(self.katalog, text))
        else:
            self._zeige_kategorie(self._schluessel(self.kategorien.currentItem()))

    @staticmethod
    def _schluessel(punkt):
        return punkt.data(Qt.ItemDataRole.UserRole) if punkt is not None else ""

    def _gewaehlt(self, punkt):
        self.gewaehlt = punkt.data(Qt.ItemDataRole.UserRole)
        self.accept()
