# -*- coding: utf-8 -*-
import pytest
from PIL import ImageOps

from kern import etikett as et
from kern import stile, zeichnen
from kern.etikett import Etikett, Linie, Rahmen


def _bild(element):
    return zeichnen.zeichnen(Etikett(36, 12, [element])).convert("L")


def _schwarze_punkte(bild):
    return bild.histogram()[0]


@pytest.mark.parametrize("stil", [s for s, _ in stile.RAHMENSTILE])
def test_jeder_rahmenstil_zeichnet_im_feld(stil):
    bild = _bild(Rahmen(x_mm=2, y_mm=1, breite_mm=30, hoehe_mm=10, strich_mm=0.375, stil=stil))
    kasten = ImageOps.invert(bild).getbbox()
    assert kasten is not None
    assert kasten[0] >= 16 and kasten[1] >= 8 and kasten[2] <= 256 and kasten[3] <= 88


@pytest.mark.parametrize("stil", [s for s, _ in stile.LINIENSTILE])
def test_jeder_linienstil_zeichnet_im_feld(stil):
    bild = _bild(Linie(x_mm=2, y_mm=3, breite_mm=30, hoehe_mm=6, strich_mm=0.375, stil=stil))
    kasten = ImageOps.invert(bild).getbbox()
    assert kasten is not None
    assert kasten[0] >= 16 and kasten[1] >= 24 and kasten[2] <= 256 and kasten[3] <= 72


def test_keine_vollflaechen():
    # Grosse Schwarzflaechen belasten den Thermokopf: kein Rahmen fuellt mehr als 30 %.
    for stil, _ in stile.RAHMENSTILE:
        bild = _bild(Rahmen(x_mm=0, y_mm=0, breite_mm=36, hoehe_mm=12, strich_mm=0.5, stil=stil))
        assert _schwarze_punkte(bild) < 0.3 * bild.width * bild.height, stil


def test_strich_mindestens_zwei_punkte():
    # 0,125 mm waere ein einzelner Druckpunkt; gezeichnet werden mindestens 2.
    bild = _bild(Linie(x_mm=0, y_mm=0, breite_mm=10, hoehe_mm=4, strich_mm=0.125))
    spalte = [bild.getpixel((40, y)) for y in range(32)]
    assert spalte.count(0) == 2


def test_gestrichelt_hat_luecken():
    bild = _bild(Linie(x_mm=0, y_mm=0, breite_mm=30, hoehe_mm=4, strich_mm=0.25, stil="gestrichelt"))
    zeile = [bild.getpixel((x, 15)) for x in range(240)]
    wechsel = sum(1 for a, b in zip(zeile, zeile[1:]) if a != b)
    assert wechsel >= 10                              # viele Striche, nicht eine Linie
    assert zeile.count(0) < 0.8 * 240


def test_doppelter_rahmen_hat_zwei_kanten():
    bild = _bild(Rahmen(x_mm=0, y_mm=0, breite_mm=36, hoehe_mm=12, strich_mm=0.375, stil="doppelt"))
    zeile = [bild.getpixel((x, 48)) for x in range(20)]
    # aussen 3 Punkte schwarz, 3 weiss, innen 3 schwarz
    assert zeile[:9] == [0, 0, 0, 255, 255, 255, 0, 0, 0]


def test_stil_wird_gespeichert_und_alte_vorlagen_bleiben_lesbar(tmp_path):
    etikett = Etikett(40, 12, [Rahmen(stil="wellen"), Linie(stil="ornament")])
    et.speichern(etikett, tmp_path / "a.etikett.json")
    assert et.laden(tmp_path / "a.etikett.json") == etikett
    alt = et.aus_dict({"fassung": 1, "breite_mm": 40, "hoehe_mm": 12,
                       "elemente": [{"typ": "rahmen"}, {"typ": "linie"}]})
    assert alt.elemente[0].stil == "einfach" and alt.elemente[1].stil == "durchgezogen"


def test_unbekannter_stil_zeichnet_einfach():
    einfach = _bild(Rahmen(stil="einfach"))
    unbekannt = _bild(Rahmen(stil="gibtsnicht"))
    assert einfach.tobytes() == unbekannt.tobytes()


def test_je_rund_dreissig_formen_mit_eindeutigen_namen():
    for liste in (stile.RAHMENSTILE, stile.LINIENSTILE):
        namen = [name for name, _ in liste]
        assert len(namen) >= 30 and len(set(namen)) == len(namen)
    # Namen frueherer Fassungen bleiben gueltig, damit alte Vorlagen gleich aussehen
    alt_r = {"einfach", "doppelt", "dick-duenn", "gestrichelt", "gepunktet", "wellen", "ecken",
             "ticket"}
    alt_l = {"durchgezogen", "doppelt", "gestrichelt", "gepunktet", "strich-punkt", "welle",
             "zickzack", "ornament"}
    assert alt_r <= {n for n, _ in stile.RAHMENSTILE}
    assert alt_l <= {n for n, _ in stile.LINIENSTILE}


@pytest.mark.parametrize("stil", [s for s, _ in stile.LINIENSTILE])
def test_zierlinie_in_einfuegehoehe_ohne_vollflaeche(stil):
    hoehe = stile.LINIE_HOEHE_MM[stil]
    bild = _bild(Linie(x_mm=0, y_mm=0, breite_mm=36, hoehe_mm=hoehe, stil=stil))
    streifen = bild.crop((0, 0, 288, round(hoehe * 8)))
    assert 0 < _schwarze_punkte(streifen) < 0.7 * streifen.width * streifen.height, stil


@pytest.mark.parametrize("stil", [s for s, _ in stile.RAHMENSTILE])
def test_rahmen_klein_und_mit_dickem_strich_stuerzt_nicht(stil):
    for breite, hoehe, strich in ((4, 3, 0.25), (36, 12, 2.0), (1, 1, 0.5)):
        _bild(Rahmen(x_mm=0, y_mm=0, breite_mm=breite, hoehe_mm=hoehe, strich_mm=strich, stil=stil))


@pytest.mark.parametrize("stil", [s for s, _ in stile.LINIENSTILE])
def test_linie_klein_und_mit_dickem_strich_stuerzt_nicht(stil):
    for breite, hoehe, strich in ((4, 0.5, 0.25), (36, 4, 2.0), (1, 0.25, 0.5)):
        _bild(Linie(x_mm=0, y_mm=0, breite_mm=breite, hoehe_mm=hoehe, strich_mm=strich, stil=stil))
