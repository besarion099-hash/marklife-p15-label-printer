# -*- coding: utf-8 -*-
"""Galerie der Rahmen- bzw. Linienformen: jede Form als Vorschau, ein Klick
waehlt und schliesst. Die Vorschau zeichnet kern.zeichnen, also genau das,
was auch gedruckt wird."""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QDialog, QListView, QListWidget, QListWidgetItem, QVBoxLayout

from gui.bilder import zu_qimage
from kern import stile, zeichnen
from kern.etikett import Linie, Rahmen

VORSCHAU = QSize(216, 72)


def vorschau(art, stil):
    """Vorschaubild einer Form: Rahmen 36 x 12 mm, Linie 36 mm in ihrer Einfuegehoehe."""
    if art == "rahmen":
        element = Rahmen(breite_mm=36, hoehe_mm=12, stil=stil)
    else:
        element = Linie(breite_mm=36, hoehe_mm=stile.LINIE_HOEHE_MM.get(stil, 1.0), stil=stil)
    bild = zu_qimage(zeichnen.element_bild(element))
    return bild.scaled(VORSCHAU, Qt.AspectRatioMode.KeepAspectRatio,
                       Qt.TransformationMode.SmoothTransformation)


class FormenDialog(QDialog):
    def __init__(self, art, jetzt=None, eltern=None):
        super().__init__(eltern)
        self.art = art
        self.gewaehlt = None
        formen = stile.RAHMENSTILE if art == "rahmen" else stile.LINIENSTILE
        self.setWindowTitle(f"{'Rahmen' if art == 'rahmen' else 'Linie'} wählen")
        self.resize(780, 600)
        self.raster = QListWidget()
        self.raster.setViewMode(QListView.ViewMode.IconMode)
        hoch = VORSCHAU.height() if art == "rahmen" else VORSCHAU.height() // 2
        self.raster.setIconSize(QSize(VORSCHAU.width(), hoch))
        self.raster.setGridSize(QSize(VORSCHAU.width() + 24, hoch + 40))
        self.raster.setResizeMode(QListView.ResizeMode.Adjust)
        self.raster.setMovement(QListView.Movement.Static)
        self.raster.setUniformItemSizes(True)
        self.raster.setWordWrap(True)
        for name, text in formen:
            punkt = QListWidgetItem(QIcon(QPixmap.fromImage(vorschau(art, name))), text)
            punkt.setData(Qt.ItemDataRole.UserRole, name)
            punkt.setToolTip(text)
            self.raster.addItem(punkt)
            if name == jetzt:
                self.raster.setCurrentItem(punkt)
        QVBoxLayout(self).addWidget(self.raster)
        self.raster.itemClicked.connect(self._gewaehlt)

    def _gewaehlt(self, punkt):
        self.gewaehlt = punkt.data(Qt.ItemDataRole.UserRole)
        self.accept()


def form_waehlen(art, jetzt=None, eltern=None):
    """Galerie zeigen; die gewaehlte Form oder None bei Abbruch."""
    dialog = FormenDialog(art, jetzt, eltern)
    return dialog.gewaehlt if dialog.exec() else None
