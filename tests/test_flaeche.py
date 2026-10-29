# -*- coding: utf-8 -*-
import pytest
from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent

from kern.etikett import Etikett, QRCode, Rahmen


def _maus(art, pos):
    links = Qt.MouseButton.LeftButton
    if art == QEvent.Type.MouseButtonPress:
        knopf, knoepfe = links, links
    elif art == QEvent.Type.MouseMove:
        knopf, knoepfe = Qt.MouseButton.NoButton, links
    else:
        knopf, knoepfe = links, Qt.MouseButton.NoButton
    return QMouseEvent(art, pos, pos, knopf, knoepfe, Qt.KeyboardModifier.NoModifier)


def _flaeche(*elemente):
    from gui.flaeche import Flaeche
    flaeche = Flaeche()
    flaeche.resize(600, 300)
    flaeche.setze_etikett(Etikett(40, 12, list(elemente)))
    return flaeche


def _ziehen(flaeche, von, nach):
    flaeche.mousePressEvent(_maus(QEvent.Type.MouseButtonPress, von))
    flaeche.mouseMoveEvent(_maus(QEvent.Type.MouseMove, nach))
    flaeche.mouseReleaseEvent(_maus(QEvent.Type.MouseButtonRelease, nach))


def test_ziehen_verschiebt_um_millimeter(qapp):
    flaeche = _flaeche(Rahmen(x_mm=5, y_mm=2, breite_mm=10, hoehe_mm=6))
    zoom, _, _ = flaeche.massstab()
    mitte = flaeche.rechteck(flaeche.etikett.elemente[0]).center()
    _ziehen(flaeche, mitte, mitte + QPointF(5 * zoom, 0))
    element = flaeche.etikett.elemente[0]
    assert flaeche.auswahl == 0
    assert (element.x_mm, element.y_mm) == (10.0, 2.0)


def test_griff_aendert_groesse(qapp):
    flaeche = _flaeche(Rahmen(x_mm=5, y_mm=2, breite_mm=10, hoehe_mm=6))
    flaeche.waehle(0)
    zoom, _, _ = flaeche.massstab()
    ecke = flaeche.griff(flaeche.rechteck(flaeche.etikett.elemente[0])).center()
    _ziehen(flaeche, ecke, ecke + QPointF(2 * zoom, 1 * zoom))
    element = flaeche.etikett.elemente[0]
    assert (element.breite_mm, element.hoehe_mm) == (12.0, 7.0)


def test_klick_ins_leere_hebt_auswahl_auf(qapp):
    flaeche = _flaeche(Rahmen(x_mm=5, y_mm=2, breite_mm=10, hoehe_mm=6))
    flaeche.waehle(0)
    gemeldet = []
    flaeche.auswahl_geaendert.connect(gemeldet.append)
    flaeche.mousePressEvent(_maus(QEvent.Type.MouseButtonPress, QPointF(2, 2)))
    assert flaeche.auswahl == -1 and gemeldet == [-1]


def test_loeschen(qapp):
    flaeche = _flaeche(Rahmen(), Rahmen(x_mm=20))
    flaeche.waehle(1)
    flaeche.loeschen()
    assert len(flaeche.etikett.elemente) == 1 and flaeche.auswahl == -1


def test_fehler_werden_gemerkt(qapp):
    flaeche = _flaeche(QRCode(breite_mm=1, hoehe_mm=1, inhalt="viel zu lang"))
    assert 0 in flaeche.fehler


def test_einrasten():
    from gui.flaeche import einrasten
    assert einrasten(1.06) == 1.0 and einrasten(1.07) == 1.125


def test_rand_am_ende_gilt_als_ausserhalb(qapp):
    flaeche = _flaeche(Rahmen(x_mm=0, y_mm=0, breite_mm=36, hoehe_mm=12),
                       Rahmen(x_mm=0, y_mm=0, breite_mm=38, hoehe_mm=12))
    flaeche.rand_ende_mm = 3.9                 # Etikett 40 mm, bedruckbar 36,1
    assert not flaeche.ausserhalb(flaeche.etikett.elemente[0])
    assert flaeche.ausserhalb(flaeche.etikett.elemente[1])


def _griff_ziehen(richtung, dx_mm, dy_mm):
    flaeche = _flaeche(Rahmen(x_mm=5, y_mm=2, breite_mm=10, hoehe_mm=6))
    flaeche.waehle(0)
    zoom, _, _ = flaeche.massstab()
    punkt = flaeche.griff(flaeche.rechteck(flaeche.etikett.elemente[0]), richtung).center()
    _ziehen(flaeche, punkt, punkt + QPointF(dx_mm * zoom, dy_mm * zoom))
    e = flaeche.etikett.elemente[0]
    return e.x_mm, e.y_mm, e.breite_mm, e.hoehe_mm


@pytest.mark.parametrize("richtung, dx, dy, erwartet", [
    ((-1, -1), 1, 1, (6.0, 3.0, 9.0, 5.0)),      # oben links: Ecke unten rechts bleibt
    ((1, -1), 2, -1, (5.0, 1.0, 12.0, 7.0)),     # oben rechts
    ((-1, 1), -2, 1, (3.0, 2.0, 12.0, 7.0)),     # unten links
    ((1, 1), 2, 1, (5.0, 2.0, 12.0, 7.0)),       # unten rechts
    ((-1, 0), -1, 3, (4.0, 2.0, 11.0, 6.0)),     # linke Seite: nur waagerecht
    ((1, 0), 3, 3, (5.0, 2.0, 13.0, 6.0)),       # rechte Seite
    ((0, -1), 3, -1, (5.0, 1.0, 10.0, 7.0)),     # obere Seite: nur senkrecht
    ((0, 1), 3, 2, (5.0, 2.0, 10.0, 8.0)),       # untere Seite
])
def test_griffe_ziehen_in_ihre_richtung(qapp, richtung, dx, dy, erwartet):
    assert _griff_ziehen(richtung, dx, dy) == erwartet


def test_linker_griff_haelt_mindestgroesse_und_rechte_kante(qapp):
    x, y, breite, hoehe = _griff_ziehen((-1, -1), 30, 30)
    assert (breite, hoehe) == (1.0, 1.0)
    assert (x + breite, y + hoehe) == (15.0, 8.0)


def test_kante_zwischen_den_griffen_greift(qapp):
    flaeche = _flaeche(Rahmen(x_mm=5, y_mm=2, breite_mm=10, hoehe_mm=6))
    flaeche.waehle(0)
    zoom, _, _ = flaeche.massstab()
    r = flaeche.rechteck(flaeche.etikett.elemente[0])
    links = QPointF(r.left() + 1, r.top() + r.height() / 4)
    assert flaeche.griff_an(links) == (-1, 0)
    assert flaeche.griff_an(r.center()) is None            # Mitte verschiebt
    _ziehen(flaeche, links, links + QPointF(-2 * zoom, 0))
    e = flaeche.etikett.elemente[0]
    assert (e.x_mm, e.breite_mm) == (3.0, 12.0)
