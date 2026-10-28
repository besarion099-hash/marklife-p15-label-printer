# -*- coding: utf-8 -*-
"""Platzhalter {{Spaltenname}} in Text, QR-Code und Barcode.

Ein Platzhalter ohne Wert bleibt sichtbar stehen. So faellt ein
Tippfehler in der Vorschau auf, bevor Etiketten verbraucht sind.
"""

from __future__ import annotations

import re

MUSTER = re.compile(r"\{\{\s*([^{}]+?)\s*\}\}")


def namen(text: str) -> list[str]:
    return [treffer.group(1) for treffer in MUSTER.finditer(text or "")]


def ersetzen(text: str, werte) -> str:
    if not werte:
        return text

    def einsetzen(treffer):
        name = treffer.group(1)
        return werte[name] if name in werte else treffer.group(0)

    return MUSTER.sub(einsetzen, text)


def fehlende(etikett, spalten) -> list[str]:
    vorhanden = set(spalten)
    gesucht = set()
    for element in etikett.elemente:
        gesucht.update(namen(getattr(element, "inhalt", "")))
    return sorted(gesucht - vorhanden)
