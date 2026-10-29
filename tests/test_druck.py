# -*- coding: utf-8 -*-
import pytest

from hilfen import FalscheVerbindung
from kern import druck
from kern.einstellungen import Einstellungen
from kern.etikett import Etikett, QRCode, Rahmen, Text

E = Einstellungen(port="COM13")          # drehung_grad 270, Papiertyp 2, Dichte 2


def _serie():
    return Etikett(30, 15, [Text(x_mm=10, inhalt="{{Name}}")])   # mittig, faellt beim Versatz nicht heraus


def test_druckbild_wird_gedreht():
    etikett = Etikett(30, 15)
    assert druck.druckbild(etikett, None, 0).size == (112, 120)   # auf Kopfbreite beschnitten
    assert druck.druckbild(etikett, None, 90).size == (112, 240)


def test_drehung_im_uhrzeigersinn():
    etikett = Etikett(2, 2, [Rahmen(x_mm=0, y_mm=0, breite_mm=1, hoehe_mm=1, strich_mm=1)])
    # 16 x 16 Punkte, mittig auf 112 aufgefuellt: Versatz 48
    bild = druck.druckbild(etikett, None, 90)
    assert bild.size == (112, 16)
    assert bild.getpixel((48 + 12, 4)) == 0  # oben links wandert nach oben rechts
    assert bild.getpixel((48 + 4, 4)) == 255
    assert bild.getpixel((0, 4)) == 255      # Auffuellung ist weiss


def test_zwoelf_mm_band_wird_mittig_aufgefuellt():
    etikett = Etikett(30, 12, [Rahmen(x_mm=0, y_mm=0, breite_mm=30, hoehe_mm=12, strich_mm=0.5)])
    bild = druck.druckbild(etikett, None, 270)
    assert bild.size == (112, 240)
    assert bild.getpixel((7, 120)) == 255 and bild.getpixel((8, 120)) == 0
    assert bild.getpixel((103, 120)) == 0 and bild.getpixel((104, 120)) == 255


def test_auftrag_fuer_etikett():
    daten = druck.auftrag_fuer(Etikett(30, 15), None, E)
    assert daten[:8] == bytes.fromhex("10FFF102 1F70010A")
    assert daten[15:23] == bytes([0x1D, 0x76, 0x30, 0x00, 14, 0, 209, 0])   # 240 - 31 Rand
    assert daten.endswith(bytes.fromhex("1D0C 1F1150 10FFF145"))


def test_serie_mit_kopien():
    verbindung = FalscheVerbindung()
    stand = []
    anzahl = druck.drucken(_serie(), [{"Name": "A"}, {"Name": "B"}, {"Name": "C"}], 2, E,
                           verbindung, lambda f, g: stand.append((f, g)))
    assert anzahl == 6
    assert verbindung.port == "COM13"
    gesendet = verbindung.gesendet
    assert len(gesendet) == 6
    assert gesendet[0] == gesendet[1] and gesendet[1] != gesendet[2]
    assert stand[-1] == (6, 6)


def test_abbrechen_nach_zwei():
    verbindung = FalscheVerbindung()
    anzahl = druck.drucken(_serie(), [{"Name": "A"}] * 5, 1, E, verbindung,
                           abbrechen=lambda: len(verbindung.gesendet) >= 2)
    assert anzahl == 2 and len(verbindung.gesendet) == 2


def test_abriss_meldet_fertige():
    with pytest.raises(druck.DruckFehler) as info:
        druck.drucken(_serie(), [{"Name": "A"}] * 3, 1, E, FalscheVerbindung(kaputt_ab=2))
    assert info.value.fertig == 2
    assert "abgerissen" in str(info.value)


def test_fehlerhaftes_element_sendet_nichts():
    verbindung = FalscheVerbindung()
    etikett = Etikett(30, 15, [QRCode(breite_mm=1, hoehe_mm=1, inhalt="viel zu lang")])
    with pytest.raises(druck.DruckFehler, match="Element 1"):
        druck.drucken(etikett, [{}], 1, E, verbindung)
    assert verbindung.gesendet == []


def test_ohne_port():
    with pytest.raises(druck.DruckFehler, match="Kein Drucker"):
        druck.drucken(_serie(), [{}], 1, Einstellungen(), FalscheVerbindung())


def test_ausrichtung_zwei_etiketten():
    verbindung = FalscheVerbindung()
    assert druck.ausrichtung_testen(E, 30, 15, verbindung) == 2
    assert verbindung.gesendet[0] != verbindung.gesendet[1]
    assert [daten[19] for daten in verbindung.gesendet] == [14, 14]   # 112 Punkte


def test_rand_am_ende_wird_abgeschnitten():
    etikett = Etikett(4, 2, [Rahmen(x_mm=0, y_mm=0, breite_mm=4, hoehe_mm=2, strich_mm=0.5)])
    bild = druck.druckbild(etikett, None, 0, rand_ende_mm=1.5)   # 12 Punkte weniger
    links = (112 - 20) // 2                                      # 32 - 12 = 20 breit, mittig
    assert bild.getpixel((links, 8)) == 0                        # linke Rahmenkante bleibt
    assert bild.getpixel((links + 19, 8)) == 255                 # rechte Kante (x 28..31) ist weg


def test_rand_bei_gedrehtem_druck():
    bild = druck.druckbild(Etikett(40, 12), None, 270, rand_ende_mm=3.9)
    assert bild.size == (112, 320 - 31)                          # 36,1 mm bedruckbar


def test_vorgabe_rand_ist_am_p15_gemessen():
    assert Einstellungen().rand_ende_mm == 3.9


def test_versatz_schiebt_inhalt_nach_rechts():
    etikett = Etikett(10, 2, [Rahmen(x_mm=0, y_mm=0, breite_mm=1, hoehe_mm=2, strich_mm=1)])
    ohne = druck.druckbild(etikett, None, 0)
    mit = druck.druckbild(etikett, None, 0, versatz_mm=2)
    assert ohne.size == mit.size
    assert ohne.getpixel((18, 8)) == 0 and mit.getpixel((18, 8)) == 255   # +16: mittig auf 112
    assert mit.getpixel((18 + 16, 8)) == 0                 # 2 mm = 16 Punkte weiter rechts
