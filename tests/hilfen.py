# -*- coding: utf-8 -*-
"""Gemeinsame Testhilfen: eine Verbindung ohne Drucker, Warten auf Qt."""

import time

from kern import anschluss


class FalscheVerbindung:
    """Steht fuer anschluss.Verbindung: aufrufen mit dem Portnamen, dann with."""

    def __init__(self, kaputt_ab=None):
        self.gesendet = []
        self.kaputt_ab = kaputt_ab
        self.port = None

    def __call__(self, port):
        self.port = port
        return self

    def __enter__(self):
        return self

    def __exit__(self, *ausnahme):
        return False

    def schreiben(self, daten, blockgroesse=512, pause_ms=20, fortschritt=None):
        if self.kaputt_ab is not None and len(self.gesendet) >= self.kaputt_ab:
            raise anschluss.AnschlussFehler("Die Verbindung zu COM13 ist abgerissen: Test")
        self.gesendet.append(bytes(daten))


def warten(app, bedingung, sekunden=10.0):
    ende = time.monotonic() + sekunden
    while not bedingung():
        if time.monotonic() > ende:
            raise AssertionError("Zeitüberschreitung beim Warten")
        app.processEvents()
        time.sleep(0.01)
    app.processEvents()
