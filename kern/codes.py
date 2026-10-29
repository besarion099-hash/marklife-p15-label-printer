# -*- coding: utf-8 -*-
"""QR-Codes und Barcodes als Bild, Punkt fuer Punkt gezeichnet.

Bewusst ohne die Bild-Ausgabe der Bibliotheken: Ein Modul muss eine
ganze Zahl von Druckpunkten breit sein, sonst verschwimmen die Kanten
und Scanner scheitern.
"""

from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont

from kern.sprache import t


class CodeFehler(Exception):
    """Der Inhalt passt nicht in den Code oder der Code nicht ins Feld."""


def ean_pruefziffer(zwoelf: str) -> str:
    summe = sum(int(z) * (1 if i % 2 == 0 else 3) for i, z in enumerate(zwoelf))
    return str((10 - summe % 10) % 10)


def qr_bild(inhalt: str, kante_px: int) -> Image.Image:
    import qrcode
    from qrcode.exceptions import DataOverflowError
    if not inhalt:
        raise CodeFehler(t("Der QR-Code ist leer."))
    qr = qrcode.QRCode(border=0, error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(inhalt)
    try:
        qr.make(fit=True)
    except (DataOverflowError, ValueError) as fehler:   # qrcode 8.2: ValueError "Invalid version"
        raise CodeFehler(t("Der Text ist zu lang für einen QR-Code.")) from fehler
    matrix = qr.get_matrix()
    anzahl = len(matrix)
    modul = kante_px // anzahl
    if modul < 1:
        raise CodeFehler(t("Der QR-Code braucht mindestens {anzahl} Punkte, das Feld hat "
                           "{feld}. Feld größer machen oder Text kürzen.",
                           anzahl=anzahl, feld=kante_px))
    bild = Image.new("L", (kante_px, kante_px), 255)
    zeichner = ImageDraw.Draw(bild)
    rand = (kante_px - anzahl * modul) // 2
    for zeile, reihe in enumerate(matrix):
        for spalte, schwarz in enumerate(reihe):
            if schwarz:
                x, y = rand + spalte * modul, rand + zeile * modul
                zeichner.rectangle([x, y, x + modul - 1, y + modul - 1], fill=0)
    return bild


def barcode_module(inhalt: str, art: str) -> str:
    import barcode
    from barcode.errors import BarcodeError
    try:
        if art == "ean13":
            ziffern = inhalt.strip()
            if not (ziffern.isascii() and ziffern.isdigit()) or len(ziffern) not in (12, 13):
                raise CodeFehler(t("Ein EAN-13 braucht 12 oder 13 Ziffern."))
            richtig = ean_pruefziffer(ziffern[:12])
            if len(ziffern) == 13 and ziffern[12] != richtig:
                raise CodeFehler(t("Die Prüfziffer stimmt nicht, richtig wäre {richtig}.",
                                   richtig=richtig))
            code = barcode.EAN13(ziffern[:12])
        elif art == "code128":
            if not inhalt:
                raise CodeFehler(t("Der Barcode ist leer."))
            code = barcode.Code128(inhalt)
        else:
            raise CodeFehler(t("Unbekannte Barcode-Art: {art}", art=art))
        return "".join(code.build())
    except (BarcodeError, ValueError, KeyError) as fehler:
        raise CodeFehler(t("Der Inhalt lässt sich nicht als Barcode darstellen: {fehler}",
                            fehler=fehler)) from fehler


def barcode_bild(inhalt: str, art: str, breite_px: int, hoehe_px: int,
                 klartext: bool) -> Image.Image:
    module = barcode_module(inhalt, art)
    modul = breite_px // len(module)
    if modul < 1:
        raise CodeFehler(t("Der Barcode braucht mindestens {anzahl} Punkte Breite, "
                           "das Feld hat {feld}.", anzahl=len(module), feld=breite_px))
    text_hoehe = hoehe_px // 4 if klartext else 0
    balken_hoehe = hoehe_px - text_hoehe
    if balken_hoehe < 4:
        raise CodeFehler(t("Das Feld ist zu niedrig für einen Barcode."))
    bild = Image.new("L", (breite_px, hoehe_px), 255)
    zeichner = ImageDraw.Draw(bild)
    links = (breite_px - modul * len(module)) // 2
    for i, bit in enumerate(module):
        if bit == "1":
            x = links + i * modul
            zeichner.rectangle([x, 0, x + modul - 1, balken_hoehe - 1], fill=0)
    if klartext and text_hoehe >= 6:
        zeichner.text((breite_px // 2, hoehe_px), inhalt, font=_schrift(text_hoehe),
                      fill=0, anchor="md")
    return bild


def _schrift(px: int):
    try:
        return ImageFont.truetype("arial.ttf", px)
    except OSError:
        return ImageFont.load_default(px)
