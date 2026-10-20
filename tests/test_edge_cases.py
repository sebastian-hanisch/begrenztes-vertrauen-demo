"""Randfälle, an denen Kernroutinen erfahrungsgemäß brechen (DEMO-PLAYBOOK §12): kleinste und größte Regler, alle Netztypen und Modi, Warnungen als Fehler, Obergrenze der Schritte, Abbildungen."""

import warnings

import numpy as np
import pytest

import bvt_algorithm as A
import bvt_constants as C
import bvt_evaluation as ev
import bvt_visualization as V


@pytest.mark.parametrize("typ", C.ALL_TYPES)
def test_every_network_type_at_the_slider_corners_runs_without_warnings(typ):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        for n, c, eps, mode in ((C.N_MIN, C.C_MIN, C.EPS_MIN, C.M_RANDOM), (C.N_MIN, C.C_MAX, C.EPS_MAX, C.M_EQUI), (C.N_MAX, C.C_MAX, 20, C.M_COMM), (C.N_MAX, C.C_MIN, 33, C.M_CAMPS)):
            an = ev.analyse(ev.Settings(typ, n, c, 3, eps, mode))
            assert 2 <= an.m <= an.inst.n and ev.verdict_main(an)[0] in ("success", "info", "warning")
            assert an.run["converged"] and an.steps >= 0 and all(len(x) == an.m for x in an.run["frames"].values()) and an.run["frames"][an.steps].tolist() == an.run["x"].tolist()
            assert np.all(an.run["x"] >= an.x0.min() - 1e-12) and np.all(an.run["x"] <= an.x0.max() + 1e-12)          # Meinungen bleiben im Bereich der Anfangsmeinungen
            assert sum(A.group_sizes(an.run["x"])) == an.m and 0 <= an.camps[0] <= 1 / C.BIG_SHARE and an.camps[3] >= 1


@pytest.mark.parametrize("typ", C.ALL_TYPES)
def test_many_seeds_in_the_smallest_networks_never_break_the_analysis(typ):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        for seed in range(6):
            for mode in C.MODES:
                an = ev.analyse(ev.Settings(typ, C.N_MIN, C.C_MIN, seed, 20, mode))
                assert an.m >= 2 and an.run["converged"] and np.isfinite(an.run["x"]).all()


def test_the_step_limit_is_reported_as_not_converged(monkeypatch):
    monkeypatch.setattr(C, "MAX_STEPS", 3)
    an = ev.analyse(ev.Settings(C.T_GRID, 100, 4, 3, 20, C.M_RANDOM))
    assert not an.run["converged"] and an.steps == 3 and ev.verdict_main(an)[0] == "warning" and "Obergrenze" in ev.verdict_main(an)[1]
    fig = V.build_paths(an, 3)
    assert fig.data and all(ax.fixedrange for ax in (fig.layout.xaxis, fig.layout.yaxis))


def test_tiny_and_huge_radius_extremes():
    tiny = ev.analyse(ev.Settings(C.T_COMPLETE, 200, 6, 3, C.EPS_MIN, C.M_RANDOM))
    assert tiny.camps[3] > 20 and tiny.run["converged"]                                              # ε = 1 %: viele kleine Gruppen
    huge = ev.analyse(ev.Settings(C.T_GRID, 100, 4, 3, C.EPS_MAX, C.M_RANDOM))
    assert huge.consensus and huge.eps >= huge.span0 and "DeGroot-Mittelung" in ev.verdict_main(huge)[1]
    assert huge.run["x"].mean() == pytest.approx(huge.formula, abs=1e-9)


def test_figures_are_built_for_the_analysis_and_the_experiment_rows():
    seeds = C.LIVE_SEEDS[:2]
    for typ in (C.T_COMPLETE, C.T_RING, C.T_COMMUNITIES):
        an = ev.analyse(ev.Settings(typ, 80, 6, 3, 25, C.M_RANDOM))
        for step in (0, max(an.run["frames"])):
            for fig in (V.build_network(an, step), V.build_paths(an, step)):
                assert fig.data and all(ax.fixedrange for ax in (fig.layout.xaxis, fig.layout.yaxis))
    e1 = ev.staircase_rows(50, 4, types=(C.T_COMPLETE, C.T_RANDOM), epsilons=(0.1, 0.3), seeds=seeds)
    e2 = ev.order_rows(40, 4, types=(C.T_COMPLETE, C.T_RANDOM), seeds=seeds)
    e3 = ev.lorenz_rows(n=60, grid=(0.15, 0.2, 0.25), random_grid=(0.1, 0.3), runs=2)
    e4 = ev.community_rows(n=60, c=8, insides=(0.5, 0.99), epsilons=(0.1, 0.25), seeds=seeds)
    for fig in (V.build_staircase(e1, "camps"), V.build_staircase(e1, "largest"), V.build_order(e2), V.build_lorenz_equi(e3), V.build_lorenz_random(e3), V.build_communities(e4)):
        assert fig.data and all(ax.fixedrange for ax in (fig.layout.xaxis, fig.layout.yaxis))


def test_the_network_figure_draws_edges_only_for_small_networks_and_colors_follow_the_step():
    small = ev.analyse(ev.Settings(C.T_RANDOM, 60, 6, 3, 25, C.M_RANDOM))
    fig = V.build_network(small, 0)
    assert len(fig.data[0].x) > 0 and list(fig.data[1].marker.color) == pytest.approx(small.x0.tolist()) and fig.data[1].marker.cmin == 0.0 and fig.data[1].marker.cmax == 1.0
    last = V.build_network(small, small.steps)
    assert list(last.data[1].marker.color) == pytest.approx(small.run["x"].tolist())
    dense = ev.analyse(ev.Settings(C.T_COMPLETE, 100, 6, 3, 25, C.M_RANDOM))
    assert len(V.build_network(dense, 0).data[0].x) == 0                                              # vollständiger Graph: zu viele Kanten, keine Linien
    assert len(V._edges(A.complete_matrix(5))) == 10 and len(V._edges(A.complete_matrix(1))) == 0


def test_the_paths_figure_has_one_color_per_camp_and_grey_splitters():
    an = ev.analyse(ev.Settings(C.T_RANDOM, 150, 6, 35, 25, C.M_RANDOM))                              # ein Lager und sechs Splitter (Preset)
    fig = V.build_paths(an, 0)
    assert [tr.name for tr in fig.data] == ["Lager 1 (Endwert 0,47)", "Splitter und kleine Gruppen"] and fig.layout.xaxis.type == "log"
    lines = sum(1 for tr in fig.data for v in tr.y if v is None)
    assert lines == an.m                                                                              # eine Linie je Betrieb
    many = ev.analyse(ev.Settings(C.T_COMMUNITIES, 120, 12, 35, 10, C.M_COMM))
    assert len(V.build_paths(many, 0).data) == C.BLOCKS                                              # sechs Lager, keine Splitter


def test_the_lorenz_chart_marks_exactly_the_comeback_points():
    res = ev.lorenz_rows(n=100, grid=(0.18, 0.19, 0.2), random_grid=(0.3,), runs=1)
    fig = V.build_lorenz_equi(res)
    assert list(fig.data[1].x) == [0.19] and list(fig.data[0].x) == [0.18, 0.19, 0.2]
    empty = dict(res, equi=[dict(r, consensus=False) for r in res["equi"]])
    assert list(V.build_lorenz_equi(empty).data[1].x) == []
