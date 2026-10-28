# -*- coding: utf-8 -*-
"""Vom Etikett zum Papier: zeichnen, drehen, Auftrag bauen, senden.

Alle Auftraege werden gebaut, bevor der erste gesendet wird. Ein Fehler
in Zeile 40 einer Serie faellt so auf, bevor Etiketten verbraucht sind.
"""

from __future__ import annotations

import dataclasses

from PIL import Image

from kern import anschluss, protokoll, zeichnen
from kern.etikett import Etikett, Rahmen, Text

TESTDREHUNGEN = (90, 270)      # der P15 druckt hochkant; 270 ist am Geraet bestaetigt
_IM_UHRZEIGERSINN = {90: Image.Transpose.ROTATE_270, 180: Image.Transpose.ROTATE_180,
                     270: Image.Transpose.ROTATE_90}


class DruckFehler(Exception):
    def __init__(self, meldung: str, fertig: int = 0):
        super().__init__(meldung)
        self.fertig = fertig


def druckbild(etikett, werte, drehung_grad: int, versatz_mm: float = 0.0):
    fehler = []
    bild = zeichnen.zeichnen(etikett, werte, fehler)
    if fehler:
        index, meldung = fehler[0]
        raise DruckFehler(f"Element {index + 1}: {meldung}")
    bild = verschieben(bild, round(versatz_mm * zeichnen.PUNKTE_JE_MM))
    if drehung_grad in _IM_UHRZEIGERSINN:
        bild = bild.transpose(_IM_UHRZEIGERSINN[drehung_grad])
    return auf_kopfbreite(bild)


def verschieben(bild, punkte: int):
    """Das Etikettbild waagerecht verschieben (negativ = nach links), Rest weiss.

    Der P15 setzt den Druck etwa 3,5 mm zu weit nach rechts (am Geraet am
    28.10.2026 gemessen); die Einstellung versatz_mm gleicht das aus.
    """
    if punkte == 0:
        return bild
    neu = Image.new(bild.mode, bild.size, 255)
    neu.paste(bild, (punkte, 0))
    return neu


def auf_kopfbreite(bild):
    """Das Bild mittig auf die 112 Punkte des Druckkopfs bringen.

    Kopfmitte = Bandmitte (am P15 beobachtet). Breiteres wird mittig
    beschnitten wie beim Windows-Treiber (30 x 15 mm: 120 -> 112),
    Schmaleres (12-mm-Band: 96 Punkte) links und rechts weiss aufgefuellt,
    sonst laege es am linken Rand des Kopfes.
    """
    kopf = protokoll.KOPF_PUNKTE
    if bild.width == kopf:
        return bild
    if bild.width > kopf:
        rand = (bild.width - kopf) // 2
        return bild.crop((rand, 0, rand + kopf, bild.height))
    breit = Image.new(bild.mode, (kopf, bild.height), 255 if bild.mode in ("1", "L") else "white")
    breit.paste(bild, ((kopf - bild.width) // 2, 0))
    return breit


def auftrag_fuer(etikett, werte, einstellungen) -> bytes:
    bild = druckbild(etikett, werte, einstellungen.drehung_grad, einstellungen.versatz_mm)
    try:
        return protokoll.auftrag(bild, einstellungen.papiertyp, einstellungen.dichte)
    except ValueError as fehler:
        raise DruckFehler(str(fehler)) from fehler


def drucken(etikett, zeilen, kopien, einstellungen, verbinden=anschluss.Verbindung,
            fortschritt=None, abbrechen=None) -> int:
    """Jede Zeile kopien-mal drucken. Liefert die Zahl gesendeter Etiketten."""
    if not einstellungen.port:
        raise DruckFehler("Kein Drucker gewählt.")
    auftraege = [auftrag_fuer(etikett, werte, einstellungen) for werte in zeilen]
    return _senden(auftraege, kopien, einstellungen, verbinden, fortschritt, abbrechen)


def _senden(auftraege, kopien, einstellungen, verbinden, fortschritt, abbrechen) -> int:
    gesamt = len(auftraege) * kopien
    fertig = 0
    try:
        with verbinden(einstellungen.port) as verbindung:
            for daten in auftraege:
                for _ in range(kopien):
                    if abbrechen is not None and abbrechen():
                        return fertig
                    verbindung.schreiben(daten, einstellungen.blockgroesse,
                                         einstellungen.pause_ms)
                    fertig += 1
                    if fortschritt is not None:
                        fortschritt(fertig, gesamt)
    except anschluss.AnschlussFehler as fehler:
        raise DruckFehler(str(fehler), fertig) from fehler
    return fertig


def testmuster(grad: int, breite_mm: float, hoehe_mm: float) -> Etikett:
    return Etikett(breite_mm, hoehe_mm, [
        Rahmen(x_mm=0, y_mm=0, breite_mm=breite_mm, hoehe_mm=hoehe_mm, strich_mm=0.375),
        Text(x_mm=1, y_mm=1, breite_mm=breite_mm - 2, hoehe_mm=hoehe_mm - 2,
             inhalt=f"↑ OBEN {grad}°", groesse_pt=8, fett=True, ausrichtung="mitte"),
    ])


def ausrichtung_testen(einstellungen, breite_mm, hoehe_mm, verbinden=anschluss.Verbindung,
                       fortschritt=None, abbrechen=None) -> int:
    """Ein Testmuster je Drehung drucken, damit man die richtige erkennt."""
    if not einstellungen.port:
        raise DruckFehler("Kein Drucker gewählt.")
    auftraege = [auftrag_fuer(testmuster(grad, breite_mm, hoehe_mm), None,
                              dataclasses.replace(einstellungen, drehung_grad=grad))
                 for grad in TESTDREHUNGEN]
    return _senden(auftraege, 1, einstellungen, verbinden, fortschritt, abbrechen)
