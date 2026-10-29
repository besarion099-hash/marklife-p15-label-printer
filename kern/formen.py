# -*- coding: utf-8 -*-
"""Grundbausteine fuer Rahmen und Linien, ausgelegt fuer Thermodruck bei 203 dpi.

Ein Druckpunkt ist 0,125 mm. Einpunkt-Linien brechen bei heller Dichte
leicht ab, deshalb ist jede Linie mindestens 2 Punkte (0,25 mm) breit,
und auch Striche, Punkte und Luecken sind mindestens 2 Punkte lang.
Vollflaechige Formen gibt es bewusst nicht: grosse Schwarzflaechen
belasten den Thermokopf.
"""

from __future__ import annotations

import math

MIN_PUNKTE = 2


def staerke(punkte: int) -> int:
    return max(MIN_PUNKTE, punkte)


def zierstrich(s: int, einheit: float) -> int:
    """Strichbreite fuer feine Muster: hoechstens die halbe Mustereinheit."""
    return max(MIN_PUNKTE, min(s, int(einheit // 2)))


def halbhoch(h, s, faktor):
    """Halbe Musterhoehe einer Linie: so gross wie erlaubt, hoechstens faktor * s."""
    return max(s / 2, min((h - s) / 2, faktor * s))


def mittellinie(z, b, h, s):
    strecke(z, (0, (h - s) // 2), (b - 1, (h - s) // 2), s)


def strecke(z, a, b, s):
    """Gerade Strecke der Breite s (Punkte); waagerecht/senkrecht exakt gefuellt."""
    (x0, y0), (x1, y1) = a, b
    if y0 == y1:
        z.rectangle([min(x0, x1), y0, max(x0, x1), y0 + s - 1], fill=0)
    elif x0 == x1:
        z.rectangle([x0, min(y0, y1), x0 + s - 1, max(y0, y1)], fill=0)
    else:
        z.line([a, b], fill=0, width=s)


def zug(z, punkte, s, geschlossen=False):
    """Linienzug mit runden Gelenken; geschlossen fuehrt zum Anfang zurueck."""
    punkte = [(round(x), round(y)) for x, y in punkte]
    if geschlossen:
        punkte = punkte + punkte[:2]
    if len(punkte) > 1:
        z.line(punkte, fill=0, width=s, joint="curve")


def muster(z, a, b, s, folge):
    """Strecke a-b als Muster: folge = [(laenge, an), ...] in Punkten, wiederholt."""
    (x0, y0), (x1, y1) = a, b
    gesamt = math.hypot(x1 - x0, y1 - y0)
    if gesamt == 0:
        return
    dx, dy = (x1 - x0) / gesamt, (y1 - y0) / gesamt
    pos, i = 0.0, 0
    while pos < gesamt:
        laenge, an = folge[i % len(folge)]
        ende = min(gesamt, pos + laenge)
        if an:
            p = (round(x0 + dx * pos), round(y0 + dy * pos))
            q = (round(x0 + dx * (ende - 1)), round(y0 + dy * (ende - 1)))
            strecke(z, p, q, s)
        pos, i = ende, i + 1


def folge(art, s):
    strich, luecke = max(4 * s, 8), max(2 * s, 4)
    if art == "gestrichelt":
        return [(strich, True), (luecke, False)]
    if art == "lang-gestrichelt":
        return [(2 * strich, True), (luecke, False)]
    if art == "gepunktet":
        return [(s, True), (max(s, MIN_PUNKTE) + s // 2, False)]
    if art == "strich-punkt-punkt":
        return [(strich, True), (luecke, False), (s, True), (luecke, False), (s, True),
                (luecke, False)]
    return [(strich, True), (luecke, False), (s, True), (luecke, False)]   # strich-punkt


def verteilt(von, bis, abstand):
    """Gleichmaessig verteilte Mittelpunkte von..bis, beide Enden eingeschlossen."""
    if bis <= von:
        return [(von + bis) / 2]
    n = max(1, round((bis - von) / abstand))
    return [von + i * (bis - von) / n for i in range(n + 1)]


def ringsum(breite, hoehe, m, abstand):
    """Mittelpunkte entlang eines Rechtecks mit Abstand m vom Rand, Ecken einmal."""
    x0, y0, x1, y1 = m, m, breite - 1 - m, hoehe - 1 - m
    punkte = [(x, y0) for x in verteilt(x0, x1, abstand)]
    punkte += [(x, y1) for x in verteilt(x0, x1, abstand)]
    seite = verteilt(y0, y1, abstand)[1:-1]
    punkte += [(x0, y) for y in seite] + [(x1, y) for y in seite]
    return punkte


def scheibe(z, x, y, r):
    z.ellipse([x - r, y - r, x + r, y + r], fill=0)


def ring(z, x, y, r, s, ry=None):
    ry = r if ry is None else ry
    z.ellipse([x - r, y - ry, x + r, y + ry], outline=0, width=s)


def raute(z, x, y, rx, ry=None):
    ry = rx if ry is None else ry
    z.polygon([(x - rx, y), (x, y - ry), (x + rx, y), (x, y + ry)], fill=0)


def stern(z, x, y, r):
    punkte = []
    for i in range(10):
        w = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        punkte.append((x + rr * math.cos(w), y + rr * math.sin(w)))
    z.polygon(punkte, fill=0)


def herz(z, x, y, r):
    punkte = []
    for i in range(48):
        t = 2 * math.pi * i / 48
        hx = 16 * math.sin(t) ** 3
        hy = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        punkte.append((x + hx * r / 17, y - hy * r / 17 - r * 0.1))
    z.polygon(punkte, fill=0)


def blatt(z, x, y, laenge, winkel, breite=0.22):
    """Spitzes Blatt (Linse) ab (x, y) in Richtung winkel (Bogenmass);
    breite ist die halbe Blattbreite als Anteil der Laenge."""
    dx, dy = math.cos(winkel), math.sin(winkel)
    nx, ny = -dy, dx
    breit = laenge * breite
    oben, unten = [], []
    for i in range(13):
        t = i / 12
        b = breit * math.sin(math.pi * t)
        px, py = x + dx * laenge * t, y + dy * laenge * t
        oben.append((px + nx * b, py + ny * b))
        unten.append((px - nx * b, py - ny * b))
    z.polygon(oben + unten[::-1], fill=0)


def spirale(cx, cy, r, start, umdrehungen=1.25, ende=0.3):
    """Punkte einer nach innen laufenden Spirale; start in Grad, positiv dreht im
    Bild im Uhrzeigersinn (y zeigt nach unten), negative umdrehungen dagegen."""
    schritte = max(12, int(abs(umdrehungen) * 40))
    punkte = []
    for i in range(schritte + 1):
        t = i / schritte
        w = math.radians(start) + t * umdrehungen * 2 * math.pi
        rr = r * (1 - (1 - ende) * t)
        punkte.append((cx + rr * math.cos(w), cy + rr * math.sin(w)))
    return punkte


def gespiegelt(punkte, breite, hoehe, rechts, unten):
    """Punkte aus der linken oberen Ecke in eine andere Ecke spiegeln."""
    return [((breite - 1 - x) if rechts else x, (hoehe - 1 - y) if unten else y)
            for x, y in punkte]


ECKEN = [(False, False), (True, False), (False, True), (True, True)]
