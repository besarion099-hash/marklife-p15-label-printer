# -*- coding: utf-8 -*-
"""Drucken in einem eigenen Thread, damit das Fenster nicht einfriert.

Die Rueckrufe fortschritt, fertig und fehler laufen ueber einen Boten,
der im Hauptthread lebt. Ein Lambda direkt am Signal des Arbeiters liefe
im Druck-Thread und duerfte dort kein Fenster anfassen.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, QThread, Signal, Slot

from kern.druck import DruckFehler


class DruckArbeiter(QObject):
    fortschritt = Signal(int, int)
    fertig = Signal(int)
    fehler = Signal(str, int)

    def __init__(self, aufgabe):
        super().__init__()
        self._aufgabe = aufgabe
        self._abbrechen = False

    def abbrechen(self):
        self._abbrechen = True

    @Slot()
    def laufen(self):
        try:
            anzahl = self._aufgabe(self.fortschritt.emit, lambda: self._abbrechen)
        except DruckFehler as fehler:
            self.fehler.emit(str(fehler), fehler.fertig)
            return
        except Exception as fehler:          # nichts darf den Thread still sterben lassen
            self.fehler.emit(f"Unerwarteter Fehler: {fehler}", 0)
            return
        self.fertig.emit(anzahl)


class _Bote(QObject):
    def __init__(self, eltern, fortschritt, fertig, fehler):
        super().__init__(eltern)
        self._rueckrufe = (fortschritt, fertig, fehler)

    @Slot(int, int)
    def fortschritt(self, fertig, gesamt):
        if self._rueckrufe[0] is not None:
            self._rueckrufe[0](fertig, gesamt)

    @Slot(int)
    def fertig(self, anzahl):
        if self._rueckrufe[1] is not None:
            self._rueckrufe[1](anzahl)

    @Slot(str, int)
    def fehler(self, meldung, fertig):
        if self._rueckrufe[2] is not None:
            self._rueckrufe[2](meldung, fertig)


def im_hintergrund(aufgabe, eltern, fortschritt=None, fertig=None, fehler=None):
    faden = QThread(eltern)
    arbeiter = DruckArbeiter(aufgabe)
    arbeiter.moveToThread(faden)
    bote = _Bote(eltern, fortschritt, fertig, fehler)
    arbeiter.fortschritt.connect(bote.fortschritt)
    arbeiter.fertig.connect(bote.fertig)
    arbeiter.fehler.connect(bote.fehler)
    arbeiter.fertig.connect(faden.quit)
    arbeiter.fehler.connect(faden.quit)
    faden.started.connect(arbeiter.laufen)
    faden.start()
    arbeiter._bote = bote          # Python-Referenz halten, wenn eltern None ist
    return faden, arbeiter
