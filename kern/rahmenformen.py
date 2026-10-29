# -*- coding: utf-8 -*-
"""Die Rahmenformen. Jede Funktion zeichnet in eine Flaeche breite x hoehe
(Punkte) mit Strichbreite s und Eckenradius r. Reihenfolge = Galerie."""

from __future__ import annotations

from kern.formen import (ECKEN, MIN_PUNKTE, folge, gespiegelt, muster, raute, ringsum, scheibe,
                         spirale, strecke, zierstrich, zug)
from kern.rahmenmuster import (briefmarke, herzen, kordel, kreise, perlen, schienen, sterne,
                               wellen, zacken)


def _kasten(z, b, h, e, s, r):
    if b - 1 - 2 * e >= 0 and h - 1 - 2 * e >= 0:      # zu dicker Strich fuellt die Flaeche
        z.rounded_rectangle([e, e, b - 1 - e, h - 1 - e], outline=0, width=s,
                            radius=max(0, min(r - e, (min(b, h) - 2 * e) // 2)))


def _klein(b, h):
    return min(b, h)


def einfach(z, b, h, s, r):
    _kasten(z, b, h, 0, s, r)


def doppelt(z, b, h, s, r):
    _kasten(z, b, h, 0, s, r)
    _kasten(z, b, h, 2 * s, s, r)


def dick_duenn(z, b, h, s, r):
    _kasten(z, b, h, 0, 2 * s, r)
    _kasten(z, b, h, 3 * s, MIN_PUNKTE, r)


def dreifach(z, b, h, s, r):
    d = zierstrich(s, s * 2)
    for e in (0, 2 * d, 4 * d):
        _kasten(z, b, h, e, d, r)


def _gemustert(z, b, h, s, art):
    for a, c in (((0, 0), (b - s, 0)), ((b - s, 0), (b - s, h - s)),
                 ((b - s, h - s), (0, h - s)), ((0, h - s), (0, 0))):
        muster(z, a, c, s, folge(art, s))


def gestrichelt(z, b, h, s, r):
    _gemustert(z, b, h, s, "gestrichelt")


def gepunktet(z, b, h, s, r):
    _gemustert(z, b, h, s, "gepunktet")


def linie_punkte(z, b, h, s, r):
    _kasten(z, b, h, 0, s, r)
    m = 3 * s
    for x, y in ringsum(b, h, m, 3 * s):
        scheibe(z, x, y, max(1, s // 2))


def abgerundet(z, b, h, s, r):
    _kasten(z, b, h, 0, s, max(r, _klein(b, h) // 3))


def kapsel(z, b, h, s, r):
    _kasten(z, b, h, 0, s, _klein(b, h) // 2)


def oval(z, b, h, s, r):
    z.ellipse([0, 0, b - 1, h - 1], outline=0, width=s)


def doppel_oval(z, b, h, s, r):
    z.ellipse([0, 0, b - 1, h - 1], outline=0, width=s)
    e = 2 * s
    if b > 2 * e + s and h > 2 * e + s:
        z.ellipse([e, e, b - 1 - e, h - 1 - e], outline=0, width=MIN_PUNKTE)


def _achteck(b, h, e, c):
    x0, y0, x1, y1 = e, e, b - 1 - e, h - 1 - e
    return [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1),
            (x0, y1 - c), (x0, y0 + c)]


def abgeschraegt(z, b, h, s, r):
    zug(z, _achteck(b, h, s / 2, max(2 * s, _klein(b, h) // 5)), s, geschlossen=True)


def doppelt_abgeschraegt(z, b, h, s, r):
    c = max(2 * s, _klein(b, h) // 5)
    zug(z, _achteck(b, h, s / 2, c), s, geschlossen=True)
    zug(z, _achteck(b, h, s / 2 + 2 * s, max(1, c - s)), MIN_PUNKTE, geschlossen=True)


def _ticketform(z, b, h, e, s, r):
    x0, y0, x1, y1 = e, e, b - 1 - e, h - 1 - e
    strecke(z, (x0 + r, y0), (x1 - r, y0), s)
    strecke(z, (x0 + r, y1 - s + 1), (x1 - r, y1 - s + 1), s)
    strecke(z, (x0, y0 + r), (x0, y1 - r), s)
    strecke(z, (x1 - s + 1, y0 + r), (x1 - s + 1, y1 - r), s)
    for (cx, cy, start) in ((x0, y0, 0), (x1, y0, 90), (x1, y1, 180), (x0, y1, 270)):
        z.arc([cx - r, cy - r, cx + r, cy + r], start, start + 90, fill=0, width=s)


def ticket(z, b, h, s, r):
    _ticketform(z, b, h, 0, s, max(r, 3 * s, _klein(b, h) // 8))


def plakette(z, b, h, s, r):
    rr = max(r, 3 * s, _klein(b, h) // 6)
    _ticketform(z, b, h, 0, s, rr)
    _ticketform(z, b, h, 2 * s, MIN_PUNKTE, rr)


def viktorianisch(z, b, h, s, r):
    _kasten(z, b, h, 0, s, 0)
    e = 2 * s
    _ticketform(z, b, h, e, MIN_PUNKTE, max(3 * s, _klein(b, h) // 6))
    for rechts, unten in ECKEN:
        (x, y), = gespiegelt([(e, e)], b, h, rechts, unten)
        scheibe(z, x, y, s)


def ecken(z, b, h, s, r):
    lang = max(3 * s, _klein(b, h) // 4)
    for rechts, unten in ECKEN:
        a, c, d = gespiegelt([(0, lang - 1), (0, 0), (lang - 1, 0)], b, h, rechts, unten)
        for p, q in ((c, a), (c, d)):
            p = (min(p[0], b - s) if rechts else p[0], min(p[1], h - s) if unten else p[1])
            q = (min(q[0], b - s) if rechts else q[0], min(q[1], h - s) if unten else q[1])
            strecke(z, p, q, s)


def eckrauten(z, b, h, s, r):
    m = max(3 * s, _klein(b, h) // 8)
    z.rectangle([m, m, b - 1 - m, h - 1 - m], outline=0, width=MIN_PUNKTE)
    for rechts, unten in ECKEN:
        (x, y), = gespiegelt([(m, m)], b, h, rechts, unten)
        raute(z, x, y, m)


def eckpunkte(z, b, h, s, r):
    m = max(3 * s, _klein(b, h) // 9)
    _kasten(z, b, h, m, MIN_PUNKTE, 0)
    for rechts, unten in ECKEN:
        (x, y), = gespiegelt([(m, m)], b, h, rechts, unten)
        scheibe(z, x, y, m)


def faecher(z, b, h, s, r):
    """Art-deco: Rahmen mit Viertelbogen-Faechern in den Ecken."""
    _kasten(z, b, h, 0, s, 0)
    gross = max(4 * s, _klein(b, h) // 3)
    for rechts, unten in ECKEN:
        cx, cy = gespiegelt([(0, 0)], b, h, rechts, unten)[0]
        start = {(False, False): 0, (True, False): 90, (True, True): 180, (False, True): 270}
        for anteil in (1.0, 0.68, 0.36):
            rr = gross * anteil
            z.arc([cx - rr, cy - rr, cx + rr, cy + rr], start[(rechts, unten)],
                  start[(rechts, unten)] + 90, fill=0, width=MIN_PUNKTE)


def stufen(z, b, h, s, r):
    """Art-deco: gestufte Ecken, innen ein zweiter Rahmen."""
    c = max(3 * s, _klein(b, h) // 6)
    e = s / 2
    x0, y0, x1, y1 = e, e, b - 1 - e, h - 1 - e
    zug(z, [(x0 + c, y0), (x1 - c, y0), (x1 - c, y0 + c), (x1, y0 + c), (x1, y1 - c),
            (x1 - c, y1 - c), (x1 - c, y1), (x0 + c, y1), (x0 + c, y1 - c), (x0, y1 - c),
            (x0, y0 + c), (x0 + c, y0 + c)], s, geschlossen=True)
    innen = c + 2 * s
    if b > 2 * innen + s and h > 2 * innen + s:
        z.rectangle([innen, innen, b - 1 - innen, h - 1 - innen], outline=0, width=MIN_PUNKTE)


def schnoerkel(z, b, h, s, r):
    """Kalligrafische Ecken: die Kanten rollen sich in den Ecken ein."""
    rr = max(2 * s, _klein(b, h) // 6)
    w = zierstrich(s, rr / 2)
    c = rr + w / 2
    strecke(z, (round(c), 0), (round(b - 1 - c), 0), w)
    strecke(z, (round(c), h - w), (round(b - 1 - c), h - w), w)
    strecke(z, (0, round(c)), (0, round(h - 1 - c)), w)
    strecke(z, (b - w, round(c)), (b - w, round(h - 1 - c)), w)
    rolle = spirale(c, c, rr, -90, -1.3, 0.2)
    for rechts, unten in ECKEN:
        zug(z, gespiegelt(rolle, b, h, rechts, unten), w)


def geschweift(z, b, h, s, r):
    """Geschweifte Klammern links und rechts, oben und unten gerade."""
    k = max(4 * s, _klein(b, h) // 4)
    e = s / 2
    mitte = (h - 1) / 2
    halb = [(k, e), (k * 0.55, e + k * 0.15), (k * 0.5, e + k * 0.5), (k * 0.5, mitte - k * 0.5),
            (k * 0.4, mitte - k * 0.15), (e, mitte)]
    form = halb + [(x, h - 1 - y) for x, y in reversed(halb)]
    zug(z, form, s)
    zug(z, gespiegelt(form, b, h, True, False), s)
    strecke(z, (round(k), 0), (round(b - 1 - k), 0), s)
    strecke(z, (round(k), h - s), (round(b - 1 - k), h - s), s)


def banner(z, b, h, s, r):
    """Banderole mit Schwalbenschwanz-Enden."""
    n, e = max(2 * s, h // 4), s / 2
    zug(z, [(e, e), (b - 1 - e, e), (b - 1 - n, (h - 1) / 2), (b - 1 - e, h - 1 - e),
            (e, h - 1 - e), (n, (h - 1) / 2)], s, geschlossen=True)


def schild(z, b, h, s, r):
    """Sechseckiges Schild mit spitzen Enden."""
    p, e = max(2 * s, h // 3), s / 2
    zug(z, [(p, e), (b - 1 - p, e), (b - 1 - e, (h - 1) / 2), (b - 1 - p, h - 1 - e),
            (p, h - 1 - e), (e, (h - 1) / 2)], s, geschlossen=True)


FORMEN = [
    ("einfach", "einfach", einfach), ("doppelt", "doppelt", doppelt),
    ("dick-duenn", "dick-dünn", dick_duenn), ("dreifach", "dreifach", dreifach),
    ("gestrichelt", "gestrichelt", gestrichelt), ("gepunktet", "gepunktet", gepunktet),
    ("linie-punkte", "Linie mit Punkten", linie_punkte), ("abgerundet", "abgerundet", abgerundet),
    ("kapsel", "Kapsel", kapsel), ("oval", "oval", oval), ("doppel-oval", "Doppel-Oval", doppel_oval),
    ("abgeschraegt", "abgeschrägt", abgeschraegt),
    ("doppelt-abgeschraegt", "abgeschrägt doppelt", doppelt_abgeschraegt),
    ("ticket", "Ticket", ticket), ("plakette", "Plakette", plakette),
    ("viktorianisch", "viktorianisch", viktorianisch), ("ecken", "Eckwinkel", ecken),
    ("eckrauten", "Eckrauten", eckrauten), ("eckpunkte", "Eckpunkte", eckpunkte),
    ("faecher", "Art déco Fächer", faecher), ("stufen", "Art déco Stufen", stufen),
    ("schnoerkel", "Schnörkel", schnoerkel), ("geschweift", "geschweifte Klammern", geschweift),
    ("banner", "Banderole", banner), ("schild", "Schild", schild),
    ("wellen", "Wellenrand", wellen), ("zacken", "Zackenrand", zacken),
    ("briefmarke", "Briefmarke", briefmarke), ("kordel", "Kordel", kordel),
    ("schienen", "Schienen", schienen), ("perlen", "Perlen", perlen), ("kreise", "Kreise", kreise),
    ("sterne", "Sterne", sterne), ("herzen", "Herzen", herzen),
]
