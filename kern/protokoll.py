# -*- coding: utf-8 -*-
"""Druckauftrag fuer den Marklife P15 als Bytes.

Der Ablauf stammt aus einem Mitschnitt des Windows-Treibers (P15UNI.DLL,
am 28.10.2026 per Datei-Port aufgezeichnet) und ist am Geraet bestaetigt:
damit gedruckte Etiketten kamen lesbar heraus. Die Klasse P15Protocol der
Android-App sendet einen anderen Ablauf (1F 70 02 d, 15 Nullbytes, Bild
120 Punkte breit); der kam am P15 nicht an.

Annahmen, noch nicht am Geraet geprueft: die Dichte-Werte ausser 0x0A
und der Nachschub fuer Endlospapier und schwarze Marke.
"""

from __future__ import annotations

from kern.sprache import t

KOPF_PUNKTE = 112                    # Breite des Druckkopfs (14 mm bei 203 dpi)
DICHTE_BYTE = {1: 0x06, 2: 0x0A, 3: 0x0E}   # 0x0A sendet der Treiber als Vorgabe
NACHSCHUB = {
    1: bytes([0x1B, 0x4A, 0x64]),   # Endlospapier: 100 Punkte vor (ESC J)
    2: bytes([0x1D, 0x0C]),         # Etikett mit Luecke: zum naechsten Etikett
    3: b"",                         # schwarze Marke: nichts
}
DRUCKER_AN = bytes([0x10, 0xFF, 0xF1, 0x02])
ENDE = bytes([0x10, 0xFF, 0xF1, 0x45])


def raster(bild) -> bytes:
    """Zeilenweise 1 Bit je Punkt, hoechstes Bit links, 1 = schwarz.

    Was dunkler als 128 ist, wird schwarz. Die Fuellbits am Ende jeder
    Zeile bleiben 0, sonst druckt der Kopf dort einen Streifen.
    """
    schwarz = bild.convert("L").point(lambda v: 255 if v < 128 else 0, mode="1")
    return schwarz.tobytes()


def bildbefehl(bild) -> bytes:
    breite, hoehe = bild.size
    if breite < 1 or hoehe < 1:
        raise ValueError(t("Das Bild ist leer."))
    zeilenbytes = (breite + 7) // 8
    if zeilenbytes > 0xFFFF or hoehe > 0xFFFF:
        raise ValueError(t("Das Bild ist zu groß für den Drucker."))
    kopf = bytes([0x1D, 0x76, 0x30, 0x00,
                  zeilenbytes & 0xFF, zeilenbytes >> 8,
                  hoehe & 0xFF, hoehe >> 8])
    return kopf + raster(bild)


def auftrag(bild, papiertyp: int, dichte: int) -> bytes:
    if papiertyp not in NACHSCHUB:
        raise ValueError(t("Unbekannter Papiertyp: {wert}", wert=papiertyp))
    if dichte not in DICHTE_BYTE:
        raise ValueError(t("Unbekannte Dichte: {wert}", wert=dichte))
    # Der Treiber springt auch VOR dem Bild mit 1D 0C zum naechsten Etikett.
    # Am Geraet kostete das ein leeres Etikett je Druck; deshalb nur danach.
    return b"".join([
        DRUCKER_AN,
        bytes([0x1F, 0x70, 0x01, DICHTE_BYTE[dichte]]),
        bytes([0x1F, 0x11, 0x51]),
        bytes([0x1F, 0xC0, 0x01, 0x00]),
        bildbefehl(bild),
        bytes([0x0D, 0x0A]),
        bytes([0x1F, 0xC0, 0x01, 0x01]),
        NACHSCHUB[papiertyp],
        bytes([0x1F, 0x11, 0x50]),
        ENDE,
    ])
