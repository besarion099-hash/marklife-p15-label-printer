# -*- coding: utf-8 -*-
"""Einstellungen des Etikettendruckers.

Liegen als JSON neben dem Programm. Was fehlt, den falschen Typ hat oder
ausserhalb des Erlaubten liegt, faellt still auf die Vorgabe zurueck:
Eine kaputte Einstellungsdatei darf den Start nie verhindern.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, fields
from pathlib import Path

STANDARD_PFAD = Path(__file__).resolve().parent.parent / "einstellungen.json"

_ERLAUBT = {
    "papiertyp": {1, 2, 3},
    "dichte": {1, 2, 3},
    "drehung_grad": {0, 90, 180, 270},
}
_MINDESTENS = {"blockgroesse": 1, "pause_ms": 0}


@dataclass
class Einstellungen:
    port: str = ""
    groesse: str = "40 x 12 mm"   # Rolle des Nutzers (P15)
    eigene_breite_mm: float = 40.0
    eigene_hoehe_mm: float = 12.0
    papiertyp: int = 2          # 1 Endlos, 2 Etikett mit Luecke, 3 schwarze Marke
    dichte: int = 2             # 1 hell, 2 normal, 3 dunkel
    drehung_grad: int = 270     # im Uhrzeigersinn vor dem Senden; am P15 bestaetigt
    versatz_mm: float = 3.9     # weisser Vorlauf vor dem Etikett; P15 druckt 3,9 mm zu frueh
    blockgroesse: int = 512
    pause_ms: int = 20
    letzter_ordner: str = ""


def _passend(wert, vorgabe):
    """Den Wert in den Typ der Vorgabe bringen, oder None, wenn er nicht passt."""
    if isinstance(wert, bool):
        return None
    if isinstance(vorgabe, float):
        return float(wert) if isinstance(wert, (int, float)) else None
    if isinstance(vorgabe, int):
        return wert if isinstance(wert, int) else None
    if isinstance(vorgabe, str):
        return wert if isinstance(wert, str) else None
    return None


def laden(pfad: Path = STANDARD_PFAD) -> Einstellungen:
    try:
        roh = json.loads(Path(pfad).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return Einstellungen()
    if not isinstance(roh, dict):
        return Einstellungen()
    vorgaben = Einstellungen()
    werte = {}
    for feld in fields(Einstellungen):
        if feld.name not in roh:
            continue
        wert = _passend(roh[feld.name], getattr(vorgaben, feld.name))
        if wert is None:
            continue
        if feld.name in _ERLAUBT and wert not in _ERLAUBT[feld.name]:
            continue
        if feld.name in _MINDESTENS and wert < _MINDESTENS[feld.name]:
            continue
        werte[feld.name] = wert
    return Einstellungen(**werte)


def speichern(einstellungen: Einstellungen, pfad: Path = STANDARD_PFAD) -> None:
    pfad = Path(pfad)
    zwischen = pfad.with_suffix(".tmp")
    zwischen.write_text(json.dumps(asdict(einstellungen), indent=2, ensure_ascii=False),
                        encoding="utf-8")
    os.replace(zwischen, pfad)
