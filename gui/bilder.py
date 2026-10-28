# -*- coding: utf-8 -*-
"""Kleine Bruecken zwischen Pillow und Qt."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PySide6.QtGui import QImage
from PySide6.QtWidgets import QMessageBox


def zu_qimage(bild) -> QImage:
    grau = bild.convert("L")
    qbild = QImage(grau.tobytes(), grau.width, grau.height, grau.width,
                   QImage.Format.Format_Grayscale8)
    return qbild.copy()      # die Bytes oben leben nur bis zum Ende dieser Funktion


def bild_lesen(pfad, eltern=None) -> bytes | None:
    """Datei lesen und pruefen, dass Pillow sie oeffnen kann; sonst Meldung und None."""
    from PIL import Image
    try:
        daten = Path(pfad).read_bytes()
        with Image.open(BytesIO(daten)) as bild:
            bild.verify()
    except (OSError, SyntaxError, ValueError) as fehler:
        QMessageBox.warning(eltern, "Bild", f"Das Bild lässt sich nicht lesen:\n{fehler}")
        return None
    return daten
