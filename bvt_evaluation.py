"""Kennzahlen, Messreihen und Verdikte der Demo „Begrenztes Vertrauen“. Verdikte sind reine Funktionen (Art, Text); jede Zahl im Text kommt aus der Rechnung.

Modell: Hegselmann–Krause (jeder mittelt über sich und die Partner innerhalb des Vertrauensradius ε), synchron, bis zum Stillstand. Ausgewertet wird die größte zusammenhängende Gruppe (oder der vollständige
Graph). Maße: Lager (Gruppen mit gleicher Meinung und mindestens 5 % der Betriebe), größter Anteil, Splitter (Betriebe in kleineren Gruppen), Schritte; Konsens = größtes Lager mit mindestens 99 %.
Jede Messreihe mittelt (Median) über feste Netze (`LIVE_SEEDS` in der App, `SWEEP_SEEDS` für die README-Zahlen)."""

import math
import os
from dataclasses import dataclass

# BLAS-Threads: siehe bvt_algorithm.py (muss vor dem ersten Import von numpy stehen).
for _var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

import numpy as np

import bvt_algorithm as A
import bvt_constants as C
from bvt_scenario import Instance, layout_ring, make_instance

NAN = float("nan")


def de(x, digits=1) -> str:
    """Dezimalzahl mit Komma (deutsche Texte); eine nicht definierte Zahl erscheint als Gedankenstrich."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "–"
    return f"{x:.{digits}f}".replace(".", ",").replace("-", "−")


def pct(x, digits=0) -> str:
    return de(100.0 * x, digits)


def sci(x) -> str:
    """Zahl als Zehnerpotenz mit einer Nachkommastelle, zum Beispiel 1,1 · 10⁻¹¹; null bleibt 0."""
    if x == 0:
        return "0"
    mant, exp = f"{x:.1e}".split("e")
    e = int(exp)
    sup = ("⁻" if e < 0 else "") + "".join("⁰¹²³⁴⁵⁶⁷⁸⁹"[int(d)] for d in str(abs(e)))
    return f"{mant.replace('.', ',')} · 10{sup}"


def _rng(*parts):
    return np.random.default_rng([int(p) for p in parts])


def _median(values):
    return float(np.median(values)) if len(values) else NAN


# --- Netze --------------------------------------------------------------------------------------------------------------------------------------


def build_net(typ, n, c, seed, layout=False):
    """(Nachbarschaftsmatrix der ausgewerteten Gruppe, Verbund je Betrieb oder None, Knoten im Gesamtnetz, Instanz). Der vollständige Graph hat alle n Betriebe."""
    if typ == C.T_COMPLETE:
        adj = A.matrix_to_adj(A.complete_matrix(n))
        inst = Instance(typ, adj, layout_ring(n))
        return A.complete_matrix(n), None, list(range(n)), inst
    inst = make_instance(typ, n, c, seed, layout=layout)
    nodes = A.largest_component(inst.adj)
    labels = np.array([inst.groups[v] for v in nodes]) if inst.groups is not None else None
    return A.induced_matrix(inst.adj, nodes), labels, nodes, inst


# --- Hauptanalyse -----------------------------------------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Settings:
    netztyp: str = C.T_COMPLETE
    n: int = C.DEFAULT_N
    c: int = C.DEFAULT_C
    seed: int = C.DEFAULT_SEED
    eps: int = C.DEFAULT_EPS          # Vertrauensradius in Prozent
    mode: str = C.DEFAULT_MODE


@dataclass(frozen=True, eq=False)
class Analysis:
    inst: Instance
    settings: Settings
    nodes: tuple            # Betriebe der ausgewerteten Gruppe (Nummern im Gesamtnetz)
    a: object               # Nachbarschaftsmatrix der Gruppe
    x0: object              # Anfangsmeinungen
    run: dict               # Ergebnis von `run`
    camps: tuple            # (Lager, größter Anteil, Splitter, Gruppen) im Endzustand
    formula: float          # Endwert für ε größer als die Spanne (DeGroot mit Selbstgewicht), Σ (d + 1) x / Σ (d + 1)

    @property
    def m(self) -> int:
        return len(self.nodes)

    @property
    def eps(self) -> float:
        return self.settings.eps / 100.0

    @property
    def span0(self) -> float:
        return float(np.ptp(self.x0))

    @property
    def steps(self) -> int:
        return self.run["steps"]

    @property
    def consensus(self) -> bool:
        return self.camps[1] >= C.CONSENSUS_SHARE

    @property
    def top_value(self) -> float:
        """Meinung im größten Lager."""
        labels = A.group_labels(self.run["x"])
        sizes = np.bincount(labels)
        return float(np.mean(self.run["x"][labels == int(np.argmax(sizes))]))


def analyse(settings: Settings) -> Analysis:
    a, labels, nodes, inst = build_net(settings.netztyp, settings.n, settings.c, settings.seed, layout=True)
    x0 = A.initial_opinions(settings.mode, len(a), _rng(settings.seed, 2), labels)
    run = A.run(a, x0, settings.eps / 100.0, C.TOL, C.MAX_STEPS, frames=A.frame_schedule(C.MAX_STEPS, C.FRAMES))
    return Analysis(inst, settings, tuple(nodes), a, x0, run, A.camps(run["x"], C.BIG_SHARE), A.consensus_formula(a, x0))


def verdict_main(an: Analysis) -> tuple[str, str]:
    """Verdikt dieses Laufs: wie viele Lager bleiben, wie viele Betriebe sind Splitter, und kehrte sich die Reihenfolge um?"""
    if an.span0 == 0:
        return "info", f"Alle {an.m} Betriebe beginnen mit derselben Meinung ({de(float(an.x0[0]), 2)}): es gibt nichts abzugleichen."
    big, largest, splitters, groups = an.camps
    eps_txt = f"Vertrauensradius {an.settings.eps} %"
    if not an.run["converged"]:
        return "warning", f"Nach {an.steps} Schritten (Obergrenze) steht das Netz bei {eps_txt} noch nicht still: bisher {groups} Gruppen, die größte mit {pct(largest)} % der Betriebe."
    tail = f" In Schritt {an.run['first_reversal']} kehrte sich die Reihenfolge der Meinungen zum ersten Mal um." if an.run["first_reversal"] is not None else ""
    if an.consensus:
        text = f"Nach {an.steps} Schritten einigen sich {pct(largest, 1)} % der Betriebe auf {de(an.top_value, 3)} ({eps_txt}: Konsens)."
        if splitters:
            text += f" {splitters} Betriebe bleiben als Splitter zurück ({groups} Gruppen insgesamt)."
        if an.eps >= an.span0:
            text += (f" Weil der Vertrauensradius nicht kleiner als die Spanne der Anfangsmeinungen ({de(an.span0, 3)}) ist, ist das die DeGroot-Mittelung mit Selbstgewicht: der Endwert ist Σ (d + 1) x / Σ (d + 1) = {de(an.formula, 3)}.")
        return "success", text + tail
    if big == 0:
        return "info", f"Nach {an.steps} Schritten steht das Netz bei {eps_txt} still, aber ohne Lager: alle {groups} Gruppen haben weniger als {pct(C.BIG_SHARE)} % der Betriebe." + tail
    text = f"Nach {an.steps} Schritten steht das Netz bei {eps_txt} still: {big} Lager (das größte mit {pct(largest, 1)} % der Betriebe)"
    text += f" und {splitters} Betriebe in kleinen Gruppen (Splittern, insgesamt {groups} Gruppen)." if splitters else f", {groups} Gruppen insgesamt."
    return "info", text + tail


# --- E1: Treppe und Netz --------------------------------------------------------------------------------------------------------------------------


def staircase_rows(n, c, types=C.ALL_TYPES, epsilons=C.STAIR_EPS, seeds=C.LIVE_SEEDS, mode=C.M_RANDOM) -> list[dict]:
    """Je Netztyp und Vertrauensradius: Lager, größter Anteil, Gruppen (Median über die festen Netze), Anteil der Netze mit Konsens und Schritte; ob alle Läufe stillstanden."""
    rows = []
    for typ in types:
        nets = [build_net(typ, n, c, seed) for seed in seeds]
        for eps in epsilons:
            cells, steps, ok = [], [], True
            for seed, (a, labels, _, _) in zip(seeds, nets):
                x0 = A.initial_opinions(mode, len(a), _rng(seed, 5), labels)
                out = A.run(a, x0, eps, C.TOL, C.MAX_STEPS)
                cells.append(A.camps(out["x"], C.BIG_SHARE))
                steps.append(out["steps"])
                ok &= out["converged"]
            rows.append({"typ": typ, "eps": eps, "camps": _median([x[0] for x in cells]), "largest": _median([x[1] for x in cells]), "groups": _median([x[3] for x in cells]),
                         "consensus": float(np.mean([x[1] >= C.CONSENSUS_SHARE for x in cells])), "steps": _median(steps), "converged": ok, "nets": len(cells)})
    return rows


def stair_cell(rows, typ, eps):
    return next(r for r in rows if r["typ"] == typ and r["eps"] == eps)


def first_consensus(rows, typ, share=0.5):
    """Kleinster Vertrauensradius der Messreihe, bei dem mindestens `share` der Netze Konsens haben, oder None."""
    hits = [r["eps"] for r in sorted((r for r in rows if r["typ"] == typ), key=lambda r: r["eps"]) if r["consensus"] >= share]
    return hits[0] if hits else None


def verdict_staircase(rows: list[dict]) -> tuple[str, str]:
    """Verdikt zu E1: wo beginnt der Konsens, und wie zerfällt das Netz darunter?"""
    if not rows:
        return "warning", "Keine Läufe."
    types = list(dict.fromkeys(r["typ"] for r in rows))
    eps0 = min(r["eps"] for r in rows)
    parts = []
    for t in types:
        e = first_consensus(rows, t)
        parts.append(f"„{t}“ " + (f"ab {de(e, 2)}" if e is not None else f"im Raster nicht (bis {de(max(r['eps'] for r in rows), 2)})"))
    low = [stair_cell(rows, t, eps0) for t in types]
    worst = max(low, key=lambda r: r["groups"])
    text = "Konsens (das größte Lager hat mindestens 99 % der Betriebe) gibt es in mindestens der Hälfte der Netze bei Vertrauensradius: " + "; ".join(parts) + ". "
    text += (f"Bei ε = {de(eps0, 2)} zerfällt „{worst['typ']}“ im Median in {de(worst['groups'], 0)} Gruppen ({de(worst['camps'], 0)} Lager, größter Anteil {pct(worst['largest'])} %)")
    if types[0] == C.T_COMPLETE and worst["typ"] != C.T_COMPLETE:
        c0 = low[0]
        text += f", der vollständige Graph in {de(c0['groups'], 0)} ({de(c0['camps'], 0)} Lager)"
    return "info", text + "."


# --- E2: Reihenfolge und Identität ----------------------------------------------------------------------------------------------------------------


def order_rows(n, c, eps=C.ORDER_EPS, types=C.ALL_TYPES, seeds=C.LIVE_SEEDS) -> dict:
    """Je Netztyp: in wie vielen Läufen sich die Reihenfolge der Meinungen irgendwann umkehrt (Vertrauensradius `eps`), der Schritt der ersten Umkehr (Median), und für einen Radius über der Spanne
    die größte Abweichung des Endwerts von Σ (d + 1) x / Σ (d + 1) (Brücke zu Stück 9)."""
    order, identity = [], []
    for typ in types:
        nets = [build_net(typ, n, c, seed) for seed in seeds]
        firsts, devs = [], []
        for seed, (a, labels, _, _) in zip(seeds, nets):
            x0 = A.initial_opinions(C.M_RANDOM, len(a), _rng(seed, 6), labels)
            firsts.append(A.run(a, x0, eps, C.TOL, C.MAX_STEPS)["first_reversal"])
            out = A.run(a, x0, C.IDENTITY_EPS, 1e-13, 4 * C.MAX_STEPS)
            devs.append(max(abs(float(out["x"].mean()) - A.consensus_formula(a, x0)), float(np.ptp(out["x"]))))
        hit = [f for f in firsts if f is not None]
        order.append({"typ": typ, "reversed": len(hit), "runs": len(firsts), "first": _median(hit)})
        identity.append({"typ": typ, "max_dev": float(max(devs)), "runs": len(devs)})
    return {"order": order, "identity": identity, "eps": eps}


def verdict_order(res: dict) -> tuple[str, str]:
    """Verdikt zu E2: wo kehrt sich die Reihenfolge der Meinungen um, und stimmt die DeGroot-Brücke?"""
    if not res or not res.get("order"):
        return "warning", "Keine Läufe."
    always = [r["typ"] for r in res["order"] if r["reversed"] == r["runs"]]
    never = [r["typ"] for r in res["order"] if r["reversed"] == 0]
    mixed = [r for r in res["order"] if 0 < r["reversed"] < r["runs"]]
    text = f"Bei Vertrauensradius {de(res['eps'], 2)} kehrt sich die Reihenfolge der Meinungen "
    text += ("in jedem Lauf um in: " + ", ".join(f"„{t}“" for t in always)) if always else "in keinem Netztyp in jedem Lauf um"
    text += ("; nie in: " + ", ".join(f"„{t}“" for t in never)) if never else ""
    text += ("; teilweise in: " + ", ".join(f"„{r['typ']}“ ({r['reversed']} von {r['runs']})" for r in mixed)) if mixed else ""
    worst = max(r["max_dev"] for r in res["identity"])
    return "info", text + f". Für einen Radius über der Spanne weicht der Endwert um höchstens {sci(worst)} von der DeGroot-Formel Σ (d + 1) x / Σ (d + 1) ab."


# --- E3: Konsens kehrt zurück ---------------------------------------------------------------------------------------------------------------------


def lorenz_rows(n=C.LORENZ_N, grid=C.LORENZ_GRID, random_grid=C.LORENZ_RANDOM_GRID, runs=C.LORENZ_RANDOM_RUNS) -> dict:
    """Vollständiger Graph mit n Betrieben: (1) gleichabständiger Start über das feine Raster `grid`: Lager, größter Anteil, Konsens; (2) zufälliger Start über das gröbere Raster `random_grid`: Anteil der Läufe mit Konsens."""
    a = A.complete_matrix(n)
    x0 = np.linspace(0.0, 1.0, n)
    equi = []
    for eps in grid:
        out = A.run(a, x0, eps, C.TOL, C.MAX_STEPS)
        big, largest, _, groups = A.camps(out["x"], C.BIG_SHARE)
        equi.append({"eps": eps, "camps": big, "largest": largest, "groups": groups, "consensus": largest >= C.CONSENSUS_SHARE})
    rand = []
    for eps in random_grid:
        res = []
        for r in range(runs):
            out = A.run(a, A.initial_opinions(C.M_RANDOM, n, _rng(7, r), None), eps, C.TOL, C.MAX_STEPS)
            res.append(A.camps(out["x"], C.BIG_SHARE))
        rand.append({"eps": eps, "p_consensus": float(np.mean([x[1] >= C.CONSENSUS_SHARE for x in res])), "mean_camps": float(np.mean([x[0] for x in res])), "runs": runs})
    return {"n": n, "equi": equi, "random": rand}


def comeback_eps(equi) -> list:
    """Vertrauensradien, bei denen es Konsens gibt, obwohl er bei einem größeren Radius des Rasters fehlt (der Konsens „kehrt zurück“)."""
    out = []
    for i, r in enumerate(equi):
        if r["consensus"] and any(not q["consensus"] for q in equi[i + 1:]):
            out.append(r["eps"])
    return out


def biggest_drop(random_rows) -> float:
    """Größter Rückgang des Konsensanteils beim Übergang zum nächstgrößeren Radius (null heißt: monoton steigend)."""
    return max([0.0] + [random_rows[i]["p_consensus"] - random_rows[i + 1]["p_consensus"] for i in range(len(random_rows) - 1)])


def verdict_lorenz(res: dict) -> tuple[str, str]:
    """Verdikt zu E3: kehrt der Konsens bei sinkendem Radius zurück, und bei welchem Start?"""
    if not res or not res.get("equi"):
        return "warning", "Keine Läufe."
    back = comeback_eps(res["equi"])
    drop = biggest_drop(res["random"])
    text = f"Im vollständigen Graphen mit {res['n']} Betrieben gibt es bei gleichabständigem Start "
    if back:
        first_miss = next(q["eps"] for q in res["equi"] if not q["consensus"] and q["eps"] > back[0])
        text += f"Konsens bei ε = {', '.join(de(e, 4) for e in back)}, obwohl er bei ε = {de(first_miss, 4)} fehlt: der Konsens kehrt bei sinkendem Radius kurz zurück. "
    else:
        text += "keinen Radius, bei dem der Konsens bei sinkendem ε zurückkehrt. "
    runs = res["random"][0]["runs"]
    if drop == 0:
        text += f"Bei zufälligem Start ({runs} Läufe je Radius) steigt der Anteil der Läufe mit Konsens dagegen monoton mit ε."
    else:
        text += f"Bei zufälligem Start ({runs} Läufe je Radius) sinkt der Anteil der Läufe mit Konsens beim Übergang zum nächstgrößeren Radius höchstens um {pct(drop)} Prozentpunkte."
    return "info", text


# --- E4: Verbünde ------------------------------------------------------------------------------------------------------------------------------------


def community_rows(n=C.COMM_N, c=C.COMM_C, insides=C.COMM_INSIDES, epsilons=C.COMM_EPS, modes=(C.M_RANDOM, C.M_COMM), seeds=C.LIVE_SEEDS) -> list[dict]:
    """Verbünde mit einstellbarem Anteil der Kanten innen (sechs Verbünde): Lager und größter Anteil im Median über feste Netze, je Radius und Anfangsverteilung."""
    rows = []
    for inside in insides:
        nets = []
        for seed in seeds:
            a_full, lab = A.sbm_matrix(n, C.BLOCKS, c, inside, 7 * int(seed) + int(round(100 * inside)))
            nodes = A.largest_component(A.matrix_to_adj(a_full))
            nets.append((seed, A.induced_matrix(A.matrix_to_adj(a_full), nodes), lab[nodes]))
        for eps in epsilons:
            for mode in modes:
                cells = []
                for seed, a, lab in nets:
                    x0 = A.initial_opinions(mode, len(a), _rng(seed, 8), lab)
                    cells.append(A.camps(A.run(a, x0, eps, C.TOL, C.MAX_STEPS)["x"], C.BIG_SHARE))
                rows.append({"inside": inside, "eps": eps, "mode": mode, "camps": _median([x[0] for x in cells]), "largest": _median([x[1] for x in cells]), "nets": len(cells)})
    return rows


def community_cell(rows, inside, eps, mode):
    return next(r for r in rows if r["inside"] == inside and r["eps"] == eps and r["mode"] == mode)


def verdict_communities(rows: list[dict]) -> tuple[str, str]:
    """Verdikt zu E4: halten Verbünde Lager, und wann?"""
    if not rows:
        return "warning", "Keine Läufe."
    insides = sorted({r["inside"] for r in rows})
    eps = min(r["eps"] for r in rows)
    lo, hi = insides[0], insides[-1]
    text = f"Bei Vertrauensradius {de(eps, 2)} und zufälligem Start hat das Netz bei {pct(lo)} % Kanten innerhalb der Verbünde {de(community_cell(rows, lo, eps, C.M_RANDOM)['camps'], 0)} Lager, bei {pct(hi)} % "
    text += f"{de(community_cell(rows, hi, eps, C.M_RANDOM)['camps'], 0)}; beginnt jeder Verbund bei seiner eigenen Meinung, sind es {de(community_cell(rows, lo, eps, C.M_COMM)['camps'], 0)} bzw. {de(community_cell(rows, hi, eps, C.M_COMM)['camps'], 0)}."
    return "info", text
