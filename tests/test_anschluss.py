# -*- coding: utf-8 -*-
from types import SimpleNamespace

import pytest

from kern import anschluss

P15 = (r"BTHENUM\{00001101-0000-1000-8000-00805F9B34FB}_VID&000205AC_PID&0239"
       r"\7&2C9806C5&0&55550906F39F_C00000000")
EINGEHEND = (r"BTHENUM\{00001101-0000-1000-8000-00805F9B34FB}_LOCALMFG&0000"
             r"\7&2C9806C5&0&000000000000_00000000")


def test_mac_aus_hwid():
    assert anschluss.mac_aus_hwid(P15) == "55550906f39f"
    assert anschluss.mac_aus_hwid(EINGEHEND) is None
    assert anschluss.mac_aus_hwid("USB VID:PID=1A86:7523") is None


def test_ports_sortiert_und_benannt():
    liste = [
        SimpleNamespace(device="COM3", description="USB-SERIAL CH340",
                        hwid="USB VID:PID=1A86:7523"),
        SimpleNamespace(device="COM5", description="Seriell über Bluetooth", hwid=EINGEHEND),
        SimpleNamespace(device="COM13", description="Seriell über Bluetooth", hwid=P15),
    ]
    gefunden = anschluss.ports(lambda: liste,
                               lambda mac: {"55550906f39f": "P15_ZF39F"}.get(mac))
    assert [p.name for p in gefunden] == ["COM13", "COM3"]
    assert gefunden[0].beschreibung == "P15_ZF39F (COM13)"
    assert gefunden[0].bluetooth and not gefunden[1].bluetooth


def test_drucker_steht_vor_kopfhoerern():
    jbl = (r"BTHENUM\{00001101-0000-1000-8000-00805F9B34FB}_VID&000102B0_PID&0000"
           r"\7&2C9806C5&0&08EBEDB9543F_C00000000")
    liste = [SimpleNamespace(device="COM4", description="Seriell", hwid=jbl),
             SimpleNamespace(device="COM13", description="Seriell", hwid=P15)]
    namen = {"08ebedb9543f": "JBL WAVE BEAM", "55550906f39f": "P15_ZF39F"}
    gefunden = anschluss.ports(lambda: liste, namen.get)
    assert [p.name for p in gefunden] == ["COM13", "COM4"]


def test_ports_ohne_registry_name():
    liste = [SimpleNamespace(device="COM13", description="Seriell über Bluetooth", hwid=P15)]
    gefunden = anschluss.ports(lambda: liste, lambda mac: None)
    assert gefunden[0].beschreibung == "Seriell über Bluetooth (COM13)"


class FalscherPort:
    def __init__(self, kaputt_ab=None):
        self.bloecke = []
        self.zu = False
        self.kaputt_ab = kaputt_ab

    def write(self, block):
        if self.kaputt_ab is not None and len(self.bloecke) >= self.kaputt_ab:
            raise OSError("weg")
        self.bloecke.append(bytes(block))
        return len(block)

    def flush(self):
        pass

    def close(self):
        self.zu = True


def test_schreiben_in_bloecken():
    port = FalscherPort()
    pausen, stand = [], []
    with anschluss.Verbindung("COM13", lambda name: port, schlafen=pausen.append) as v:
        v.schreiben(bytes(1200), blockgroesse=512, pause_ms=20,
                    fortschritt=lambda a, g: stand.append((a, g)))
    assert [len(b) for b in port.bloecke] == [512, 512, 176]
    assert stand == [(512, 1200), (1024, 1200), (1200, 1200)]
    assert pausen == [0.02, 0.02, 0.02, 1.0]    # drei Bloecke, dann Nachlauf
    assert port.zu


def test_oeffnen_scheitert():
    def kaputt(name):
        raise OSError("Zugriff verweigert")
    with pytest.raises(anschluss.AnschlussFehler, match="COM13"):
        with anschluss.Verbindung("COM13", kaputt):
            pass


def test_abriss_beim_schreiben_schliesst_port():
    port = FalscherPort(kaputt_ab=1)
    with pytest.raises(anschluss.AnschlussFehler, match="abgerissen"):
        with anschluss.Verbindung("COM13", lambda name: port, schlafen=lambda s: None) as v:
            v.schreiben(bytes(1000), blockgroesse=512)
    assert port.zu
