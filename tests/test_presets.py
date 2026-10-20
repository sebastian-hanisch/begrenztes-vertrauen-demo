"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, jedes Preset zeigt, wofür es benannt ist."""

import dataclasses

import bvt_algorithm as A
import bvt_constants as C
import bvt_evaluation as ev
import bvt_presets as P


def _settings(name):
    return ev.Settings(**C.PRESETS[name])


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_slider_bounds():
    for name, p in C.PRESETS.items():
        assert p["netztyp"] in C.ALL_TYPES and C.N_MIN <= p["n"] <= C.N_MAX and C.C_MIN <= p["c"] <= C.C_MAX and 0 <= p["seed"] <= C.SEED_MAX, name
        assert C.EPS_MIN <= p["eps"] <= C.EPS_MAX and p["mode"] in C.MODES, name


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS[C.DEFAULT_PRESET_NAME]) == ev.Settings()
    assert next(iter(C.PRESETS)) == C.DEFAULT_PRESET_NAME


def test_setting_specs_cover_every_preset_key_and_defaults_match():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)
    for key, state_key in P.PRESET_KEYS.items():
        assert P.SETTING_SPECS[state_key].default == C.PRESETS[C.DEFAULT_PRESET_NAME][key], key


def test_every_preset_differs_from_the_default_in_something_besides_the_network_type():
    default = C.PRESETS[C.DEFAULT_PRESET_NAME]
    for name, p in C.PRESETS.items():
        if name != C.DEFAULT_PRESET_NAME:
            assert any(p[k] != default[k] for k in p if k != "netztyp"), name


def test_each_preset_shows_what_its_name_says():
    an = {name: ev.analyse(_settings(name)) for name in C.PRESETS}
    stair = an[C.DEFAULT_PRESET_NAME]
    assert stair.inst.typ == C.T_COMPLETE and stair.camps[0] == 2 and stair.camps[2] == 0 and not stair.consensus and stair.run["first_reversal"] is None
    thin = an["Dünnes Netz: ein Block und viele Splitter"]
    assert thin.camps[0] == 1 and 0.9 < thin.camps[1] < C.CONSENSUS_SHARE and thin.camps[2] >= 3 and thin.camps[3] >= 5
    back = an["Gleichabständig: der Konsens kehrt zurück"]
    assert back.consensus and back.settings.mode == C.M_EQUI and back.inst.typ == C.T_COMPLETE
    above = ev.analyse(dataclasses.replace(back.settings, eps=back.settings.eps + 1))
    assert not above.consensus and above.camps[0] == 2                                              # ein Prozentpunkt mehr Vertrauen: wieder zwei Lager
    camps = an["Zwei Lager bleiben"]
    assert camps.inst.typ == C.T_COMPLETE and camps.camps[0] == 2 and camps.camps[2] == 0 and abs(camps.camps[1] - 0.5) < 0.01 and camps.settings.mode == C.M_CAMPS
    comm = an["Verbünde halten Lager"]
    assert comm.inst.typ == C.T_COMMUNITIES and comm.camps[0] == C.BLOCKS and comm.camps[2] == 0 and comm.settings.mode == C.M_COMM
    order = an["Reihenfolge kehrt sich um"]
    assert order.inst.typ != C.T_COMPLETE and order.run["first_reversal"] is not None


def test_every_preset_runs_and_the_verdict_is_a_known_kind():
    for name in C.PRESETS:
        an = ev.analyse(_settings(name))
        kind, text = ev.verdict_main(an)
        assert kind in ("success", "info", "warning") and text and an.run["converged"]
        assert set(an.run["frames"]) >= {0, an.steps} and all(len(x) == an.m for x in an.run["frames"].values())
        assert abs(A.step(an.a, an.run["x"], an.eps) - an.run["x"]).max() < 1e-11                    # der Endzustand ist ein Fixpunkt
