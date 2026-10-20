"""End-to-end Smoke-Test via Streamlits offiziellem AppTest-Framework: lädt app.py mit den Standardeinstellungen, klickt jeden Button, fährt jeden Slider an seine Grenzen,
prüft Permalink, Netztypen, Modi, den Schritt-Regler und alle vier Experimente; es darf kein Python-Fehler auftreten."""

import os

import pytest
from streamlit.testing.v1 import AppTest

import bvt_constants as C

APP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))  # unter Last reichen 180 s nicht immer; Umgebungsvariable zum Anpassen
EXPERIMENTS = ("staircase", "order", "lorenz", "communities")


def _fresh_app() -> AppTest:
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _metric(at, label):
    return next(m.value for m in at.metric if m.label == label)


def test_app_loads_without_exception():
    at = _fresh_app()
    assert [m.label for m in at.metric] == ["Lager", "Größtes Lager", "Splitter", "Gruppen", "Schritte"]
    assert _metric(at, "Lager") == "2" and _metric(at, "Größtes Lager") == "62 %" and _metric(at, "Splitter") == "0" and _metric(at, "Gruppen") == "2" and _metric(at, "Schritte") == "4"
    assert not at.error and not at.warning
    assert any(i.value.startswith("Nach 4 Schritten steht das Netz bei Vertrauensradius 20 % still: 2 Lager") for i in at.info)


def test_every_preset_click_does_not_raise():
    for name in C.PRESETS:
        at = _fresh_app()
        at.sidebar.button(key=f"preset_{name}").click().run(timeout=TIMEOUT)
        assert not at.exception, (name, [str(e) for e in at.exception])


def test_the_presets_show_their_numbers():
    at = _fresh_app()
    at.sidebar.button(key="preset_Dünnes Netz: ein Block und viele Splitter").click().run(timeout=TIMEOUT)
    assert [_metric(at, k) for k in ("Lager", "Größtes Lager", "Splitter", "Gruppen")] == ["1", "96 %", "6", "7"]
    at.sidebar.button(key="preset_Gleichabständig: der Konsens kehrt zurück").click().run(timeout=TIMEOUT)
    assert _metric(at, "Lager") == "1" and _metric(at, "Größtes Lager") == "100 %" and any("Konsens" in s.value for s in at.success)
    at.sidebar.button(key="preset_Verbünde halten Lager").click().run(timeout=TIMEOUT)
    assert _metric(at, "Lager") == "6" and _metric(at, "Splitter") == "0"


def test_every_slider_at_its_min_and_max_does_not_raise():
    labels = [s.label for s in _fresh_app().sidebar.slider]
    assert labels == ["Betriebe n", "Partner je Betrieb c", "Vertrauensradius ε (%)"], labels
    for index in range(len(labels)):
        for edge in ("min", "max"):
            at = _fresh_app()
            slider = at.sidebar.slider[index]
            value = slider.min if edge == "min" else slider.max
            slider.set_value(int(value)).run(timeout=TIMEOUT)
            assert not at.exception, (labels[index], edge, [str(e) for e in at.exception])


def test_all_sliders_at_their_minimum_and_all_at_their_maximum_do_not_raise():
    for edge in ("min", "max"):
        at = _fresh_app()
        for index in range(len(at.sidebar.slider)):
            slider = at.sidebar.slider[index]
            slider.set_value(int(slider.min if edge == "min" else slider.max))
        at.run(timeout=TIMEOUT)
        assert not at.exception, (edge, [str(e) for e in at.exception])


@pytest.mark.parametrize("typ", C.ALL_TYPES)
def test_every_network_type_renders(typ):
    at = _fresh_app()
    at.selectbox(key="netztyp_select").set_value(typ).run(timeout=TIMEOUT)
    assert not at.exception, (typ, [str(e) for e in at.exception])


@pytest.mark.parametrize("mode", C.MODES)
def test_every_initial_distribution_renders(mode):
    at = _fresh_app()
    at.selectbox(key="mode_select").set_value(mode).run(timeout=TIMEOUT)
    assert not at.exception, (mode, [str(e) for e in at.exception])


def test_the_step_slider_moves_through_the_frames_and_resets_with_the_settings():
    at = _fresh_app()
    slider = at.select_slider[0]
    last = int(slider.options[-1])
    assert slider.label == "Schritt" and slider.value == 0 and last == 4
    slider.set_value(last).run(timeout=TIMEOUT)
    assert not at.exception and at.select_slider[0].value == last
    at.sidebar.slider(key="eps_slider").set_value(15).run(timeout=TIMEOUT)
    assert not at.exception and at.select_slider[0].value == 0                                       # neue Einstellungen: neuer Regler, zurück auf Schritt 0


def test_a_new_run_changes_the_seed_and_the_result():
    at = _fresh_app()
    before = at.number_input(key="seed_input").value
    at.button[[b.label for b in at.button].index("🎲 Neuer Lauf")].click().run(timeout=TIMEOUT)
    assert not at.exception and at.number_input(key="seed_input").value != before


def test_permalink_values_are_clamped_and_unknown_choices_ignored():
    at = AppTest.from_file(APP_PATH)
    at.query_params["n"] = "5"
    at.query_params["c"] = "99"
    at.query_params["radius"] = "999"
    at.query_params["start"] = "gibt es nicht"
    at.query_params["typ"] = "gibt es nicht"
    at.run(timeout=TIMEOUT)
    assert not at.exception
    assert at.slider(key="n_slider").value == C.N_MIN and at.slider(key="c_slider").value == C.C_MAX and at.slider(key="eps_slider").value == C.EPS_MAX
    assert at.selectbox(key="mode_select").value == C.DEFAULT_MODE and at.selectbox(key="netztyp_select").value == C.T_COMPLETE


def test_permalink_selects_type_and_mode_and_the_address_mirrors_the_settings():
    at = AppTest.from_file(APP_PATH)
    at.query_params["typ"] = C.T_GRID
    at.query_params["start"] = C.M_EQUI
    at.query_params["radius"] = "30"
    at.run(timeout=TIMEOUT)
    assert not at.exception and at.selectbox(key="netztyp_select").value == C.T_GRID and at.selectbox(key="mode_select").value == C.M_EQUI and at.slider(key="eps_slider").value == 30
    assert dict(at.query_params) == {"typ": C.T_GRID, "n": "100", "c": "6", "seed": "35", "radius": "30", "start": C.M_EQUI}


def test_every_experiment_runs_and_is_invalidated_by_a_setting_change():
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=TIMEOUT)
    at.sidebar.slider(key="n_slider").set_value(C.N_MIN).run(timeout=TIMEOUT)         # kleines Netz: schnell
    for name in EXPERIMENTS:
        at.button(key=f"run_{name}").click().run(timeout=TIMEOUT)
        assert not at.exception, (name, [str(e) for e in at.exception])
    texts = " ".join(x.value for x in list(at.info) + list(at.warning) + list(at.success))
    for fragment in ("Konsens (das größte Lager hat mindestens 99 % der Betriebe) gibt es", "kehrt sich die Reihenfolge der Meinungen", "Im vollständigen Graphen mit 400 Betrieben", "Bei Vertrauensradius 0,10 und zufälligem Start"):
        assert fragment in texts, fragment
    at.sidebar.slider(key="n_slider").set_value(C.N_MIN + 10).run(timeout=TIMEOUT)
    assert not at.exception
    assert sum("neu starten" in i.value for i in at.info) == 2                                    # Experiment 1 und 2 hängen an n; 3 und 4 an nichts
