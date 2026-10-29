# -*- coding: utf-8 -*-
from pathlib import Path

from kern import orte


def test_quellordner_ist_beides():
    programm, daten = orte.ordner(eingefroren=False)
    assert programm == daten
    assert (programm / "kern" / "orte.py").is_file()


def test_portabel_schreibt_neben_die_exe(tmp_path):
    exe = tmp_path / "Etikettendrucker" / "Etikettendrucker.exe"
    intern = tmp_path / "Etikettendrucker" / "_internal"
    programm, daten = orte.ordner(eingefroren=True, exe=exe, meipass=intern)
    assert programm == intern
    assert daten == Path(tmp_path / "Etikettendrucker").resolve()


def test_eigene_aufkleber_aus_eigenem_ordner(tmp_path):
    from kern import aufkleber as ak
    eigene = tmp_path / "eigene"
    (eigene / "Kueche").mkdir(parents=True)
    (eigene / "Kueche" / "topf.png").write_bytes(b"x")
    alle = ak.katalog(tmp_path / "leer", eigene)
    assert [a.name for a in alle[f"{ak.EIGENE}: Kueche"]] == ["topf"]
