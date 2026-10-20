"""Einheiten des Kerns an Mini-Instanzen mit von Hand gerechneten Werten (DEMO-PLAYBOOK §1b)."""

import numpy as np
import pytest

import bvt_algorithm as A
import bvt_constants as C
from conftest import make_matrix

# --- Netze --------------------------------------------------------------------------------------------------------------------------------------


def test_complete_matrix_and_adjacency_helpers(path3):
    assert A.complete_matrix(3).tolist() == [[0, 1, 1], [1, 0, 1], [1, 1, 0]] and A.complete_matrix(1).tolist() == [[0.0]]
    assert A.matrix_to_adj(path3) == ((1,), (0, 2), (1,))


def test_largest_component_and_induced_matrix():
    adj = ((1,), (0, 2), (1,), (4,), (3,), ())
    assert A.largest_component(adj) == [0, 1, 2] and A.largest_component(((1,), (0,), (3,), (2,))) == [0, 1] and A.largest_component(()) == []
    assert A.induced_matrix(adj, [2, 1, 0]).tolist() == [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
    assert A.induced_matrix(adj, [3, 4]).tolist() == [[0, 1], [1, 0]]


def test_sbm_matrix_is_symmetric_deterministic_and_has_the_inside_share():
    a, lab = A.sbm_matrix(240, 6, 6, 0.9, 5)
    assert np.array_equal(a, a.T) and np.trace(a) == 0 and np.array_equal(a, A.sbm_matrix(240, 6, 6, 0.9, 5)[0]) and not np.array_equal(a, A.sbm_matrix(240, 6, 6, 0.9, 6)[0])
    inner = sum(a[i, j] for i in range(240) for j in range(i + 1, 240) if lab[i] == lab[j])
    assert inner / (a.sum() / 2) == pytest.approx(0.9, abs=0.05) and np.bincount(lab).tolist() == [40] * 6
    assert A.sbm_matrix(6, 6, 3, 0.5, 1)[0].shape == (6, 6)                                     # Gruppen der Größe 1: keine Paare innen


# --- Schritt ------------------------------------------------------------------------------------------------------------------------------------


def test_step_by_hand_on_the_path_and_the_triangle(path3, tri):
    assert A.step(path3, [0.0, 0.4, 1.0], 0.5).tolist() == pytest.approx([0.2, 0.2, 1.0])        # Betrieb 2 findet im Radius 0,5 niemanden
    assert A.step(tri, [0.0, 0.1, 0.8], 0.5).tolist() == pytest.approx([0.05, 0.05, 0.8])
    assert A.step(path3, [0.0, 0.3, 0.9], 1.0).tolist() == pytest.approx([0.15, 0.4, 0.6])       # ε größer als die Spanne: Mittel über sich und alle Partner
    assert A.step(path3, [0.2, 0.5, 0.8], 0.0).tolist() == pytest.approx([0.2, 0.5, 0.8])        # ε = 0: jeder bleibt bei sich


def test_step_trusts_exactly_at_the_boundary():
    pair = make_matrix(2, [(0, 1)])
    assert A.step(pair, [0.25, 0.75], 0.5).tolist() == [0.5, 0.5]                                  # Abstand genau ε: vertraut
    assert A.step(pair, [0.25, 0.75], 0.4999).tolist() == [0.25, 0.75]


def test_step_does_not_change_its_input(path3):
    x = np.array([0.0, 0.4, 1.0])
    A.step(path3, x, 0.5)
    assert x.tolist() == [0.0, 0.4, 1.0]


# --- Lauf ---------------------------------------------------------------------------------------------------------------------------------------


def test_run_reaches_the_two_camps_of_the_path_and_counts_the_steps(path3):
    out = A.run(path3, [0.0, 0.4, 1.0], 0.5, C.TOL, 100)
    assert out["converged"] and out["steps"] == 1 and out["x"].tolist() == pytest.approx([0.2, 0.2, 1.0]) and out["first_reversal"] is None
    assert A.group_sizes(out["x"]) == [2, 1] and out["frames"][1].tolist() == out["x"].tolist()


def test_run_of_the_triangle_stops_after_one_step_and_equal_opinions_stop_at_once(tri):
    out = A.run(tri, [0.0, 0.1, 0.8], 0.5, C.TOL, 100)
    assert out["steps"] == 1 and out["x"].tolist() == pytest.approx([0.05, 0.05, 0.8])
    flat = A.run(tri, [0.3, 0.3, 0.3], 0.5, C.TOL, 100)
    assert flat["steps"] == 0 and flat["converged"] and flat["x"].tolist() == [0.3, 0.3, 0.3] and set(flat["frames"]) == {0}


def test_run_detects_the_first_reversal_of_the_order_on_a_path(path3):
    out = A.run(path3, [0.0, 0.5, 0.4], 1.0, C.TOL, 100)
    assert out["first_reversal"] == 1                                                              # (0; 0,5; 0,4) → (0,25; 0,3; 0,45): Betrieb 1 und 2 haben die Plätze getauscht


def test_run_stops_at_the_step_limit_and_keeps_the_wanted_frames():
    n = 30
    chain = make_matrix(n, [(i, i + 1) for i in range(n - 1)])
    out = A.run(chain, np.linspace(0, 1, n), 1.0, C.TOL, 2, frames=[0, 1])
    assert out["steps"] == 2 and not out["converged"] and set(out["frames"]) == {0, 1, 2} and out["frames"][0].tolist() == pytest.approx(np.linspace(0, 1, n).tolist())


def test_run_with_a_huge_radius_is_the_degroot_average_with_self_weight(path3):
    out = A.run(path3, [0.0, 0.3, 0.9], 2.0, 1e-14, 100_000)
    assert out["converged"] and out["x"].tolist() == pytest.approx([2.7 / 7] * 3, abs=1e-12) and A.consensus_formula(path3, [0.0, 0.3, 0.9]) == pytest.approx(2.7 / 7)


def test_frame_schedule_is_sorted_unique_and_bounded():
    sched = A.frame_schedule(5000, 120)
    assert sched == sorted(set(sched)) and sched[0] == 0 and sched[1] == 1 and sched[-1] == 5000 and len(sched) <= 125
    assert A.frame_schedule(0, 10) == [0] and A.frame_schedule(3, 120) == [0, 1, 2, 3]


# --- Lager --------------------------------------------------------------------------------------------------------------------------------------


def test_groups_labels_and_camps_by_hand():
    x = [0.0, 0.0, 0.5, 1.0, 1.0, 1.0]
    assert A.group_sizes(x) == [2, 1, 3] and A.group_labels(x).tolist() == [0, 0, 1, 2, 2, 2]
    assert A.camps(x, share=0.3) == (2, 0.5, 1, 3)                                                  # Lager ab 1,8 Betrieben: 2 und 3; ein Splitter
    assert A.camps([0.0, 1e-7, 2e-7], share=0.05)[0] == 1 and A.camps([0.0, 2e-6], share=0.05)[3] == 2     # Abstand unter 10⁻⁶ gehört zusammen
    assert A.group_labels([0.9, 0.1, 0.5]).tolist() == [2, 0, 1] and A.group_sizes([0.7]) == [1]


def test_camps_threshold_is_inclusive():
    x = [0.0] * 5 + [1.0] * 95
    assert A.camps(x, share=0.05)[0] == 2 and A.camps(x, share=0.0501)[0] == 1


def test_consensus_formula_by_hand(path3, tri):
    assert A.consensus_formula(path3, [0.0, 0.3, 0.9]) == pytest.approx(2.7 / 7)
    assert A.consensus_formula(tri, [0.0, 0.3, 0.9]) == pytest.approx(0.4)                          # alle haben Grad 2: einfacher Mittelwert


# --- Anfangsverteilungen --------------------------------------------------------------------------------------------------------------------------


def test_initial_opinions_by_mode():
    rng = np.random.default_rng(3)
    r = A.initial_opinions(C.M_RANDOM, 50, rng)
    assert r.shape == (50,) and 0.0 <= r.min() and r.max() <= 1.0 and A.initial_opinions(C.M_RANDOM, 50, np.random.default_rng(3)).tolist() == r.tolist()
    e = A.initial_opinions(C.M_EQUI, 50, rng)
    assert np.sort(e).tolist() == pytest.approx(np.linspace(0, 1, 50).tolist()) and not np.array_equal(e, np.sort(e))
    c = A.initial_opinions(C.M_COMM, 60, rng)
    assert c.shape == (60,) and abs(c[:10].mean() - 1 / 12) < 0.05 and abs(c[-10:].mean() - 11 / 12) < 0.05
    lab = np.array([0, 1] * 30)
    assert abs(A.initial_opinions(C.M_COMM, 60, rng, labels=lab, blocks=6)[lab == 1].mean() - 1.5 / 6) < 0.03
    k = A.initial_opinions(C.M_CAMPS, 60, rng)
    assert (k < 0.5).sum() == 30 and abs(k[k < 0.5].mean() - 0.25) < 0.05 and abs(k[k >= 0.5].mean() - 0.75) < 0.05
    with pytest.raises(ValueError):
        A.initial_opinions("unbekannt", 5, rng)


# --- Lücken der Mutationsprüfung -----------------------------------------------------------------------------------------------------------------


def test_group_gap_is_inclusive_distance_exactly_at_the_gap_stays_together():
    assert A.group_sizes([0.0, 1e-6]) == [2] and A.group_labels([0.0, 1e-6]).tolist() == [0, 0]            # Abstand genau 10⁻⁶: dieselbe Gruppe
    assert A.group_sizes([0.0, 1.1e-6]) == [1, 1] and A.group_labels([0.0, 1.1e-6]).tolist() == [0, 1]
    assert A.group_sizes([0.0, 0.5, 0.5 + 2e-6], gap=3e-6) == [1, 2] and A.group_sizes([0.0, 0.5, 0.5 + 2e-6], gap=1e-6) == [1, 1, 1]


def test_noise_of_the_aligned_and_the_camp_start_is_added_not_subtracted():
    n = 60
    lab = np.arange(n) * 6 // n
    expected = np.clip((lab + 0.5) / 6 + 0.04 * np.random.default_rng(5).standard_normal(n), 0.0, 1.0)
    assert A.initial_opinions(C.M_COMM, n, np.random.default_rng(5)).tolist() == expected.tolist()
    rng = np.random.default_rng(5)
    low = np.zeros(n, dtype=bool)
    low[rng.permutation(n)[: n // 2]] = True
    camp = np.clip(np.where(low, 0.25, 0.75) + 0.04 * rng.standard_normal(n), 0.0, 1.0)
    assert A.initial_opinions(C.M_CAMPS, n, np.random.default_rng(5)).tolist() == camp.tolist()
