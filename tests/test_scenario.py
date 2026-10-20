"""Netze: gültige Netze, Determinismus (auch über Prozesse), Positionen, größte Gruppe, Verbünde, vollständiger Graph."""

import math
import os
import subprocess
import sys
from pathlib import Path

import pytest

import bvt_algorithm as A
import bvt_constants as C
import bvt_evaluation as ev
import bvt_scenario as S

ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize("typ", C.GENERATED_TYPES)
@pytest.mark.parametrize("n,c", [(C.N_MIN, C.C_MIN), (C.N_MIN, C.C_MAX), (C.DEFAULT_N, C.DEFAULT_C), (C.N_MAX, C.C_MAX)])
def test_every_corner_gives_a_valid_network(typ, n, c):
    inst = S.make_instance(typ, n, c, 35)
    assert inst.n >= 2 and len(inst.pos) == inst.n
    for x, y in inst.pos:
        assert math.isfinite(x) and math.isfinite(y) and -1e-9 <= x <= 1 + 1e-9 and -1e-9 <= y <= 1 + 1e-9
    for a, nb in enumerate(inst.adj):
        assert list(nb) == sorted(set(nb)) and a not in nb
        for b in nb:
            assert a in inst.adj[b]


def test_instances_are_deterministic_per_seed_and_differ_between_seeds():
    a = S.make_instance(C.T_COMMUNITIES, 80, 6, 5)
    assert a.adj == S.make_instance(C.T_COMMUNITIES, 80, 6, 5).adj and a.pos == S.make_instance(C.T_COMMUNITIES, 80, 6, 5).pos
    assert S.make_instance(C.T_COMMUNITIES, 80, 6, 6, layout=False).adj != a.adj


def test_network_run_and_start_are_independent_of_the_hash_seed_of_the_process():
    code = ("import sys; sys.path.insert(0, sys.argv[1]); import hashlib, bvt_scenario as S, bvt_constants as C, bvt_evaluation as E;"
            "h = hashlib.sha256();"
            "[h.update(repr(S.make_instance(t, 60, 5, 7, layout=False).adj).encode()) for t in C.GENERATED_TYPES];"
            "[h.update(repr((E.analyse(E.Settings(t, 60, 5, 7, 22, m)).x0.tolist(), E.analyse(E.Settings(t, 60, 5, 7, 22, m)).run['steps'], E.analyse(E.Settings(t, 60, 5, 7, 22, m)).camps)).encode()) for t in C.ALL_TYPES for m in C.MODES];"
            "print(h.hexdigest())")
    outs = []
    for hashseed in ("1", "2"):
        env = dict(os.environ, PYTHONHASHSEED=hashseed)
        outs.append(subprocess.run([sys.executable, "-I", "-X", "utf8", "-c", code, str(ROOT)], capture_output=True, text=True, env=env, check=True).stdout.strip())
    assert outs[0] == outs[1] and len(outs[0]) == 64


def test_layout_false_skips_the_force_layout_and_unknown_type_raises():
    inst = S.make_instance(C.T_RANDOM, 60, 4, 1, layout=False)
    assert set(inst.pos) == {(0.5, 0.5)}
    with pytest.raises(ValueError):
        S.make_instance("gibt es nicht", 60, 4, 1)


def test_the_complete_graph_has_every_node_no_labels_and_a_circle_layout():
    a, labels, nodes, inst = ev.build_net(C.T_COMPLETE, 30, 6, 3, layout=True)
    assert a.shape == (30, 30) and a.sum() == 30 * 29 and labels is None and nodes == list(range(30)) and inst.n == 30 and len(set(inst.pos)) == 30


@pytest.mark.parametrize("typ", C.GENERATED_TYPES)
def test_build_net_is_the_connected_largest_component_with_matching_labels(typ):
    a, labels, nodes, inst = ev.build_net(typ, 90, 3, 11)
    assert len(nodes) == len(a) >= 2 and (a == a.T).all() and a.sum(axis=1).min() >= 1
    assert len(A.largest_component(A.matrix_to_adj(a))) == len(a)
    if typ == C.T_COMMUNITIES:
        assert [int(g) for g in labels] == [inst.groups[v] for v in nodes]
    else:
        assert labels is None


@pytest.mark.parametrize("inside", C.COMM_INSIDES)
def test_community_networks_have_the_requested_inside_share(inside):
    a, lab = A.sbm_matrix(C.COMM_N, C.BLOCKS, C.COMM_C, inside, 100000)
    same = lab[:, None] == lab[None, :]
    assert (a * same).sum() / a.sum() == pytest.approx(inside, abs=0.05) and a.sum() / C.COMM_N == pytest.approx(C.COMM_C, rel=0.1)
    nodes = A.largest_component(A.matrix_to_adj(a))
    assert len(nodes) >= 0.95 * C.COMM_N                                                         # c = 12: das Netz bleibt fast ganz zusammenhängend

