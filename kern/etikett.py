# -*- coding: utf-8 -*-
"""Das Etikett als Daten: Groesse und Elemente, dazu die Vorlagendatei.

Lage und Groesse eines Elements beschreiben die Flaeche, die es auf dem
Etikett einnimmt, nach seiner Drehung. breite_mm ist immer die Laenge
entlang des Bandes, hoehe_mm die Bandbreite.
"""

from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import ClassVar

from kern.sprache import t

FASSUNG = 1
DREHUNGEN = (0, 90, 180, 270)
GROESSEN = [
    ("22 x 12 mm", 22.0, 12.0), ("22 x 14 mm", 22.0, 14.0), ("26 x 15 mm", 26.0, 15.0),
    ("30 x 12 mm", 30.0, 12.0), ("30 x 14 mm", 30.0, 14.0), ("30 x 15 mm", 30.0, 15.0),
    ("40 x 12 mm", 40.0, 12.0), ("40 x 14 mm", 40.0, 14.0), ("40 x 15 mm", 40.0, 15.0),
    ("50 x 15 mm", 50.0, 15.0),
]


class VorlagenFehler(Exception):
    """Die Datei ist keine lesbare Vorlage."""


@dataclass
class Element:
    ART: ClassVar[str] = ""
    x_mm: float = 1.0
    y_mm: float = 1.0
    breite_mm: float = 10.0
    hoehe_mm: float = 5.0
    drehung: int = 0


@dataclass
class Text(Element):
    ART: ClassVar[str] = "text"
    inhalt: str = "Text"
    schrift: str = "Arial"
    groesse_pt: float = 10.0
    fett: bool = False
    ausrichtung: str = "links"      # links, mitte, rechts


@dataclass
class QRCode(Element):
    ART: ClassVar[str] = "qr"
    inhalt: str = "https://"


@dataclass
class Barcode(Element):
    ART: ClassVar[str] = "barcode"
    inhalt: str = "12345678"
    art: str = "code128"            # code128, ean13
    klartext: bool = True


@dataclass
class Bild(Element):
    ART: ClassVar[str] = "bild"
    daten: bytes = b""
    verfahren: str = "schwelle"     # schwelle, fehlerverteilung


@dataclass
class Rahmen(Element):
    ART: ClassVar[str] = "rahmen"
    strich_mm: float = 0.5
    ecken_mm: float = 0.0
    stil: str = "einfach"           # siehe kern.stile.RAHMENSTILE


@dataclass
class Linie(Element):
    ART: ClassVar[str] = "linie"
    strich_mm: float = 0.5
    stil: str = "durchgezogen"      # siehe kern.stile.LINIENSTILE


ARTEN = {klasse.ART: klasse for klasse in (Text, QRCode, Barcode, Bild, Rahmen, Linie)}


@dataclass
class Etikett:
    breite_mm: float = 30.0
    hoehe_mm: float = 15.0
    elemente: list = field(default_factory=list)


def ragt_ueber(etikett, element) -> bool:
    toleranz = 1e-6
    return (element.x_mm < -toleranz or element.y_mm < -toleranz
            or element.x_mm + element.breite_mm > etikett.breite_mm + toleranz
            or element.y_mm + element.hoehe_mm > etikett.hoehe_mm + toleranz)


def zu_dict(etikett) -> dict:
    elemente = []
    for element in etikett.elemente:
        eintrag = {"typ": element.ART}
        for feld in fields(element):
            wert = getattr(element, feld.name)
            if isinstance(wert, bytes):
                wert = base64.b64encode(wert).decode("ascii")
            eintrag[feld.name] = wert
        elemente.append(eintrag)
    return {"fassung": FASSUNG, "breite_mm": etikett.breite_mm,
            "hoehe_mm": etikett.hoehe_mm, "elemente": elemente}


def aus_dict(daten) -> Etikett:
    if not isinstance(daten, dict):
        raise VorlagenFehler(t("Die Datei enthält keine Vorlage."))
    fassung = daten.get("fassung")
    if not isinstance(fassung, int):
        raise VorlagenFehler(t("Der Datei fehlt die Fassungsnummer."))
    if fassung > FASSUNG:
        raise VorlagenFehler(
            t("Die Vorlage stammt aus einer neueren Fassung ({fassung}) dieses Programms.",
              fassung=fassung))
    try:
        etikett = Etikett(float(daten["breite_mm"]), float(daten["hoehe_mm"]))
        for eintrag in daten.get("elemente", []):
            etikett.elemente.append(_element(eintrag))
    except (KeyError, TypeError, ValueError) as fehler:
        raise VorlagenFehler(t("Die Vorlage ist beschädigt: {fehler}", fehler=fehler)) from fehler
    return etikett


def _element(eintrag: dict):
    klasse = ARTEN.get(eintrag.get("typ"))
    if klasse is None:
        raise VorlagenFehler(t("Unbekannte Elementart: {art}", art=repr(eintrag.get("typ"))))
    werte = {}
    for feld in fields(klasse):
        if feld.name in eintrag:
            wert = eintrag[feld.name]
            if klasse is Bild and feld.name == "daten":
                wert = base64.b64decode(wert, validate=True)
            werte[feld.name] = wert
    element = klasse(**werte)
    if element.drehung not in DREHUNGEN:
        element.drehung = 0
    return element


def speichern(etikett, pfad) -> None:
    pfad = Path(pfad)
    zwischen = pfad.with_name(pfad.name + ".tmp")
    zwischen.write_text(json.dumps(zu_dict(etikett), indent=2, ensure_ascii=False),
                        encoding="utf-8")
    os.replace(zwischen, pfad)


def laden(pfad) -> Etikett:
    try:
        daten = json.loads(Path(pfad).read_text(encoding="utf-8"))
    except (OSError, ValueError) as fehler:
        raise VorlagenFehler(t("Die Datei lässt sich nicht lesen: {fehler}", fehler=fehler)) from fehler
    return aus_dict(daten)
