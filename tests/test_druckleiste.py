# -*- coding: utf-8 -*-
from hilfen import warten
from kern.anschluss import Port
from kern.druck import DruckFehler
from kern.einstellungen import Einstellungen

P15 = Port("COM13", "P15_ZF39F (COM13)", True)


def _leiste(einstellungen=None, gefunden=(P15,)):
    from gui.druckleiste import Druckleiste
    return Druckleiste(einstellungen or Einstellungen(), lambda: list(gefunden))


def test_port_wird_gewaehlt_und_knopf_aktiv(qapp):
    leiste = _leiste()
    assert leiste.port.currentData() == "COM13"
    assert leiste.knopf.isEnabled()


def test_ohne_drucker_bleibt_knopf_grau(qapp):
    leiste = _leiste(gefunden=())
    assert not leiste.knopf.isEnabled()
    assert "Kein Drucker gefunden" in leiste.port.currentText()


def test_gespeicherter_port_der_fehlt(qapp):
    leiste = _leiste(Einstellungen(port="COM7"))
    assert leiste.port.currentData() == "COM13"


def test_groessen(qapp):
    leiste = _leiste()
    leiste.groesse.setCurrentText("40 x 12 mm")
    assert leiste.groesse_mm() == (40.0, 12.0)
    leiste.setze_groesse(33.0, 11.0)
    assert leiste.groesse.currentText() == "Eigene Größe"
    assert leiste.groesse_mm() == (33.0, 11.0)
    leiste.setze_groesse(50.0, 15.0)
    assert leiste.groesse.currentText() == "50 x 15 mm"


def test_uebernehmen(qapp):
    einstellungen = Einstellungen()
    leiste = _leiste(einstellungen)
    leiste.papier.setCurrentIndex(leiste.papier.findData(1))
    leiste.dichte.setCurrentIndex(leiste.dichte.findData(3))
    leiste.uebernehmen()
    assert (einstellungen.port, einstellungen.papiertyp, einstellungen.dichte) == ("COM13", 1, 3)


def test_druckt_sperrt_knopf(qapp):
    leiste = _leiste()
    leiste.setze_druckt(True)
    assert not leiste.knopf.isEnabled()
    leiste.setze_druckt(False)
    assert leiste.knopf.isEnabled()


def test_arbeiter_direkt(qapp):
    from gui.arbeiter import DruckArbeiter
    stand, fertig = [], []
    arbeiter = DruckArbeiter(lambda fort, ab: (fort(1, 2), fort(2, 2), 2)[-1])
    arbeiter.fortschritt.connect(lambda a, g: stand.append((a, g)))
    arbeiter.fertig.connect(fertig.append)
    arbeiter.laufen()
    assert stand == [(1, 2), (2, 2)] and fertig == [2]


def test_arbeiter_meldet_druckfehler(qapp):
    from gui.arbeiter import DruckArbeiter

    def kaputt(fort, ab):
        raise DruckFehler("abgerissen", 3)

    fehler = []
    arbeiter = DruckArbeiter(kaputt)
    arbeiter.fehler.connect(lambda m, n: fehler.append((m, n)))
    arbeiter.laufen()
    assert fehler == [("abgerissen", 3)]


def test_im_hintergrund(qapp):
    from gui.arbeiter import im_hintergrund
    fertig = []
    faden, _ = im_hintergrund(lambda fort, ab: 5, None, fertig=fertig.append)
    warten(qapp, lambda: fertig != [])
    faden.wait(2000)
    assert fertig == [5]
