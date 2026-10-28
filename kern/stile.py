# -*- coding: utf-8 -*-
"""Rahmen- und Linienstile, ausgelegt fuer Thermodruck bei 203 dpi.

Ein Druckpunkt ist 0,125 mm. Einpunkt-Linien brechen bei heller Dichte
leicht ab, deshalb ist jede Linie hier mindestens 2 Punkte (0,25 mm) breit,
und auch Striche, Punkte und Luecken sind mindestens 2 Punkte lang.
Vollflaechige Stile gibt es bewusst nicht: grosse Schwarzflaechen belasten
den Thermokopf.
"""

from __future__ import annotations

import math

MIN_PUNKTE = 2

RAHMENSTILE = [("einfach", "einfach"), ("doppelt", "doppelt"), ("dick-duenn", "dick-dünn"),
               ("gestrichelt", "gestrichelt"), ("gepunktet", "gepunktet"),
               ("wellen", "Wellenrand"), ("ecken", "Eckwinkel"), ("ticket", "Ticket")]
LINIENSTILE = [("durchgezogen", "durchgezogen"), ("doppelt", "doppelt"),
               ("gestrichelt", "gestrichelt"), ("gepunktet", "gepunktet"),
               ("strich-punkt", "Strich-Punkt"), ("welle", "Welle"), ("zickzack", "Zickzack"),
               ("ornament", "Ornament")]


def staerke(punkte: int) -> int:
    return max(MIN_PUNKTE, punkte)


# --- Grundbausteine ------------------------------------------------------------

def _strecke(zeichner, a, b, s):
    """Gerade Strecke der Breite s (Punkte), als Rechteck exakt gefuellt."""
    (x0, y0), (x1, y1) = a, b
    if y0 == y1:
        zeichner.rectangle([min(x0, x1), y0, max(x0, x1), y0 + s - 1], fill=0)
    elif x0 == x1:
        zeichner.rectangle([x0, min(y0, y1), x0 + s - 1, max(y0, y1)], fill=0)
    else:
        zeichner.line([a, b], fill=0, width=s)


def _muster(zeichner, a, b, s, folge):
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
            _strecke(zeichner, p, q, s)
        pos, i = ende, i + 1


def _folge(stil, s):
    strich, luecke = max(4 * s, 8), max(2 * s, 4)
    if stil == "gestrichelt":
        return [(strich, True), (luecke, False)]
    if stil == "gepunktet":
        return [(s, True), (max(s, MIN_PUNKTE) + s // 2, False)]
    return [(strich, True), (luecke, False), (s, True), (luecke, False)]   # strich-punkt


def _rechteck_kanten(x0, y0, x1, y1):
    return [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)),
            ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]


# --- Rahmen --------------------------------------------------------------------

def rahmen(zeichner, breite, hoehe, s, ecken, stil):
    """Rahmen in eine Flaeche breite x hoehe zeichnen (Masse in Punkten)."""
    s = staerke(s)
    if stil == "doppelt":
        zeichner.rounded_rectangle([0, 0, breite - 1, hoehe - 1], radius=ecken, outline=0, width=s)
        e = 2 * s
        zeichner.rounded_rectangle([e, e, breite - 1 - e, hoehe - 1 - e],
                                   radius=max(0, ecken - e), outline=0, width=s)
    elif stil == "dick-duenn":
        zeichner.rounded_rectangle([0, 0, breite - 1, hoehe - 1], radius=ecken, outline=0,
                                   width=2 * s)
        e = 3 * s
        zeichner.rounded_rectangle([e, e, breite - 1 - e, hoehe - 1 - e],
                                   radius=max(0, ecken - e), outline=0, width=MIN_PUNKTE)
    elif stil in ("gestrichelt", "gepunktet"):
        for a, b in _rechteck_kanten(0, 0, breite - s, hoehe - s):
            _muster(zeichner, a, b, s, _folge(stil, s))
    elif stil == "wellen":
        _wellenrand(zeichner, breite, hoehe, s)
    elif stil == "ecken":
        lang = max(3 * s, min(breite, hoehe) // 4)
        for (x, y, rx, ry) in ((0, 0, 1, 1), (breite - s, 0, -1, 1),
                               (0, hoehe - s, 1, -1), (breite - s, hoehe - s, -1, -1)):
            _strecke(zeichner, (x, y), (x + rx * (lang - 1), y), s)
            _strecke(zeichner, (x, y), (x, y + ry * (lang - 1)), s)
    elif stil == "ticket":
        _ticket(zeichner, breite, hoehe, s, max(ecken, 3 * s, min(breite, hoehe) // 8))
    else:
        zeichner.rounded_rectangle([0, 0, breite - 1, hoehe - 1], radius=ecken, outline=0, width=s)


def _wellenrand(zeichner, breite, hoehe, s):
    """Bogenkante: Halbkreise nach aussen, die Ecken bleiben geschlossen."""
    d = max(6 * s, 12)
    r = d // 2
    innen = [r, r, breite - 1 - r, hoehe - 1 - r]
    if innen[2] <= innen[0] or innen[3] <= innen[1]:
        zeichner.rectangle([0, 0, breite - 1, hoehe - 1], outline=0, width=s)
        return
    nx = max(1, round((innen[2] - innen[0]) / d))
    ny = max(1, round((innen[3] - innen[1]) / d))
    bx, by = (innen[2] - innen[0]) / nx, (innen[3] - innen[1]) / ny
    for i in range(nx):
        x = innen[0] + i * bx
        zeichner.arc([x, 0, x + bx, 2 * r], 180, 360, fill=0, width=s)
        zeichner.arc([x, hoehe - 1 - 2 * r, x + bx, hoehe - 1], 0, 180, fill=0, width=s)
    for i in range(ny):
        y = innen[1] + i * by
        zeichner.arc([0, y, 2 * r, y + by], 90, 270, fill=0, width=s)
        zeichner.arc([breite - 1 - 2 * r, y, breite - 1, y + by], 270, 90, fill=0, width=s)


def _ticket(zeichner, breite, hoehe, s, r):
    """Rahmen mit nach innen gewoelbten Ecken (Eintrittskarten-Form)."""
    x1, y1 = breite - 1, hoehe - 1
    _strecke(zeichner, (r, 0), (x1 - r, 0), s)
    _strecke(zeichner, (r, y1 - s + 1), (x1 - r, y1 - s + 1), s)
    _strecke(zeichner, (0, r), (0, y1 - r), s)
    _strecke(zeichner, (x1 - s + 1, r), (x1 - s + 1, y1 - r), s)
    for (cx, cy, start) in ((0, 0, 0), (x1, 0, 90), (x1, y1, 180), (0, y1, 270)):
        zeichner.arc([cx - r, cy - r, cx + r, cy + r], start, start + 90, fill=0, width=s)


# --- Linien --------------------------------------------------------------------

def linie(zeichner, breite, hoehe, s, stil):
    """Waagerechte Linie mittig in eine Flaeche breite x hoehe zeichnen."""
    s = min(hoehe, staerke(s))
    mitte = (hoehe - s) // 2
    if stil == "doppelt":
        abstand = min(2 * s, max(0, (hoehe - 2 * s) // 2))
        oben = max(0, mitte - (s + abstand) // 2 - s // 2)
        _strecke(zeichner, (0, oben), (breite - 1, oben), s)
        _strecke(zeichner, (0, oben + s + abstand), (breite - 1, oben + s + abstand), s)
    elif stil in ("gestrichelt", "gepunktet", "strich-punkt"):
        _muster(zeichner, (0, mitte), (breite - 1, mitte), s, _folge(stil, s))
    elif stil in ("welle", "zickzack"):
        welle = stil == "welle"
        hub = max(s, min((hoehe - s) // 2, (3 if welle else 4) * s))
        periode = max((16 if welle else 8) * s, 24 if welle else 16)
        punkte = []
        schritt = 2 if stil == "welle" else periode / 4
        x = 0.0
        while x <= breite - 1:
            if stil == "welle":
                y = math.sin(2 * math.pi * x / periode)
            else:
                phase = (x / periode) % 1
                y = 4 * phase - 1 if phase < 0.5 else 3 - 4 * phase
            punkte.append((round(x), round(hoehe / 2 + y * hub)))
            x += schritt
        zeichner.line(punkte, fill=0, width=s, joint="curve")
    elif stil == "ornament":
        mx, my = breite // 2, hoehe // 2
        raute = max(3 * s, min(hoehe // 2 - 1, 6 * s))
        _strecke(zeichner, (0, mitte), (mx - raute - 2 * s, mitte), s)
        _strecke(zeichner, (mx + raute + 2 * s, mitte), (breite - 1, mitte), s)
        zeichner.polygon([(mx - raute, my), (mx, my - raute), (mx + raute, my), (mx, my + raute)],
                         fill=0)
    else:
        _strecke(zeichner, (0, mitte), (breite - 1, mitte), s)
