# -*- coding: utf-8 -*-
import datetime

import pytest

from kern import platzhalter, serie
from kern.etikett import Barcode, Etikett, Rahmen, Text


def test_namen():
    assert platzhalter.namen("{{ Name }} wohnt in {{Ort}}") == ["Name", "Ort"]
    assert platzhalter.namen("keine") == []


def test_ersetzen_laesst_unbekannte_stehen():
    assert platzhalter.ersetzen("{{Name}} / {{Fehlt}}", {"Name": "Anna"}) == "Anna / {{Fehlt}}"
    assert platzhalter.ersetzen("{{Name}}", None) == "{{Name}}"


def test_fehlende():
    etikett = Etikett(30, 15, [Text(inhalt="{{Name}}"), Barcode(inhalt="{{Nummer}}"), Rahmen()])
    assert platzhalter.fehlende(etikett, ["Name"]) == ["Nummer"]
    assert platzhalter.fehlende(etikett, ["Name", "Nummer"]) == []


def test_csv_semikolon_windows1252(tmp_path):
    pfad = tmp_path / "a.csv"
    pfad.write_bytes("Name;Ort\nJürgen;Köln\nAnna;Bonn\n".encode("cp1252"))
    tabelle = serie.lesen(pfad)
    assert tabelle.spalten == ["Name", "Ort"]
    assert tabelle.zeilen == [{"Name": "Jürgen", "Ort": "Köln"}, {"Name": "Anna", "Ort": "Bonn"}]


def test_csv_komma_utf8_mit_bom_und_kurzer_zeile(tmp_path):
    pfad = tmp_path / "a.csv"
    pfad.write_text("Artikel,Preis\nSchraube,0.10\nMutter\n\n", encoding="utf-8-sig")
    tabelle = serie.lesen(pfad)
    assert tabelle.spalten == ["Artikel", "Preis"]
    assert tabelle.zeilen == [{"Artikel": "Schraube", "Preis": "0.10"},
                              {"Artikel": "Mutter", "Preis": ""}]


def test_xlsx_zahlen_und_datum(tmp_path):
    import openpyxl
    mappe = openpyxl.Workbook()
    blatt = mappe.active
    blatt.append(["Artikel", "Preis", "Menge", "Datum"])
    blatt.append(["Schraube", 3.5, 42, datetime.date(2026, 10, 28)])
    mappe.save(tmp_path / "t.xlsx")
    tabelle = serie.lesen(tmp_path / "t.xlsx")
    assert tabelle.zeilen == [{"Artikel": "Schraube", "Preis": "3.5", "Menge": "42",
                               "Datum": "28.10.2026"}]


def test_leere_datei(tmp_path):
    pfad = tmp_path / "leer.csv"
    pfad.write_text("", encoding="utf-8")
    with pytest.raises(serie.TabellenFehler, match="keine Zeilen"):
        serie.lesen(pfad)


def test_falsche_endung(tmp_path):
    pfad = tmp_path / "a.txt"
    pfad.write_text("x", encoding="utf-8")
    with pytest.raises(serie.TabellenFehler):
        serie.lesen(pfad)
