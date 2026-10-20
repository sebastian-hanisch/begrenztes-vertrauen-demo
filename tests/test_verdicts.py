"""Verdikte und Messhilfen an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier."""

import dataclasses
import math

import numpy as np
import pytest

import bvt_algorithm as A
import bvt_constants as C
import bvt_evaluation as ev

NAN = float("nan")


def _an(x_final, eps=20, steps=12, converged=True, first_reversal=None, x0=None, formula=0.375):
    """Analyse mit handgesetztem Endzustand `x_final` auf einem echten kleinen Lauf; Lager, Splitter und Gruppen kommen aus der echten Zählung."""
    real = ev.analyse(ev.Settings(C.T_COMPLETE, C.N_MIN, 4, 3))
    x_final = np.array(x_final, dtype=float)
    m = len(x_final)
    x0 = np.linspace(0.0, 1.0, m) if x0 is None else np.array(x0, dtype=float)
    run = {"steps": steps, "converged": converged, "x": x_final, "frames": {0: x0.tolist()}, "first_reversal": first_reversal}
    return dataclasses.replace(real, nodes=tuple(range(m)), x0=x0, run=run, camps=A.camps(x_final, C.BIG_SHARE), formula=formula, settings=dataclasses.replace(real.settings, eps=eps))


def test_de_pct_sci_helpers():
    assert ev.de(1.26, 1) == "1,3" and ev.de(0.9487, 3) == "0,949" and ev.de(NAN, 2) == "–" and ev.de(None) == "–" and ev.pct(0.1234, 1) == "12,3" and ev.pct(0.5) == "50" and ev.de(-1.0, 3) == "−1,000"
    assert ev.sci(1.1e-11) == "1,1 · 10⁻¹¹" and ev.sci(0) == "0" and ev.sci(2.5e3) == "2,5 · 10³"


def test_main_verdict_two_camps_and_the_reversal_sentence():
    x = [0.5] * 24 + [0.9] * 16
    kind, text = ev.verdict_main(_an(x))
    assert kind == "info" and text == "Nach 12 Schritten steht das Netz bei Vertrauensradius 20 % still: 2 Lager (das größte mit 60,0 % der Betriebe), 2 Gruppen insgesamt."
    kind, text = ev.verdict_main(_an(x, first_reversal=3))
    assert text.endswith("2 Gruppen insgesamt. In Schritt 3 kehrte sich die Reihenfolge der Meinungen zum ersten Mal um.")


def test_main_verdict_one_camp_with_splitters_is_not_a_consensus():
    x = [0.5] * 36 + [0.1, 0.2, 0.3, 0.9]
    kind, text = ev.verdict_main(_an(x))
    assert kind == "info" and text == ("Nach 12 Schritten steht das Netz bei Vertrauensradius 20 % still: 1 Lager (das größte mit 90,0 % der Betriebe) und 4 Betriebe in kleinen Gruppen (Splittern, insgesamt 5 Gruppen).")


def test_main_verdict_consensus_with_and_without_splitters_and_the_degroot_sentence():
    kind, text = ev.verdict_main(_an([0.5] * 40))
    assert kind == "success" and text == "Nach 12 Schritten einigen sich 100,0 % der Betriebe auf 0,500 (Vertrauensradius 20 %: Konsens)."
    x = [0.5] * 198 + [0.1, 0.2]
    kind, text = ev.verdict_main(_an(x))
    assert kind == "success" and text == "Nach 12 Schritten einigen sich 99,0 % der Betriebe auf 0,500 (Vertrauensradius 20 %: Konsens). 2 Betriebe bleiben als Splitter zurück (3 Gruppen insgesamt)."
    big_radius = _an([0.5] * 40, eps=100, x0=np.linspace(0.25, 0.75, 40))
    assert ev.verdict_main(big_radius)[1].endswith("Selbstgewicht: der Endwert ist Σ (d + 1) x / Σ (d + 1) = 0,375.") and "Spanne der Anfangsmeinungen (0,500)" in ev.verdict_main(big_radius)[1]
    equal = _an([0.5] * 40, eps=50, x0=np.linspace(0.25, 0.75, 40))                               # Radius genau gleich der Spanne zählt als „nicht kleiner“
    assert "DeGroot-Mittelung" in ev.verdict_main(equal)[1]
    assert "DeGroot-Mittelung" not in ev.verdict_main(_an([0.5] * 40, eps=49, x0=np.linspace(0.25, 0.75, 40)))[1]


def test_main_verdict_consensus_threshold_is_ninety_nine_percent():
    assert ev.verdict_main(_an([0.5] * 99 + [0.1]))[0] == "success"                                # 99 von 100
    assert ev.verdict_main(_an([0.5] * 98 + [0.1, 0.2]))[0] == "info"                              # 98 von 100


def test_main_verdict_without_camps_step_limit_and_equal_opinions():
    kind, text = ev.verdict_main(_an(list(np.linspace(0.0, 1.0, 40))))
    assert kind == "info" and text == "Nach 12 Schritten steht das Netz bei Vertrauensradius 20 % still, aber ohne Lager: alle 40 Gruppen haben weniger als 5 % der Betriebe."
    kind, text = ev.verdict_main(_an([0.5] * 24 + [0.9] * 16, steps=20000, converged=False))
    assert kind == "warning" and text == "Nach 20000 Schritten (Obergrenze) steht das Netz bei Vertrauensradius 20 % noch nicht still: bisher 2 Gruppen, die größte mit 60 % der Betriebe."
    assert ev.verdict_main(_an([0.3] * 40, x0=np.full(40, 0.3))) == ("info", "Alle 40 Betriebe beginnen mit derselben Meinung (0,30): es gibt nichts abzugleichen.")


# --- E1 bis E4 --------------------------------------------------------------------------------------------------------------------------------


def _srows():
    def row(typ, eps, camps, largest, groups, consensus):
        return {"typ": typ, "eps": eps, "camps": camps, "largest": largest, "groups": groups, "consensus": consensus, "steps": 10.0, "converged": True, "nets": 4}
    return [row(C.T_COMPLETE, 0.1, 4.0, 0.3, 4.0, 0.0), row(C.T_COMPLETE, 0.25, 1.0, 1.0, 1.0, 1.0), row(C.T_RANDOM, 0.1, 3.0, 0.25, 50.0, 0.0), row(C.T_RANDOM, 0.25, 1.0, 0.9, 6.0, 0.25)]


def test_staircase_verdict_names_the_first_consensus_and_the_fragmentation():
    rows = _srows()
    kind, text = ev.verdict_staircase(rows)
    assert kind == "info"
    assert text == ("Konsens (das größte Lager hat mindestens 99 % der Betriebe) gibt es in mindestens der Hälfte der Netze bei Vertrauensradius: „Vollständig (jeder kennt jeden)“ ab 0,25; „Zufallsnetz“ im Raster nicht (bis 0,25). "
                    "Bei ε = 0,10 zerfällt „Zufallsnetz“ im Median in 50 Gruppen (3 Lager, größter Anteil 25 %), der vollständige Graph in 4 (4 Lager).")
    assert ev.first_consensus(rows, C.T_COMPLETE) == 0.25 and ev.first_consensus(rows, C.T_RANDOM) is None and ev.first_consensus(rows, C.T_RANDOM, share=0.25) == 0.25
    assert ev.stair_cell(rows, C.T_RANDOM, 0.1)["groups"] == 50.0 and ev.verdict_staircase([])[0] == "warning"


def test_order_verdict_lists_always_never_and_partial_types():
    res = {"order": [{"typ": "A", "reversed": 4, "runs": 4, "first": 1.0}, {"typ": "B", "reversed": 0, "runs": 4, "first": NAN}, {"typ": "C", "reversed": 2, "runs": 4, "first": 3.0}],
           "identity": [{"typ": "A", "max_dev": 1.1e-11, "runs": 4}, {"typ": "B", "max_dev": 2.0e-12, "runs": 4}], "eps": 0.2}
    assert ev.verdict_order(res) == ("info", "Bei Vertrauensradius 0,20 kehrt sich die Reihenfolge der Meinungen in jedem Lauf um in: „A“; nie in: „B“; teilweise in: „C“ (2 von 4). "
                                              "Für einen Radius über der Spanne weicht der Endwert um höchstens 1,1 · 10⁻¹¹ von der DeGroot-Formel Σ (d + 1) x / Σ (d + 1) ab.")
    none = dict(res, order=[{"typ": "C", "reversed": 2, "runs": 4, "first": 3.0}])
    assert ev.verdict_order(none)[1].startswith("Bei Vertrauensradius 0,20 kehrt sich die Reihenfolge der Meinungen in keinem Netztyp in jedem Lauf um; teilweise in: „C“ (2 von 4).")
    assert ev.verdict_order({})[0] == "warning"


def _lres(consensus, random_p, n=400, runs=12):
    eps = [0.18, 0.19, 0.1925][: len(consensus)]
    return {"n": n, "equi": [{"eps": e, "camps": 1 if c else 2, "largest": 1.0 if c else 0.5, "groups": 1 if c else 2, "consensus": c} for e, c in zip(eps, consensus)],
            "random": [{"eps": 0.2 + 0.01 * i, "p_consensus": p, "mean_camps": 1.0, "runs": runs} for i, p in enumerate(random_p)]}


def test_lorenz_verdict_names_the_comeback_and_the_random_start():
    res = _lres([False, True, False], [0.0, 0.25, 1.0])
    assert ev.comeback_eps(res["equi"]) == [0.19] and ev.biggest_drop(res["random"]) == 0.0
    assert ev.verdict_lorenz(res) == ("info", "Im vollständigen Graphen mit 400 Betrieben gibt es bei gleichabständigem Start Konsens bei ε = 0,1900, obwohl er bei ε = 0,1925 fehlt: der Konsens kehrt bei sinkendem Radius kurz zurück. "
                                              "Bei zufälligem Start (12 Läufe je Radius) steigt der Anteil der Läufe mit Konsens dagegen monoton mit ε.")
    none = _lres([False, False, True], [0.5, 0.25, 1.0])
    assert ev.comeback_eps(none["equi"]) == [] and ev.biggest_drop(none["random"]) == 0.25
    assert ev.verdict_lorenz(none)[1] == ("Im vollständigen Graphen mit 400 Betrieben gibt es bei gleichabständigem Start keinen Radius, bei dem der Konsens bei sinkendem ε zurückkehrt. "
                                          "Bei zufälligem Start (12 Läufe je Radius) sinkt der Anteil der Läufe mit Konsens beim Übergang zum nächstgrößeren Radius höchstens um 25 Prozentpunkte.")
    assert ev.verdict_lorenz({})[0] == "warning" and ev.biggest_drop([]) == 0.0


def test_communities_verdict_compares_low_and_high_inside_share():
    rows = []
    values = {(0.5, 0.1, C.M_RANDOM): 2, (0.99, 0.1, C.M_RANDOM): 8, (0.5, 0.1, C.M_COMM): 4, (0.99, 0.1, C.M_COMM): 6, (0.5, 0.25, C.M_RANDOM): 1, (0.99, 0.25, C.M_RANDOM): 2, (0.5, 0.25, C.M_COMM): 1, (0.99, 0.25, C.M_COMM): 3}
    for (inside, eps, mode), camps in values.items():
        rows.append({"inside": inside, "eps": eps, "mode": mode, "camps": float(camps), "largest": 0.5, "nets": 4})
    assert ev.verdict_communities(rows) == ("info", "Bei Vertrauensradius 0,10 und zufälligem Start hat das Netz bei 50 % Kanten innerhalb der Verbünde 2 Lager, bei 99 % 8; beginnt jeder Verbund bei seiner eigenen Meinung, sind es 4 bzw. 6.")
    assert ev.community_cell(rows, 0.99, 0.25, C.M_COMM)["camps"] == 3.0 and ev.verdict_communities([])[0] == "warning"


# --- Messreihen ---------------------------------------------------------------------------------------------------------------------------------


def test_staircase_rows_shape_monotone_steps_and_consensus_at_a_huge_radius():
    rows = ev.staircase_rows(60, 6, types=(C.T_COMPLETE, C.T_RING), epsilons=(0.1, 0.3, 1.5), seeds=C.LIVE_SEEDS[:2])
    assert [(r["typ"], r["eps"]) for r in rows] == [(t, e) for t in (C.T_COMPLETE, C.T_RING) for e in (0.1, 0.3, 1.5)] and all(r["converged"] and r["nets"] == 2 for r in rows)
    assert ev.stair_cell(rows, C.T_COMPLETE, 1.5)["consensus"] == 1.0 and ev.stair_cell(rows, C.T_RING, 1.5)["consensus"] == 1.0 and ev.stair_cell(rows, C.T_COMPLETE, 1.5)["camps"] == 1.0
    assert ev.stair_cell(rows, C.T_COMPLETE, 0.1)["camps"] > ev.stair_cell(rows, C.T_COMPLETE, 0.3)["camps"]                      # kleiner Radius: mehr Lager


def test_order_rows_complete_graph_never_reverses_and_identity_is_tiny():
    res = ev.order_rows(40, 6, types=(C.T_COMPLETE, C.T_RANDOM), seeds=C.LIVE_SEEDS[:2])
    complete, random = res["order"]
    assert complete["reversed"] == 0 and complete["runs"] == 2 and random["reversed"] == 2 and random["first"] >= 1 and res["eps"] == C.ORDER_EPS
    assert all(r["max_dev"] < 1e-9 and r["runs"] == 2 for r in res["identity"])


def test_lorenz_rows_shape_and_the_comeback_at_the_default_size():
    res = ev.lorenz_rows(n=100, grid=(0.18, 0.19, 0.2, 0.21), random_grid=(0.1, 0.3), runs=3)
    assert res["n"] == 100 and [r["eps"] for r in res["equi"]] == [0.18, 0.19, 0.2, 0.21] and [r["eps"] for r in res["random"]] == [0.1, 0.3]
    assert [r["consensus"] for r in res["equi"]] == [False, True, False, False] and ev.comeback_eps(res["equi"]) == [0.19]          # n = 100: Konsens nur bei 0,19
    assert res["random"][0]["p_consensus"] == 0.0 and res["random"][1]["p_consensus"] == 1.0 and res["random"][0]["runs"] == 3


def test_community_rows_shape_and_the_aligned_start_keeps_the_blocks():
    rows = ev.community_rows(n=120, c=12, insides=(0.8, 0.99), epsilons=(0.1,), seeds=C.LIVE_SEEDS[:2])
    assert [(r["inside"], r["eps"], r["mode"]) for r in rows] == [(i, 0.1, m) for i in (0.8, 0.99) for m in (C.M_RANDOM, C.M_COMM)]
    assert ev.community_cell(rows, 0.8, 0.1, C.M_COMM)["camps"] == C.BLOCKS and all(r["nets"] == 2 for r in rows)


def test_helpers_median_and_rng_are_deterministic():
    assert ev._rng(1, 2).integers(1000) == ev._rng(1, 2).integers(1000) and math.isnan(ev._median([])) and ev._median([3, 1, 2]) == 2.0
