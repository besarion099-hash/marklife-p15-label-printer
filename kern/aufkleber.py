# -*- coding: utf-8 -*-
"""Aufkleber-Katalog: Kategorien wie in der Marklife-App, Grafiken frei.

Die Aufkleber der Marklife-App liegen zum groessten Teil auf dem Server des
Herstellers und werden nicht kopiert. Stattdessen fuellen die frei nutzbaren
Tabler Icons (MIT-Lizenz, aufkleber/tabler) dieselben Kategorien. Zugeordnet
wird ueber Tablers eigene Kategorie und ueber Namensbestandteile
("crown" in "crown-off" -> Schmuck). Dazu kommen die 29 Aufkleber, die in der
App selbst stecken (aufkleber/marklife), und eigene Grafiken
(aufkleber/eigene, Unterordner werden zu Kategorien).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

STANDARD_ORDNER = Path(__file__).resolve().parent.parent / "aufkleber"
BILDENDUNGEN = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".svg"}

# Reihenfolge und Namen wie in der Marklife-App (Screenshots vom 28.10.2026).
KATEGORIEN = [
    ("Blumenladen-Geschenk", set(), {"flower", "flowers", "gift", "heart", "hearts", "balloon",
                                      "cake", "confetti", "rosette", "sparkles", "christmas",
                                      "candle", "bow"}),
    ("Achten Sie auf die Warnung", set(), {"alert", "exclamation", "ban", "flame", "fire",
                                           "radioactive", "biohazard", "skull", "barrier",
                                           "traffic", "cone", "hazard", "warning", "urgent",
                                           "lock", "hand", "stop"}),
    ("Schmuck", set(), {"diamond", "diamonds", "crown", "jewel", "gem", "ring", "necklace",
                        "bracelet", "earring", "sparkles", "eyeglass", "eyeglass-2",
                        "device-watch", "rosette", "hanger", "umbrella", "bow", "flower",
                        "glasses", "sunglasses"}),
    ("Pflanze", set(), {"plant", "plant-2", "leaf", "leaf-2", "trees", "tree", "flower",
                        "seedling", "cactus", "sprout", "clover", "mushroom", "grain", "pinecone",
                        "acorn", "cherry", "lemon", "apple", "plant-off"}),
    ("Zahlen", {"Numbers"}, set()),
    ("Sport", {"Sport"}, {"ball", "bike", "swimming", "run", "yoga", "trophy", "medal",
                          "barbell", "karate", "tennis", "golf", "skateboard", "ski"}),
    ("Medikamente", set(), {"pill", "pills", "medicine", "vaccine", "vaccine-bottle",
                            "stethoscope", "thermometer", "bandage", "heartbeat",
                            "first-aid-kit", "dental", "virus", "nurse", "medical-cross",
                            "prescription", "emergency-bed", "wheelchair", "massage",
                            "activity-heartbeat", "heart-rate-monitor", "dna", "microscope"}),
    ("Kleideraufbewahrung", {"Laundry"}, {"shirt", "hanger", "jacket", "hat", "tie",
                                          "ironing", "needle", "wash", "sock", "hood"}),
    ("Schuh", set(), {"shoe", "shoes", "sneaker", "boot", "boots", "heels", "shoe-off"}),
    ("Kommunikationsstärke", {"Communication"}, set()),
    ("Wetter", {"Weather"}, set()),
    ("Mathematik", {"Math"}, set()),
    ("digitale Geräte", {"Devices", "Computers"}, set()),
    ("Supermarkt", {"E-commerce", "Food"}, set()),
    ("Marke", {"Brand"}, set()),
    ("Baby Produkte", set(), {"baby", "carriage", "stroller", "teddy", "toy", "pacifier",
                              "diaper", "kid", "bottle", "rattle", "horse"}),
    ("Mutter und Kind", set(), {"woman", "girl", "kid", "baby", "family", "friends",
                                "mood-kid", "heart-handshake", "home-heart", "users"}),
]
MARKLIFE = "Marklife"
EIGENE = "Meine Aufkleber"


@dataclass(frozen=True)
class Aufkleber:
    name: str
    pfad: Path
    stichworte: tuple = field(default=())

    def passt(self, suche: str) -> bool:
        suche = suche.strip().lower()
        return (not suche or suche in self.name.lower()
                or any(suche in wort.lower() for wort in self.stichworte))


# Endungen, die nur eine Abwandlung des Grundsymbols sind (durchgestrichen, mit
# Haken, mit Zahnrad ...). Sie blaehen den Katalog auf, ohne neue Motive zu bringen.
ABWANDLUNGEN = {"off", "bolt", "cancel", "check", "code", "cog", "dollar", "down", "up",
                "minus", "plus", "pause", "pin", "question", "search", "share", "star", "x",
                "edit", "exclamation", "heart", "spark", "shield", "dots", "bitcoin",
                "filled", "time", "upload", "download", "lock", "settings"}


STOERTEILE = {"number", "discount", "percentage", "broken", "asterisk", "rate", "dollar",
              "euro", "minus", "plus"}


def _passt_zu(eintrag: dict, tabler_kategorien: set, woerter: set) -> bool:
    name = eintrag["name"]
    teile = name.split("-")
    if name in woerter:
        return True                                  # ausdruecklich gewuenscht
    if len(teile) > 1 and teile[-1] in ABWANDLUNGEN:
        return False
    if eintrag.get("category") in tabler_kategorien:
        return True
    # Zahlen-Rosetten, Rabatt- und Prozent-Zeichen gehoeren nicht in Motiv-Kategorien
    # ("rosette-number-3" ist kein Geschenk, "heart-broken" kein Blumengruss).
    if set(teile[1:]) & STOERTEILE:
        return False
    # Stichwort muss das Motiv sein (erster Namensteil), nicht ein Zusatz:
    # "crown" ja, "basket-heart" nein.
    return teile[0] in woerter or any(name.startswith(w + "-") for w in woerter if "-" in w)


def tabler_katalog(ordner: Path) -> dict:
    """Die App-Kategorien, gefuellt aus Tabler Icons (outline)."""
    metadaten = ordner / "icons.json"
    if not metadaten.is_file():
        return {}
    eintraege = json.loads(metadaten.read_text(encoding="utf-8")).values()
    # Den Ordner einmal auflisten statt jede Datei einzeln zu pruefen: 17
    # Kategorien x 5203 Dateien kosteten unter Windows sonst ~26 s.
    vorhanden = {pfad.stem: pfad for pfad in (ordner / "outline").glob("*.svg")}
    katalog = {name: [] for name, _, _ in KATEGORIEN}
    for eintrag in eintraege:
        pfad = vorhanden.get(eintrag["name"])
        if pfad is None or "outline" not in eintrag.get("styles", {}):
            continue
        aufkleber = None
        for name, tabler_kategorien, woerter in KATEGORIEN:
            if _passt_zu(eintrag, tabler_kategorien, woerter):
                aufkleber = aufkleber or Aufkleber(
                    eintrag["name"], pfad, tuple(str(t) for t in eintrag.get("tags", ())))
                katalog[name].append(aufkleber)
    return {name: sorted(liste, key=lambda a: a.name)
            for name, liste in katalog.items() if liste}


def ordner_katalog(ordner: Path, standardname: str) -> dict:
    """Bilder eines Ordners; Unterordner werden zu eigenen Kategorien."""
    katalog = {}
    if not ordner.is_dir():
        return katalog
    for pfad in sorted(ordner.rglob("*")):
        if pfad.suffix.lower() not in BILDENDUNGEN or not pfad.is_file():
            continue
        unter = pfad.parent.relative_to(ordner).parts
        kategorie = unter[0] if unter else standardname
        katalog.setdefault(kategorie, []).append(Aufkleber(pfad.stem, pfad))
    return katalog


def katalog(wurzel: Path = STANDARD_ORDNER) -> dict:
    """Alle Kategorien in der Reihenfolge der App, dann Marklife und eigene."""
    gesamt = dict(tabler_katalog(wurzel / "tabler"))
    marklife = ordner_katalog(wurzel / "marklife", MARKLIFE)
    if marklife:
        gesamt[MARKLIFE] = [a for liste in marklife.values() for a in liste]
    for name, liste in ordner_katalog(wurzel / "eigene", EIGENE).items():
        gesamt[name if name == EIGENE else f"{EIGENE}: {name}"] = liste
    return gesamt


def suchen(alle: dict, suche: str) -> list:
    """Treffer ueber alle Kategorien, jeder Aufkleber nur einmal."""
    gesehen, treffer = set(), []
    for liste in alle.values():
        for aufkleber in liste:
            if aufkleber.pfad not in gesehen and aufkleber.passt(suche):
                gesehen.add(aufkleber.pfad)
                treffer.append(aufkleber)
    return treffer
