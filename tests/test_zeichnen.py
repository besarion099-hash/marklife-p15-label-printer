# -*- coding: utf-8 -*-
from io import BytesIO

from PIL import Image, ImageOps

from kern import zeichnen
from kern.etikett import Bild, Etikett, Linie, QRCode, Rahmen, Text


def _schwarz(bild, xy):
    return bild.getpixel(xy) == 0


def test_groesse_in_punkten():
    assert zeichnen.zeichnen(Etikett(40, 12)).size == (320, 96)


def test_leeres_etikett_ist_weiss():
    bild = zeichnen.zeichnen(Etikett(40, 12))
    assert bild.mode == "1"
    assert bild.getextrema() == (255, 255)


def test_rahmen_halber_mm_ist_vier_punkte():
    bild = zeichnen.zeichnen(Etikett(40, 12, [
        Rahmen(x_mm=0, y_mm=0, breite_mm=40, hoehe_mm=12, strich_mm=0.5)]))
    assert all(_schwarz(bild, (x, 48)) for x in range(4))
    assert not _schwarz(bild, (4, 48))


def test_text_bleibt_in_seinem_feld():
    bild = zeichnen.zeichnen(Etikett(40, 12, [
        Text(x_mm=10, y_mm=2, breite_mm=20, hoehe_mm=8, inhalt="HALLO", groesse_pt=12)]))
    kasten = ImageOps.invert(bild.convert("L")).getbbox()
    assert kasten is not None
    assert kasten[0] >= 80 and kasten[2] <= 240 and kasten[1] >= 16 and kasten[3] <= 80


def test_rahmen_ueber_text_loescht_ihn_nicht():
    text = Text(x_mm=2, y_mm=2, breite_mm=36, hoehe_mm=8, inhalt="HALLO", groesse_pt=12)
    nur_text = zeichnen.zeichnen(Etikett(40, 12, [text]))
    beides = zeichnen.zeichnen(Etikett(40, 12, [
        text, Rahmen(x_mm=0, y_mm=0, breite_mm=40, hoehe_mm=12, strich_mm=0.5)]))
    innen = (8, 8, 312, 88)
    assert nur_text.crop(innen).tobytes() == beides.crop(innen).tobytes()


def test_platzhalter_wird_ersetzt():
    mit = zeichnen.zeichnen(Etikett(40, 12, [Text(inhalt="{{Name}}", breite_mm=38, hoehe_mm=10)]),
                            {"Name": "Anna"})
    direkt = zeichnen.zeichnen(Etikett(40, 12, [Text(inhalt="Anna", breite_mm=38, hoehe_mm=10)]))
    assert mit.tobytes() == direkt.tobytes()


def test_gedrehte_linie_steht_senkrecht():
    # Feld 16 x 96 Punkte bei x = 80; innen 96 x 16, Linie 4 Punkte in Zeile 6..9,
    # 90 Grad im Uhrzeigersinn -> Spalten 6..9, also x 86..89.
    bild = zeichnen.zeichnen(Etikett(40, 12, [
        Linie(x_mm=10, y_mm=0, breite_mm=2, hoehe_mm=12, strich_mm=0.5, drehung=90)]))
    assert all(_schwarz(bild, (x, 50)) for x in range(86, 90))
    assert not _schwarz(bild, (85, 50)) and not _schwarz(bild, (90, 50))


def test_kaputter_qr_wird_gemeldet_und_bleibt_leer():
    fehler = []
    bild = zeichnen.zeichnen(Etikett(40, 12, [
        QRCode(breite_mm=1, hoehe_mm=1, inhalt="viel zu lang für acht Punkte")]), fehler=fehler)
    assert len(fehler) == 1 and fehler[0][0] == 0
    assert bild.getextrema() == (255, 255)


def test_bild_mit_transparenz():
    quelle = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    for x in range(5):
        for y in range(10):
            quelle.putpixel((x, y), (0, 0, 0, 255))
    puffer = BytesIO()
    quelle.save(puffer, "PNG")
    bild = zeichnen.zeichnen(Etikett(40, 12, [
        Bild(x_mm=0, y_mm=0, breite_mm=1.25, hoehe_mm=1.25, daten=puffer.getvalue())]))
    assert _schwarz(bild, (2, 5))
    assert not _schwarz(bild, (7, 5))


def test_element_links_ausserhalb_wird_beschnitten():
    bild = zeichnen.zeichnen(Etikett(40, 12, [
        Rahmen(x_mm=-1, y_mm=0, breite_mm=5, hoehe_mm=12, strich_mm=0.5)]))
    assert not _schwarz(bild, (0, 48))        # linke Kante liegt bei x = -8
    assert _schwarz(bild, (28, 48))           # rechte Kante bei x = 28..31
