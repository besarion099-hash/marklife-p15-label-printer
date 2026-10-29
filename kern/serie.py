# -*- coding: utf-8 -*-
"""Tabellen fuer den Serien-Druck lesen: CSV und XLSX.

Die erste Zeile enthaelt die Spaltennamen. Alles wird zu Text, so wie es
in der Tabelle zu sehen ist: 42 statt 42.0, ein Datum als TT.MM.JJJJ.
"""

from __future__ import annotations

import csv
import datetime
import io
from dataclasses import dataclass
from pathlib import Path

from kern.sprache import t


class TabellenFehler(Exception):
    """Die Datei laesst sich nicht als Tabelle lesen."""


@dataclass
class Tabelle:
    spalten: list
    zeilen: list        # je Zeile ein dict Spaltenname -> Text


def lesen(pfad) -> Tabelle:
    pfad = Path(pfad)
    endung = pfad.suffix.lower()
    try:
        if endung == ".csv":
            zeilen = _csv(pfad)
        elif endung == ".xlsx":
            zeilen = _xlsx(pfad)
        else:
            raise TabellenFehler(
                t("Dateien vom Typ {endung} kann der Serien-Druck nicht lesen. "
                  "Bitte CSV oder Excel (.xlsx) nehmen.", endung=endung or t("(ohne Endung)")))
    except OSError as fehler:
        raise TabellenFehler(t("Die Datei lässt sich nicht öffnen: {fehler}", fehler=fehler)) from fehler
    return _tabelle(zeilen)


def _csv(pfad: Path) -> list:
    roh = pfad.read_bytes()
    try:
        text = roh.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = roh.decode("cp1252", errors="replace")
    erste = text.splitlines()[0] if text.strip() else ""
    trenner = ";" if erste.count(";") > erste.count(",") else ","
    return list(csv.reader(io.StringIO(text), delimiter=trenner))


def _xlsx(pfad: Path) -> list:
    import openpyxl
    try:
        mappe = openpyxl.load_workbook(pfad, read_only=True, data_only=True)
    except OSError:
        raise
    except Exception as fehler:     # openpyxl wirft je nach Schaden verschiedene Typen
        raise TabellenFehler(t("Die Excel-Datei lässt sich nicht lesen: {fehler}",
                               fehler=fehler)) from fehler
    try:
        blatt = mappe.worksheets[0]
        return [[_zelle(wert) for wert in zeile] for zeile in blatt.iter_rows(values_only=True)]
    finally:
        mappe.close()


def _zelle(wert) -> str:
    if wert is None:
        return ""
    if isinstance(wert, bool):
        return t("ja") if wert else t("nein")
    if isinstance(wert, float) and wert.is_integer():
        return str(int(wert))
    if isinstance(wert, (datetime.datetime, datetime.date)):
        return wert.strftime("%d.%m.%Y")
    return str(wert)


def _tabelle(zeilen: list) -> Tabelle:
    zeilen = [zeile for zeile in zeilen if any(str(zelle).strip() for zelle in zeile)]
    if not zeilen:
        raise TabellenFehler(t("Die Datei enthält keine Zeilen."))
    spalten = [str(name).strip() or t("Spalte {nr}", nr=i + 1) for i, name in enumerate(zeilen[0])]
    daten = [{name: (zeile[i] if i < len(zeile) else "") for i, name in enumerate(spalten)}
             for zeile in zeilen[1:]]
    return Tabelle(spalten, daten)
