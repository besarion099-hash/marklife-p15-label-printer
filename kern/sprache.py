# -*- coding: utf-8 -*-
"""Zweisprachigkeit (Deutsch, Englisch).

Deutsch ist die Quellsprache: Im Code steht der deutsche Text, t() liefert
ihn in der eingestellten Sprache. Platzhalter wie in str.format:

    t("Kopien: {anzahl}", anzahl=3)

Texte, die als Konstante auf Modulebene stehen, werden mit N_() markiert
und erst beim Anzeigen mit t() uebersetzt - die Sprache kann sich zur
Laufzeit aendern. tests/test_sprache.py prueft, dass jeder markierte Text
eine englische Fassung hat.
"""

from __future__ import annotations

import locale

from kern.sprache_en import EN

SPRACHEN = [("de", "Deutsch"), ("en", "English")]
_jetzt = "de"


def setze(code: str) -> None:
    global _jetzt
    _jetzt = code if code in dict(SPRACHEN) else "de"


def aktuell() -> str:
    return _jetzt


def t(quelle: str, /, **werte) -> str:
    if _jetzt == "en":
        quelle = EN.get(quelle, quelle)
    return quelle.format(**werte) if werte else quelle


def N_(text: str) -> str:
    """Markiert einen Text zum Uebersetzen, ohne ihn schon zu uebersetzen."""
    return text


def system_sprache() -> str:
    """"de" bei deutschem Windows, sonst "en" - Vorauswahl beim ersten Start."""
    try:
        import ctypes
        name = locale.windows_locale.get(ctypes.windll.kernel32.GetUserDefaultUILanguage(), "")
    except (AttributeError, OSError):
        name = (locale.getlocale()[0] or "")
    return "de" if name.lower().startswith("de") else "en"
