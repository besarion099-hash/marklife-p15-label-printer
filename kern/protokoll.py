# -*- coding: utf-8 -*-
"""Druckauftrag fuer den Marklife P15 als Bytes.

Gelesen aus der Marklife-App V3.9.1 (Paket com.feioou.deliprint.yxq):
P15Protocol.getData baut den Auftrag, die Bausteine kommen aus
BaseProtocol (jeweils der Zweig fuer getProtocol() == 6), das Raster aus
Printer_ESC.printBitmap. Einzelheiten im Entwurf
docs/superpowers/specs/2026-10-28-etikettendrucker-p15-design.md
"""

from __future__ import annotations

DICHTE_BYTE = {1: 0x02, 2: 0x06, 3: 0x0A}
NACHSCHUB = {
    1: bytes([0x1B, 0x4A, 0x64]),   # Endlospapier: 100 Punkte vor (ESC J)
    2: bytes([0x1D, 0x0C]),         # Etikett mit Luecke: zum naechsten Etikett
    3: b"",                         # schwarze Marke: nichts
}
AUFWECKEN = bytes(15)
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
        raise ValueError("Das Bild ist leer.")
    zeilenbytes = (breite + 7) // 8
    if zeilenbytes > 0xFFFF or hoehe > 0xFFFF:
        raise ValueError("Das Bild ist zu groß für den Drucker.")
    kopf = bytes([0x1D, 0x76, 0x30, 0x00,
                  zeilenbytes & 0xFF, zeilenbytes >> 8,
                  hoehe & 0xFF, hoehe >> 8])
    return kopf + raster(bild)


def auftrag(bild, papiertyp: int, dichte: int) -> bytes:
    if papiertyp not in NACHSCHUB:
        raise ValueError(f"Unbekannter Papiertyp: {papiertyp}")
    if dichte not in DICHTE_BYTE:
        raise ValueError(f"Unbekannte Dichte: {dichte}")
    return b"".join([
        bytes([0x1F, 0x70, 0x02, DICHTE_BYTE[dichte]]),
        AUFWECKEN,
        DRUCKER_AN,
        bildbefehl(bild),
        NACHSCHUB[papiertyp],
        ENDE,
    ])
