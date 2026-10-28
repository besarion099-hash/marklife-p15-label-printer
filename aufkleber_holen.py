# -*- coding: utf-8 -*-
"""Laedt die freie Aufkleber-Sammlung (Tabler Icons 3.50.0, MIT) nach aufkleber/tabler.

Aufruf: venv\\Scripts\\python.exe aufkleber_holen.py   (macht install.bat)
Die Datei wird gegen die Pruefsumme aus der npm-Registry geprueft. Nur die
Linien-Symbole (outline), icons.json und die Lizenz werden ausgepackt.
"""

from __future__ import annotations

import base64
import hashlib
import io
import sys
import tarfile
import urllib.request
from pathlib import Path

ADRESSE = "https://registry.npmjs.org/@tabler/icons/-/icons-3.50.0.tgz"
INTEGRITAET = ("sha512-HflLxyrH1cqC7s7jzQGSjpsTAVIoaf7+/yHjbdM59rJQBMjliibp+LYhDPFxOMcwa1M8"
               "DNpOk6ENzQiWn9a1Dg==")
ZIEL = Path(__file__).resolve().parent / "aufkleber" / "tabler"


def main() -> int:
    if (ZIEL / "icons.json").is_file():
        print("Aufkleber-Sammlung ist schon da.")
        return 0
    print("Lade Tabler Icons 3.50.0 (ca. 5 MB) ...")
    with urllib.request.urlopen(ADRESSE, timeout=120) as antwort:
        daten = antwort.read()
    pruefsumme = "sha512-" + base64.b64encode(hashlib.sha512(daten).digest()).decode("ascii")
    if pruefsumme != INTEGRITAET:
        print("Pruefsumme stimmt nicht - Download verworfen.")
        return 1
    (ZIEL / "outline").mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(daten), mode="r:gz") as archiv:
        for eintrag in archiv.getmembers():
            name = eintrag.name
            if name.startswith("package/icons/outline/") and name.endswith(".svg"):
                ziel = ZIEL / "outline" / Path(name).name
            elif name in ("package/icons.json", "package/LICENSE"):
                ziel = ZIEL / Path(name).name
            else:
                continue
            if eintrag.isfile():
                ziel.write_bytes(archiv.extractfile(eintrag).read())
    print(f"Fertig: {len(list((ZIEL / 'outline').glob('*.svg')))} Aufkleber.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
