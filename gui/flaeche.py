# -*- coding: utf-8 -*-
"""Das Etikett in Vergroesserung, mit verschiebbaren Rahmen darueber.

Gezeigt wird genau das Bild, das auch der Drucker bekommt
(kern.zeichnen), Punkt fuer Punkt ohne Glaettung. Die Rahmen der
Elemente liegen darueber: anklicken waehlt, ziehen verschiebt, das
Quadrat unten rechts aendert die Groesse. Alles rastet auf einen
Druckpunkt (1/8 mm) ein.
"""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from gui.bilder import zu_qimage
from kern import zeichnen
from kern.etikett import Etikett, ragt_ueber

GRIFF = 10        # Kantenlaenge des Griffs in Bildschirmpunkten
RAND = 20


def einrasten(mm: float) -> float:
    return round(mm * zeichnen.PUNKTE_JE_MM) / zeichnen.PUNKTE_JE_MM


class Flaeche(QWidget):
    auswahl_geaendert = Signal(int)
    geaendert = Signal()

    def __init__(self, eltern=None):
        super().__init__(eltern)
        self.etikett = Etikett()
        self.auswahl = -1
        self.fehler = {}
        self.rand_ende_mm = 0.0       # nicht bedruckbarer Streifen am Etikettende
        self._bild = None
        self._modus = None
        self._start = QPointF()
        self._start_werte = (0.0, 0.0, 0.0, 0.0)
        self.setMinimumSize(400, 200)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.neu_zeichnen()

    def setze_etikett(self, etikett):
        self.etikett = etikett
        self.auswahl = -1
        self.neu_zeichnen()
        self.auswahl_geaendert.emit(-1)

    def neu_zeichnen(self):
        fehler = []
        bild = zeichnen.zeichnen(self.etikett, None, fehler)
        self.fehler = dict(fehler)
        self._bild = zu_qimage(bild)
        self.update()

    def massstab(self):
        breite, hoehe = self.etikett.breite_mm, self.etikett.hoehe_mm
        zoom = max(1.0, min((self.width() - 2 * RAND) / breite,
                            (self.height() - 2 * RAND) / hoehe))
        return zoom, (self.width() - breite * zoom) / 2, (self.height() - hoehe * zoom) / 2

    def rechteck(self, element) -> QRectF:
        zoom, links, oben = self.massstab()
        return QRectF(links + element.x_mm * zoom, oben + element.y_mm * zoom,
                      element.breite_mm * zoom, element.hoehe_mm * zoom)

    def griff(self, rechteck: QRectF) -> QRectF:
        return QRectF(rechteck.right() - GRIFF / 2, rechteck.bottom() - GRIFF / 2, GRIFF, GRIFF)

    def treffer(self, pos: QPointF) -> int:
        for index in range(len(self.etikett.elemente) - 1, -1, -1):
            if self.rechteck(self.etikett.elemente[index]).contains(pos):
                return index
        return -1

    def waehle(self, index: int):
        if index != self.auswahl:
            self.auswahl = index
            self.update()
            self.auswahl_geaendert.emit(index)

    def loeschen(self):
        if 0 <= self.auswahl < len(self.etikett.elemente):
            del self.etikett.elemente[self.auswahl]
            self.auswahl = -1
            self.neu_zeichnen()
            self.auswahl_geaendert.emit(-1)
            self.geaendert.emit()

    def paintEvent(self, ereignis):
        maler = QPainter(self)
        maler.fillRect(self.rect(), QColor("#c8c8c8"))
        zoom, links, oben = self.massstab()
        ziel = QRectF(links, oben, self.etikett.breite_mm * zoom, self.etikett.hoehe_mm * zoom)
        maler.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
        maler.drawImage(ziel, self._bild)
        if self.rand_ende_mm > 0:
            streifen = QRectF(ziel.right() - self.rand_ende_mm * zoom, ziel.top(),
                              self.rand_ende_mm * zoom, ziel.height())
            maler.fillRect(streifen, QBrush(QColor(120, 120, 120, 110), Qt.BrushStyle.BDiagPattern))
        for index, element in enumerate(self.etikett.elemente):
            self._rahmen_malen(maler, index, element)
        maler.end()

    def ausserhalb(self, element) -> bool:
        """Ragt ueber das Etikett oder in den nicht bedruckbaren Streifen am Ende."""
        bedruckbar = Etikett(self.etikett.breite_mm - self.rand_ende_mm, self.etikett.hoehe_mm)
        return ragt_ueber(bedruckbar, element)

    def _rahmen_malen(self, maler, index, element):
        gewaehlt = index == self.auswahl
        if index in self.fehler:
            farbe = QColor("#d00000")
        elif self.ausserhalb(element):
            farbe = QColor("#ff8c00")
        else:
            farbe = QColor("#0060ff")
            if not gewaehlt:
                farbe.setAlpha(110)
        stift = QPen(farbe, 2 if gewaehlt else 1)
        stift.setStyle(Qt.PenStyle.SolidLine if gewaehlt else Qt.PenStyle.DashLine)
        maler.setPen(stift)
        maler.setBrush(Qt.BrushStyle.NoBrush)
        rechteck = self.rechteck(element)
        maler.drawRect(rechteck)
        if gewaehlt:
            maler.fillRect(self.griff(rechteck), farbe)

    def mousePressEvent(self, ereignis):
        if ereignis.button() != Qt.MouseButton.LeftButton:
            return
        pos = ereignis.position()
        self.setFocus()
        gewaehlt = (self.etikett.elemente[self.auswahl]
                    if 0 <= self.auswahl < len(self.etikett.elemente) else None)
        if gewaehlt is not None and self.griff(self.rechteck(gewaehlt)).contains(pos):
            self._modus = "groesse"
        else:
            index = self.treffer(pos)
            self.waehle(index)
            self._modus = "ziehen" if index >= 0 else None
        if self._modus is not None:
            element = self.etikett.elemente[self.auswahl]
            self._start = pos
            self._start_werte = (element.x_mm, element.y_mm, element.breite_mm, element.hoehe_mm)

    def mouseMoveEvent(self, ereignis):
        if self._modus is None:
            return
        zoom, _, _ = self.massstab()
        pos = ereignis.position()
        dx = (pos.x() - self._start.x()) / zoom
        dy = (pos.y() - self._start.y()) / zoom
        x, y, breite, hoehe = self._start_werte
        element = self.etikett.elemente[self.auswahl]
        if self._modus == "ziehen":
            element.x_mm, element.y_mm = einrasten(x + dx), einrasten(y + dy)
        else:
            element.breite_mm = max(1.0, einrasten(breite + dx))
            element.hoehe_mm = max(1.0, einrasten(hoehe + dy))
        self.neu_zeichnen()
        self.geaendert.emit()

    def mouseReleaseEvent(self, ereignis):
        self._modus = None

    def keyPressEvent(self, ereignis):
        if ereignis.key() == Qt.Key.Key_Delete:
            self.loeschen()
        else:
            super().keyPressEvent(ereignis)
