"""Orakel-Tests (ORACLE-PLAYBOOK): der Kern wird gegen unabhängige Rechenwege geprüft, nicht gegen sich selbst.

* Schritt: eine Schleifenfassung (zwei Schleifen über Paare, ohne Matrixprodukt) auf über 100 Zufallsnetzen, Meinungen und Radien, auch an der Grenze |Δ| = ε.
* DeGroot-Fall: ε größer als die Spanne gegen die Iteration der Matrix D̃⁻¹ Ã und gegen die Formel Σ (d + 1) x / Σ (d + 1).
* Eigenschaften: Meinungen bleiben im Bereich, die Spanne wächst nie, der Stillstand ist ein Fixpunkt, im vollständigen Graphen bleibt die Reihenfolge erhalten.
"""

import numpy as np
import pytest

import bvt_algorithm as A
import bvt_constants as C
from conftest import make_matrix, random_connected

NETS = 120


def _loop_step(a, x, eps):
    n = len(x)
    out = []
    for i in range(n):
        total, count = 0.0, 0
        for j in range(n):
            if (j == i or a[i, j] == 1.0) and abs(x[j] - x[i]) <= eps + 1e-15:
                total += x[j]
                count += 1
        out.append(total / count)
    return np.array(out)


def _nets(count=NETS, seed=31, lo=4, hi=14):
    rng = np.random.default_rng(seed)
    for _ in range(count):
        n = int(rng.integers(lo, hi + 1))
        yield rng, random_connected(rng, n, extra=int(rng.integers(0, 2 * n)))


def test_step_equals_the_loop_version_on_many_random_networks_and_at_the_boundary():
    for rng, a in _nets():
        n = len(a)
        eps = float(rng.choice([0.05, 0.1, 0.25, 0.5, 1.5]))
        x = rng.random(n)
        assert np.allclose(A.step(a, x, eps), _loop_step(a, x, eps), atol=1e-14)
        grid = rng.integers(0, 9, size=n) / 8.0                                               # Vielfache von ⅛: Abstände genau ε kommen vor
        for e in (0.125, 0.25, 0.5):
            assert np.allclose(A.step(a, grid, e), _loop_step(a, grid, e), atol=1e-14)


def test_huge_radius_equals_the_degroot_matrix_iteration_and_the_formula():
    for rng, a in _nets(count=40, seed=32):
        x0 = rng.random(len(a))
        out = A.run(a, x0, 2.0, 1e-14, 200_000)
        assert out["converged"]
        w = (a + np.eye(len(a))) / (a.sum(axis=1) + 1)[:, None]                              # D̃⁻¹ Ã
        x = x0.copy()
        for _ in range(100_000):
            if np.ptp(x) < 1e-13:
                break
            x = w @ x
        assert np.allclose(out["x"], x.mean(), atol=1e-10) and np.allclose(out["x"], A.consensus_formula(a, x0), atol=1e-10)


def test_opinions_stay_in_range_the_spread_never_grows_and_the_end_is_a_fixed_point():
    for rng, a in _nets(count=60, seed=33):
        x0 = rng.random(len(a))
        eps = float(rng.choice([0.1, 0.2, 0.3, 0.5]))
        x = x0.copy()
        spread = np.ptp(x)
        for _ in range(500):
            nx = A.step(a, x, eps)
            assert nx.min() >= x.min() - 1e-12 and nx.max() <= x.max() + 1e-12 and np.ptp(nx) <= spread + 1e-12
            spread = np.ptp(nx)
            x = nx
        out = A.run(a, x0, eps, C.TOL, 20000)
        assert out["converged"] and np.allclose(A.step(a, out["x"], eps), out["x"], atol=1e-11)
        d = np.abs(out["x"][:, None] - out["x"][None, :])
        assert np.all(d[(a == 1.0) & (d <= eps)] < 1e-6)                                      # im Stillstand haben vertraute Partner dieselbe Meinung


def test_the_complete_graph_keeps_the_order_and_the_camps_stay_apart():
    for seed in range(NETS):
        n = 30
        x0 = np.random.default_rng(seed).random(n)
        eps = float(np.random.default_rng(seed + 1000).choice([0.05, 0.1, 0.2, 0.3]))
        out = A.run(A.complete_matrix(n), x0, eps, C.TOL, 5000)
        assert out["converged"] and out["first_reversal"] is None, seed
        means = np.array([out["x"][A.group_labels(out["x"]) == g].mean() for g in range(len(A.group_sizes(out["x"])))])
        assert len(means) == 1 or np.min(np.diff(means)) > eps                                  # Lager liegen im Stillstand mehr als ε auseinander


def test_networks_can_reverse_the_order_where_the_complete_graph_cannot():
    path = make_matrix(3, [(0, 1), (1, 2)])
    assert A.run(path, [0.0, 0.5, 0.4], 1.0, C.TOL, 100)["first_reversal"] == 1
    assert A.run(A.complete_matrix(3), [0.0, 0.5, 0.4], 1.0, C.TOL, 100)["first_reversal"] is None
    reversals = 0
    for rng, a in _nets(count=60, seed=34, lo=20, hi=40):
        reversals += A.run(a, rng.random(len(a)), 0.2, C.TOL, 5000)["first_reversal"] is not None
    assert reversals >= 40                                                                      # in Netzen kehrt sich die Reihenfolge fast immer irgendwann um


def test_zero_radius_keeps_everyone_and_a_huge_radius_on_the_complete_graph_agrees_in_one_step():
    for rng, a in _nets(count=10, seed=35):
        x = rng.random(len(a))
        out = A.run(a, x, 0.0, C.TOL, 10)
        assert out["steps"] == 0 and out["x"].tolist() == x.tolist() and len(A.group_sizes(x)) == len(x)
    x = np.random.default_rng(1).random(8)
    out = A.run(A.complete_matrix(8), x, 2.0, C.TOL, 10)
    assert out["steps"] == 1 and out["x"].tolist() == pytest.approx([x.mean()] * 8)
