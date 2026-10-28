# -*- coding: utf-8 -*-
import json

import pytest

from kern import etikett as et

PNG = b"\x89PNG\r\n\x1a\n" + bytes(range(256))


def _alle():
    return et.Etikett(40, 12, [
        et.Text(x_mm=1, y_mm=1, breite_mm=20, hoehe_mm=5, inhalt="Hallo\n{{Name}}",
                schrift="Consolas", groesse_pt=9.5, fett=True, ausrichtung="mitte"),
        et.QRCode(x_mm=25, inhalt="https://example.org", drehung=90),
        et.Barcode(inhalt="4006381333931", art="ean13", klartext=False),
        et.Bild(daten=PNG, verfahren="fehlerverteilung"),
        et.Rahmen(strich_mm=0.25, ecken_mm=1.0),
        et.Linie(strich_mm=0.375, drehung=270),
    ])


def test_speichern_und_laden_bitgenau(tmp_path):
    pfad = tmp_path / "a.etikett.json"
    et.speichern(_alle(), pfad)
    geladen = et.laden(pfad)
    assert geladen == _alle()
    assert geladen.elemente[3].daten == PNG


def test_datei_ist_lesbares_json_mit_fassung(tmp_path):
    pfad = tmp_path / "a.etikett.json"
    et.speichern(_alle(), pfad)
    daten = json.loads(pfad.read_text(encoding="utf-8"))
    assert daten["fassung"] == 1
    assert [e["art"] for e in daten["elemente"]] == ["text", "qr", "barcode", "bild", "rahmen", "linie"]


def test_neuere_fassung_wird_abgelehnt():
    with pytest.raises(et.VorlagenFehler, match="neueren Fassung"):
        et.aus_dict({"fassung": 2, "breite_mm": 30, "hoehe_mm": 15, "elemente": []})


def test_unbekannte_art():
    with pytest.raises(et.VorlagenFehler, match="Elementart"):
        et.aus_dict({"fassung": 1, "breite_mm": 30, "hoehe_mm": 15,
                     "elemente": [{"art": "kreis"}]})


def test_kaputtes_bild():
    with pytest.raises(et.VorlagenFehler):
        et.aus_dict({"fassung": 1, "breite_mm": 30, "hoehe_mm": 15,
                     "elemente": [{"art": "bild", "daten": "%%%"}]})


def test_keine_datei(tmp_path):
    with pytest.raises(et.VorlagenFehler):
        et.laden(tmp_path / "fehlt.etikett.json")


def test_unerlaubte_drehung_wird_null():
    geladen = et.aus_dict({"fassung": 1, "breite_mm": 30, "hoehe_mm": 15,
                           "elemente": [{"art": "linie", "drehung": 45}]})
    assert geladen.elemente[0].drehung == 0


def test_ragt_ueber():
    etikett = et.Etikett(30, 15)
    assert not et.ragt_ueber(etikett, et.Rahmen(x_mm=0, y_mm=0, breite_mm=30, hoehe_mm=15))
    assert et.ragt_ueber(etikett, et.Rahmen(x_mm=0.5, y_mm=0, breite_mm=30, hoehe_mm=15))
    assert et.ragt_ueber(etikett, et.Rahmen(x_mm=-0.1, y_mm=0, breite_mm=5, hoehe_mm=5))


def test_groessen_aus_dem_treiber():
    assert len(et.GROESSEN) == 10
    assert et.GROESSEN[0] == ("22 x 12 mm", 22.0, 12.0)
    assert et.GROESSEN[-1] == ("50 x 15 mm", 50.0, 15.0)
