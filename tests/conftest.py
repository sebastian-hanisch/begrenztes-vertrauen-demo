"""Gemeinsame Fixtures und Hilfen (DEMO-PLAYBOOK §1b): Mini-Instanzen, an denen jede Einheit von Hand geprüft wird."""

import os
import sys
from pathlib import Path

for _var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):    # vor dem ersten Import von numpy (siehe bvt_algorithm.py)
    os.environ.setdefault(_var, "1")

import numpy as np  # noqa: E402
import pytest  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def make_matrix(n, pairs):
    """0/1-Nachbarschaftsmatrix aus einer Kantenliste."""
    a = np.zeros((n, n))
    for i, j in pairs:
        if i != j:
            a[i, j] = a[j, i] = 1.0
    return a


def random_connected(rng, n, extra=None):
    """Zufälliges zusammenhängendes Netz: Baum plus `extra` Zusatzkanten (Standard: n)."""
    pairs = {(i, int(rng.integers(i))) for i in range(1, n)}
    for _ in range(n if extra is None else extra):
        i, j = sorted(rng.choice(n, size=2, replace=False).tolist())
        pairs.add((i, j))
    return make_matrix(n, pairs)


@pytest.fixture
def path3():
    """Pfad 0 - 1 - 2."""
    return make_matrix(3, [(0, 1), (1, 2)])


@pytest.fixture
def tri():
    """Dreieck (auch der vollständige Graph mit drei Betrieben)."""
    return make_matrix(3, [(0, 1), (1, 2), (0, 2)])


@pytest.fixture
def rng():
    return np.random.default_rng(7)
