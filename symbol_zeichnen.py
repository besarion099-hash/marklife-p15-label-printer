# -*- coding: utf-8 -*-
"""Zeichnet das Programmsymbol (gui/symbol.ico und gui/symbol.png).

Motiv: der Marklife P15 in Schraegansicht - cremefarbenes Gehaeuse,
schwarze Glasfront, an der Seite kommt ein Etikettstreifen heraus.
Eigene Zeichnung, kein Herstellerbild. Nur noetig, wenn sich das Symbol
aendern soll: venv\\Scripts\\python.exe symbol_zeichnen.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

HIER = Path(__file__).resolve().parent
GROSS = 1024
GROESSEN = [16, 20, 24, 32, 40, 48, 64, 96, 128, 256]

CREME, CREME_SEITE, CREME_KANTE = (241, 235, 212), (214, 205, 172), (190, 180, 146)
GLAS, RAND = (22, 22, 24), (120, 120, 118)


def zeichnen() -> Image.Image:
    bild = Image.new("RGBA", (GROSS, GROSS), (0, 0, 0, 0))

    schatten = Image.new("RGBA", bild.size, (0, 0, 0, 0))
    ImageDraw.Draw(schatten).ellipse([150, 900, 900, 990], fill=(0, 0, 0, 90))
    bild.alpha_composite(schatten.filter(ImageFilter.GaussianBlur(28)))

    z = ImageDraw.Draw(bild)
    # Seitenwand (dahinter, nach rechts versetzt) und Front
    z.rounded_rectangle([250, 110, 880, 930], radius=130, fill=CREME_SEITE, outline=CREME_KANTE,
                        width=6)
    z.rounded_rectangle([120, 80, 760, 940], radius=130, fill=CREME, outline=CREME_KANTE, width=6)
    # Schlitz an der Seite und Etikettstreifen
    z.rounded_rectangle([800, 250, 826, 560], radius=10, fill=(150, 142, 112))
    streifen = [(812, 300), (905, 292), (980, 300), (1010, 330), (1000, 520), (968, 545),
                (900, 528), (812, 520)]
    z.polygon(streifen, fill=(255, 255, 255), outline=(170, 170, 170))
    z.line([(812, 300), (905, 292), (980, 300), (1010, 330)], fill=(140, 140, 140), width=5)
    for y in (360, 400, 440, 480):                            # angedeuteter Druck
        z.line([(850, y + 8), (960, y)], fill=(70, 70, 70), width=12)
    # schwarze Glasfront mit Rand und Glanz
    z.rounded_rectangle([170, 140, 710, 880], radius=95, fill=RAND)
    z.rounded_rectangle([186, 156, 694, 864], radius=82, fill=GLAS)
    glanz = Image.new("RGBA", bild.size, (0, 0, 0, 0))
    ImageDraw.Draw(glanz).polygon([(200, 170), (520, 170), (200, 620)],
                                  fill=(255, 255, 255, 38))
    maske = Image.new("L", bild.size, 0)
    ImageDraw.Draw(maske).rounded_rectangle([186, 156, 694, 864], radius=82, fill=255)
    bild.paste(Image.alpha_composite(bild, glanz), (0, 0), maske)
    return bild


def main():
    gross = zeichnen()
    gross.resize((256, 256), Image.LANCZOS).save(HIER / "gui" / "symbol.png")
    gross.save(HIER / "gui" / "symbol.ico", sizes=[(g, g) for g in GROESSEN])
    print("gui/symbol.ico und gui/symbol.png geschrieben")


if __name__ == "__main__":
    main()
