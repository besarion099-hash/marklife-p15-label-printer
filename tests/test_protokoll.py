# -*- coding: utf-8 -*-
import pytest
from PIL import Image

from kern import protokoll


def _muster():
    """16 x 2 Punkte: Zeile 0 links halb schwarz, Zeile 1 jeder zweite Punkt."""
    bild = Image.new("1", (16, 2), 1)          # 1 = weiss
    for x in range(8):
        bild.putpixel((x, 0), 0)
    for x in range(0, 16, 2):
        bild.putpixel((x, 1), 0)
    return bild


def test_raster_des_musters():
    assert protokoll.raster(_muster()) == bytes([0xFF, 0x00, 0xAA, 0xAA])


def test_ueberzaehlige_bits_bleiben_null():
    bild = Image.new("1", (13, 1), 0)          # ganz schwarz, 13 Punkte
    assert protokoll.raster(bild) == bytes([0xFF, 0xF8])


def test_graustufen_schwelle_bei_128():
    bild = Image.new("L", (8, 1), 200)
    bild.putpixel((0, 0), 127)
    bild.putpixel((1, 0), 128)
    assert protokoll.raster(bild) == bytes([0x80])


def test_bildbefehl_kopf():
    kopf = protokoll.bildbefehl(_muster())[:8]
    assert kopf == bytes([0x1D, 0x76, 0x30, 0x00, 0x02, 0x00, 0x02, 0x00])


def test_kopf_mit_grossen_massen():
    kopf = protokoll.bildbefehl(Image.new("1", (300, 300), 1))[:8]
    assert kopf == bytes([0x1D, 0x76, 0x30, 0x00, 38, 0x00, 0x2C, 0x01])


@pytest.mark.parametrize("papiertyp, nachschub",
                         [(1, b"\x1b\x4a\x64"), (2, b"\x1d\x0c"), (3, b"")])
@pytest.mark.parametrize("dichte, d", [(1, 0x02), (2, 0x06), (3, 0x0A)])
def test_auftrag_ganz(papiertyp, nachschub, dichte, d):
    erwartet = (bytes([0x1F, 0x70, 0x02, d])
                + bytes(15)
                + bytes([0x10, 0xFF, 0xF1, 0x02])
                + bytes([0x1D, 0x76, 0x30, 0x00, 0x02, 0x00, 0x02, 0x00,
                         0xFF, 0x00, 0xAA, 0xAA])
                + nachschub
                + bytes([0x10, 0xFF, 0xF1, 0x45]))
    assert protokoll.auftrag(_muster(), papiertyp, dichte) == erwartet


def test_unbekannte_werte():
    with pytest.raises(ValueError):
        protokoll.auftrag(_muster(), 4, 2)
    with pytest.raises(ValueError):
        protokoll.auftrag(_muster(), 2, 0)
