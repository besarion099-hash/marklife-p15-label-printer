# -*- coding: utf-8 -*-
from kern import einstellungen as ein


def test_fehlende_datei_gibt_vorgaben(tmp_path):
    assert ein.laden(tmp_path / "gibtsnicht.json") == ein.Einstellungen()


def test_speichern_und_laden(tmp_path):
    pfad = tmp_path / "e.json"
    e = ein.Einstellungen(port="COM13", papiertyp=1, dichte=3, drehung_grad=270,
                          eigene_breite_mm=33.5)
    ein.speichern(e, pfad)
    assert ein.laden(pfad) == e


def test_falsche_typen_und_werte_werden_ignoriert(tmp_path):
    pfad = tmp_path / "e.json"
    pfad.write_text('{"port": 13, "dichte": "hoch", "papiertyp": 7, '
                    '"drehung_grad": 45, "blockgroesse": 0, '
                    '"eigene_hoehe_mm": 14, "unbekannt": 1}', encoding="utf-8")
    e = ein.laden(pfad)
    assert e.port == ""
    assert e.dichte == 2
    assert e.papiertyp == 2
    assert e.drehung_grad == 270
    assert e.blockgroesse == 512
    assert e.eigene_hoehe_mm == 14.0


def test_kaputte_datei_gibt_vorgaben(tmp_path):
    pfad = tmp_path / "e.json"
    pfad.write_text("{kein json", encoding="utf-8")
    assert ein.laden(pfad) == ein.Einstellungen()


def test_standardpfad_liegt_im_werkzeugordner():
    assert ein.STANDARD_PFAD.parent.name == "etikettendrucker"
