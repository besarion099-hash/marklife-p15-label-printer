# -*- coding: utf-8 -*-
"""Etikett -> Bild in Druckerauflösung (203 dpi, 8 Punkte je mm).

Dasselbe Bild zeigt das Fenster und bekommt der Drucker. Jedes Element
wird fuer sich auf Weiss gezeichnet und dann mit "dunkler gewinnt"
aufgelegt; so loescht kein Element ein anderes, das unter ihm liegt.
"""

from __future__ import annotations

import functools
import io

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps

from kern import codes, platzhalter, stile
from kern.etikett import Barcode, Bild, Linie, QRCode, Rahmen, Text

PUNKTE_JE_MM = 8
SCHRIFTEN = {
    "Arial": ("arial.ttf", "arialbd.ttf"),
    "Segoe UI": ("segoeui.ttf", "segoeuib.ttf"),
    "Consolas": ("consola.ttf", "consolab.ttf"),
    "Times New Roman": ("times.ttf", "timesbd.ttf"),
}
_IM_UHRZEIGERSINN = {90: Image.Transpose.ROTATE_270, 180: Image.Transpose.ROTATE_180,
                     270: Image.Transpose.ROTATE_90}
_AUSRICHTUNG = {"links": "left", "mitte": "center", "rechts": "right"}


def punkte(mm: float) -> int:
    return max(0, round(mm * PUNKTE_JE_MM))


def zeichnen(etikett, werte=None, fehler=None) -> Image.Image:
    """Das ganze Etikett als Bild im Modus "1".

    werte ersetzt Platzhalter {{Spalte}}. Elemente, die sich nicht zeichnen
    lassen, bleiben leer; ist fehler eine Liste, kommt (Index, Meldung) hinein.
    """
    groesse = (max(1, punkte(etikett.breite_mm)), max(1, punkte(etikett.hoehe_mm)))
    leinwand = Image.new("L", groesse, 255)
    for index, element in enumerate(etikett.elemente):
        try:
            teil = element_bild(element, werte)
        except (codes.CodeFehler, OSError, ValueError) as grund:
            if fehler is not None:
                fehler.append((index, str(grund)))
            continue
        if teil is None:
            continue
        lage = Image.new("L", groesse, 255)
        lage.paste(teil, (round(element.x_mm * PUNKTE_JE_MM), round(element.y_mm * PUNKTE_JE_MM)))
        leinwand = ImageChops.darker(leinwand, lage)
    return leinwand.point(lambda v: 0 if v < 128 else 255, mode="1")


def element_bild(element, werte=None):
    breite, hoehe = punkte(element.breite_mm), punkte(element.hoehe_mm)
    if breite < 1 or hoehe < 1:
        return None
    quer = element.drehung in (90, 270)
    innen_b, innen_h = (hoehe, breite) if quer else (breite, hoehe)
    bild = _inhalt(element, innen_b, innen_h, werte)
    if bild is None:
        return None
    if element.drehung in _IM_UHRZEIGERSINN:
        bild = bild.transpose(_IM_UHRZEIGERSINN[element.drehung])
    return bild


def _inhalt(element, breite, hoehe, werte):
    if isinstance(element, Text):
        return _text(element, breite, hoehe, platzhalter.ersetzen(element.inhalt, werte))
    if isinstance(element, QRCode):
        kante = min(breite, hoehe)
        flaeche = Image.new("L", (breite, hoehe), 255)
        qr = codes.qr_bild(platzhalter.ersetzen(element.inhalt, werte), kante)
        flaeche.paste(qr, ((breite - kante) // 2, (hoehe - kante) // 2))
        return flaeche
    if isinstance(element, Barcode):
        return codes.barcode_bild(platzhalter.ersetzen(element.inhalt, werte), element.art,
                                  breite, hoehe, element.klartext)
    if isinstance(element, Bild):
        return _bild(element, breite, hoehe)
    if isinstance(element, Rahmen):
        flaeche = Image.new("L", (breite, hoehe), 255)
        stile.rahmen(ImageDraw.Draw(flaeche), breite, hoehe, punkte(element.strich_mm),
                     punkte(element.ecken_mm), element.stil)
        return flaeche
    if isinstance(element, Linie):
        flaeche = Image.new("L", (breite, hoehe), 255)
        stile.linie(ImageDraw.Draw(flaeche), breite, hoehe, punkte(element.strich_mm), element.stil)
        return flaeche
    return None


@functools.lru_cache(maxsize=256)
def schrift(name: str, fett: bool, px: int):
    normal, dick = SCHRIFTEN.get(name, SCHRIFTEN["Arial"])
    for datei in ((dick, normal) if fett else (normal,)):
        try:
            return ImageFont.truetype(datei, px)
        except OSError:
            continue
    return ImageFont.load_default(px)


def _text(element, breite, hoehe, inhalt):
    flaeche = Image.new("L", (breite, hoehe), 255)
    if not inhalt.strip():
        return flaeche
    zeichner = ImageDraw.Draw(flaeche)
    ausrichtung = _AUSRICHTUNG.get(element.ausrichtung, "left")
    # Die eingestellte Groesse ist ein Hoechstwert: Passt der Text nicht ins
    # Feld, wird er verkleinert, statt still Buchstaben abzuschneiden (beim
    # Serien-Druck mit langen Werten sonst leicht zu uebersehen).
    def masse(px):
        font = schrift(element.schrift, element.fett, px)
        kasten = zeichner.multiline_textbbox((0, 0), inhalt, font=font, align=ausrichtung)
        return font, kasten

    def passt(kasten):
        return kasten[2] - kasten[0] <= breite and kasten[3] - kasten[1] <= hoehe

    groesste = max(4, round(element.groesse_pt * 203 / 72))
    font, kasten = masse(groesste)
    if not passt(kasten):
        klein, gross = 4, groesste             # binaere Suche: groesste passende Groesse
        while gross - klein > 1:
            mitte = (klein + gross) // 2
            if passt(masse(mitte)[1]):
                klein = mitte
            else:
                gross = mitte
        font, kasten = masse(klein)
    links, oben, rechts, unten = kasten
    text_b, text_h = rechts - links, unten - oben
    x ={"left": 0, "center": (breite - text_b) // 2, "right": breite - text_b}[ausrichtung]
    y = (hoehe - text_h) // 2
    zeichner.multiline_text((x - links, y - oben), inhalt, font=font, fill=0, align=ausrichtung)
    return flaeche


def _bild(element, breite, hoehe):
    flaeche = Image.new("L", (breite, hoehe), 255)
    if not element.daten:
        return flaeche
    with Image.open(io.BytesIO(element.daten)) as roh:
        farbig = roh.convert("RGBA")
    weiss = Image.new("RGBA", farbig.size, (255, 255, 255, 255))
    weiss.alpha_composite(farbig)
    grau = ImageOps.contain(weiss.convert("L"), (breite, hoehe), Image.Resampling.LANCZOS)
    if element.verfahren == "fehlerverteilung":
        grau = grau.convert("1").convert("L")        # Floyd-Steinberg
    else:
        grau = grau.point(lambda v: 0 if v < 128 else 255)
    flaeche.paste(grau, ((breite - grau.width) // 2, (hoehe - grau.height) // 2))
    return flaeche
