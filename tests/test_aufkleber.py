# -*- coding: utf-8 -*-
import json
from io import BytesIO

from PIL import Image

from kern import aufkleber as ak

HERZ = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2"><path d="M4 4h16v16H4z"/></svg>')


def _sammlung(tmp_path, eintraege):
    tabler = tmp_path / "tabler"
    (tabler / "outline").mkdir(parents=True)
    daten = {}
    for name, kategorie, tags in eintraege:
        (tabler / "outline" / f"{name}.svg").write_text(HERZ, encoding="utf-8")
        daten[name] = {"name": name, "category": kategorie, "tags": tags,
                       "styles": {"outline": {}}}
    (tabler / "icons.json").write_text(json.dumps(daten), encoding="utf-8")
    return tmp_path


def test_kategorien_wie_in_der_app(tmp_path):
    wurzel = _sammlung(tmp_path, [
        ("crown", "Design", ["king"]), ("crown-off", "Design", []),
        ("basket-heart", "E-commerce", []), ("cloud-rain", "Weather", ["rain"]),
        ("cloud-rain-off", "Weather", []), ("shoe", "Sport", [])])
    katalog = ak.katalog(wurzel)
    namen = {k: [a.name for a in v] for k, v in katalog.items()}
    assert namen["Schmuck"] == ["crown"]                     # -off faellt weg
    assert namen["Wetter"] == ["cloud-rain"]
    assert "basket-heart" not in namen.get("Blumenladen-Geschenk", [])
    assert namen["Schuh"] == ["shoe"]
    reihenfolge = [k for k, _, _ in ak.KATEGORIEN if k in katalog]
    assert list(katalog)[:len(reihenfolge)] == reihenfolge    # Reihenfolge der App


def test_marklife_und_eigene_ordner(tmp_path):
    (tmp_path / "marklife").mkdir()
    Image.new("L", (4, 4)).save(tmp_path / "marklife" / "type1-1.png")
    (tmp_path / "eigene" / "Gewürze").mkdir(parents=True)
    Image.new("L", (4, 4)).save(tmp_path / "eigene" / "logo.png")
    Image.new("L", (4, 4)).save(tmp_path / "eigene" / "Gewürze" / "chili.png")
    katalog = ak.katalog(tmp_path)
    assert [a.name for a in katalog["Marklife"]] == ["type1-1"]
    assert [a.name for a in katalog["Meine Aufkleber"]] == ["logo"]
    assert [a.name for a in katalog["Meine Aufkleber: Gewürze"]] == ["chili"]


def test_suche_ueber_stichworte_ohne_doppelte(tmp_path):
    wurzel = _sammlung(tmp_path, [("crown", "Design", ["king", "queen"]),
                                  ("cloud-rain", "Weather", ["rain"])])
    katalog = ak.katalog(wurzel)
    assert [a.name for a in ak.suchen(katalog, "queen")] == ["crown"]
    assert len(ak.suchen(katalog, "")) == 2


def test_ohne_sammlung_leer(tmp_path):
    assert ak.katalog(tmp_path) == {}


def test_svg_wird_schwarz_gerendert(qapp, tmp_path):
    from gui.aufkleber import als_png
    wurzel = _sammlung(tmp_path, [("crown", "Design", [])])
    eintrag = ak.katalog(wurzel)["Schmuck"][0]
    bild = Image.open(BytesIO(als_png(eintrag, 96))).convert("RGBA")
    assert bild.size == (96, 96)
    punkte = (bild.getpixel((x, y)) for x in range(96) for y in range(96))
    deckend = [p for p in punkte if p[3] > 200]
    assert deckend and all(p[0] < 60 for p in deckend)      # currentColor -> schwarz


def test_dialog_zeigt_kategorie_und_waehlt(qapp, tmp_path):
    from gui.aufkleber import AufkleberDialog
    wurzel = _sammlung(tmp_path, [("crown", "Design", ["king"]), ("diamond", "Design", [])])
    dialog = AufkleberDialog(ak.katalog(wurzel))
    assert dialog.kategorien.currentItem().text() == "Schmuck"
    assert dialog.raster.count() == 2
    dialog.suche.setText("king")
    assert dialog.raster.count() == 1
    dialog._gewaehlt(dialog.raster.item(0))
    assert dialog.gewaehlt.name == "crown"
