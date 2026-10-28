# -*- coding: utf-8 -*-
import pytest

from kern import codes


def test_ean_pruefziffer():
    assert codes.ean_pruefziffer("400638133393") == "1"


def test_ean13_module():
    module = codes.barcode_module("4006381333931", "ean13")
    assert len(module) == 95
    assert module.startswith("101") and module.endswith("101")
    assert codes.barcode_module("400638133393", "ean13") == module


def test_ean13_falsche_pruefziffer():
    with pytest.raises(codes.CodeFehler, match="richtig wäre 1"):
        codes.barcode_module("4006381333932", "ean13")


def test_ean13_falsche_laenge():
    with pytest.raises(codes.CodeFehler, match="12 oder 13 Ziffern"):
        codes.barcode_module("12345", "ean13")


def test_code128_module():
    module = codes.barcode_module("ABC", "code128")
    assert len(module) % 11 == 2                  # n Zeichen zu 11 + Stopp zu 13
    assert module.startswith("11010")             # Startzeichen A, B oder C
    assert module.endswith("1100011101011")       # Stoppzeichen


def test_barcode_bild():
    bild = codes.barcode_bild("ABC", "code128", 200, 60, True)
    assert bild.size == (200, 60) and bild.mode == "L"
    assert bild.getextrema() == (0, 255)


def test_barcode_zu_schmal():
    with pytest.raises(codes.CodeFehler, match="Punkte Breite"):
        codes.barcode_bild("ABCDEFGHIJ", "code128", 40, 60, False)


def test_qr_bild():
    bild = codes.qr_bild("Hallo", 100)        # 21 Module zu 4 Punkten, Rand 8
    assert bild.size == (100, 100)
    assert bild.getpixel((8, 8)) == 0         # Ecke des Suchmusters
    assert bild.getpixel((0, 0)) == 255


def test_qr_feld_zu_klein():
    with pytest.raises(codes.CodeFehler, match="mindestens 21 Punkte"):
        codes.qr_bild("Hallo", 10)


def test_qr_zu_lang():
    with pytest.raises(codes.CodeFehler, match="zu lang"):
        codes.qr_bild("x" * 5000, 400)
