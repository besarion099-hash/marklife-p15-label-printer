# -*- coding: utf-8 -*-
"""Das Etikett in Vergroesserung, mit verschiebbaren Rahmen darueber.

Gezeigt wird genau das Bild, das auch der Drucker bekommt
(kern.zeichnen), Punkt fuer Punkt ohne Glaettung. Die Rahmen der
Elemente liegen darueber: anklicken waehlt, ziehen verschiebt. Das
gewaehlte Element hat acht Griffe (Ecken und Seitenmitten); auch jede
Kante laesst sich direkt fassen. Alles rastet auf einen Druckpunkt
(1/8 mm) ein.
"""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from gui.bilder import zu_qimage
from kern import zeichnen
from kern.etikett import Etikett, ragt_ueber

GRIFF = 9         # Kantenlaenge eines Griffs in Bildschirmpunkten
KANTE = 4         # so nah an einer Kante des gewaehlten Elements fasst man die Kante
RAND = 20
MINDEST_MM = 1.0

# Richtung eines Griffs: (-1 links, 0 Mitte, 1 rechts), (-1 oben, 0 Mitte, 1 unten).
# Ecken zuerst, damit sie bei kleinen Elementen vor den Seiten greifen.
RICHTUNGEN = [(1, 1), (-1, -1), (1, -1), (-1, 1), (0, -1), (0, 1), (-1, 0), (1, 0)]
_C = Qt.CursorShape
ZEIGER = {(1, 1): _C.SizeFDiagCursor, (-1, -1): _C.SizeFDiagCursor,
          (1, -1): _C.SizeBDiagCursor, (-1, 1): _C.SizeBDiagCursor,
          (0, -1): _C.SizeVerCursor, (0, 1): _C.SizeVerCursor,
          (-1, 0): _C.SizeHorCursor, (1, 0): _C.SizeHorCursor}


def einrasten(mm: float) -> float:
    return round(mm * zeichnen.PUNKTE_JE_MM) / zeichnen.PUNKTE_JE_MM


def _lage(anfang, ende, seite):
    return anfang if seite < 0 else ende if seite > 0 else (anfang + ende) / 2


def achse(anfang, laenge, delta, seite):
    """Neue (anfang, laenge) auf einer Achse, wenn die Kante seite um delta
    wandert: -1 bewegt den Anfang (das Ende bleibt), 1 das Ende, 0 nichts."""
    if seite > 0:
        return anfang, max(MINDEST_MM, einrasten(laenge + delta))
    if seite < 0:
        ende = anfang + laenge
        neu = min(einrasten(anfang + delta), ende - MINDEST_MM)
        return neu, ende - neu
    return anfang, laenge


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
        self.setMouseTracking(True)        # Zeiger zeigt schon beim Darueberfahren die Richtung
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

    def griffe(self, rechteck: QRectF) -> dict:
        return {(sx, sy): QRectF(_lage(rechteck.left(), rechteck.right(), sx) - GRIFF / 2,
                                 _lage(rechteck.top(), rechteck.bottom(), sy) - GRIFF / 2,
                                 GRIFF, GRIFF)
                for sx, sy in RICHTUNGEN}

    def griff(self, rechteck: QRectF, richtung=(1, 1)) -> QRectF:
        return self.griffe(rechteck)[richtung]

    def _gewaehlt(self):
        elemente = self.etikett.elemente
        return elemente[self.auswahl] if 0 <= self.auswahl < len(elemente) else None

    def griff_an(self, pos: QPointF):
        """Richtung des Griffs oder der Kante des gewaehlten Elements unter pos, sonst None."""
        element = self._gewaehlt()
        if element is None:
            return None
        rechteck = self.rechteck(element)
        for richtung, feld in self.griffe(rechteck).items():
            if feld.contains(pos):
                return richtung
        if not rechteck.adjusted(-KANTE, -KANTE, KANTE, KANTE).contains(pos):
            return None
        sx = (-1 if abs(pos.x() - rechteck.left()) <= KANTE
              else 1 if abs(pos.x() - rechteck.right()) <= KANTE else 0)
        sy = (-1 if abs(pos.y() - rechteck.top()) <= KANTE
              else 1 if abs(pos.y() - rechteck.bottom()) <= KANTE else 0)
        return (sx, sy) if (sx, sy) != (0, 0) else None

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
            maler.setPen(QPen(farbe, 1.5))
            maler.setBrush(Qt.GlobalColor.white)
            for feld in self.griffe(rechteck).values():
                maler.drawRect(feld)

    def mousePressEvent(self, ereignis):
        if ereignis.button() != Qt.MouseButton.LeftButton:
            return
        pos = ereignis.position()
        self.setFocus()
        richtung = self.griff_an(pos)
        if richtung is not None:
            self._modus = richtung
        else:
            index = self.treffer(pos)
            self.waehle(index)
            self._modus = "ziehen" if index >= 0 else None
        if self._modus is not None:
            element = self.etikett.elemente[self.auswahl]
            self._start = pos
            self._start_werte = (element.x_mm, element.y_mm, element.breite_mm, element.hoehe_mm)

    def mouseMoveEvent(self, ereignis):
        pos = ereignis.position()
        if self._modus is None:
            self._zeiger(pos)
            return
        zoom, _, _ = self.massstab()
        dx = (pos.x() - self._start.x()) / zoom
        dy = (pos.y() - self._start.y()) / zoom
        x, y, breite, hoehe = self._start_werte
        element = self.etikett.elemente[self.auswahl]
        if self._modus == "ziehen":
            element.x_mm, element.y_mm = einrasten(x + dx), einrasten(y + dy)
        else:
            sx, sy = self._modus
            element.x_mm, element.breite_mm = achse(x, breite, dx, sx)
            element.y_mm, element.hoehe_mm = achse(y, hoehe, dy, sy)
        self.neu_zeichnen()
        self.geaendert.emit()

    def mouseReleaseEvent(self, ereignis):
        self._modus = None
        self._zeiger(ereignis.position())

    def _zeiger(self, pos):
        richtung = self.griff_an(pos)
        if richtung is not None:
            self.setCursor(ZEIGER[richtung])
        elif self.treffer(pos) >= 0:
            self.setCursor(Qt.CursorShape.SizeAllCursor)
        else:
            self.unsetCursor()

    def keyPressEvent(self, ereignis):
        if ereignis.key() == Qt.Key.Key_Delete:
            self.loeschen()
        else:
            super().keyPressEvent(ereignis)
