"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import numpy as np
import plotly.graph_objects as go

import bvt_algorithm as A
import bvt_constants as C
from bvt_evaluation import comeback_eps, de, pct

MAX_EDGES = 3000          # größere Netze (zum Beispiel der vollständige Graph) werden ohne Kanten gezeichnet
GROUP_COLORS = ("#2F6B65", "#c4623b", "#6b5b95", "#9d755d", "#4c78a8", "#d1a43b", "#b04a7a", "#5e9c4a")
MAX_LINES = 8             # so viele Lager erhalten in den Bahnen eine eigene Farbe


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=340, bottom=10):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=bottom), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def _edges(a):
    n = len(a)
    return [(i, j) for i in range(n) for j in np.flatnonzero(a[i, i + 1:]) + i + 1]


def build_network(an, step):
    """Netz der ausgewerteten Gruppe; Farbe = Meinung im gewählten Schritt (feste Skala 0 bis 1); Kanten nur bei höchstens `MAX_EDGES` Partnerschaften."""
    pos = an.inst.pos
    nodes = an.nodes
    edges = _edges(an.a) if an.a.sum() / 2 <= MAX_EDGES else []
    xs, ys = [], []
    for i, j in edges:
        xs += [pos[nodes[i]][0], pos[nodes[j]][0], None]
        ys += [pos[nodes[i]][1], pos[nodes[j]][1], None]
    x = an.run["frames"][step]
    size = 5 if an.m > 120 else 8
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=C.COLOR_EDGE, width=0.7), hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(
        x=[pos[v][0] for v in nodes], y=[pos[v][1] for v in nodes], mode="markers", showlegend=False,
        marker=dict(size=size, color=[float(v) for v in x], colorscale="Viridis", cmin=0.0, cmax=1.0, line=dict(color="rgba(40,40,40,0.45)", width=0.4),
                    colorbar=dict(title=dict(text="Meinung"), thickness=12, len=0.8)),
        hovertext=[f"Betrieb {v}: Meinung {de(float(m), 3)}, {int(an.a[i].sum())} Partner" for i, (v, m) in enumerate(zip(nodes, x))], hoverinfo="text"))
    fig.add_trace(go.Scatter(x=[-0.04, 1.04], y=[-0.04, 1.04], mode="markers", marker=dict(size=1, color="rgba(0,0,0,0)"), hoverinfo="skip", showlegend=False))
    fig.update_xaxes(visible=False, autorange=True)
    fig.update_yaxes(visible=False, autorange=True, scaleanchor="x", scaleratio=1)
    fig.update_layout(height=460, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_paths(an, step):
    """Bahnen der Meinungen über die Schritte (eine Linie je Betrieb, nach Lager des Endzustands gefärbt; kleine Gruppen grau); senkrechte Linie = gewählter Schritt. Schritte logarithmisch ab 1."""
    frames = an.run["frames"]
    keys = sorted(frames)
    traj = np.array([frames[k] for k in keys])                       # Zeilen: Bilder, Spalten: Betriebe
    labels = A.group_labels(an.run["x"])
    sizes = np.bincount(labels)
    order = np.argsort(-sizes, kind="stable")
    big = [g for g in order[:MAX_LINES] if sizes[g] >= C.BIG_SHARE * an.m]
    fig = go.Figure()
    groups = [(f"Lager {k + 1} (Endwert {de(float(np.mean(an.run['x'][labels == g])), 2)})", np.flatnonzero(labels == g), GROUP_COLORS[k]) for k, g in enumerate(big)]
    rest = np.flatnonzero(~np.isin(labels, big))
    if len(rest):
        groups.append(("Splitter und kleine Gruppen", rest, "rgba(120,120,120,0.9)"))
    xs_key = [k + 1 for k in keys]
    for name, idx, color in groups:
        xs, ys = [], []
        for i in idx:
            xs += xs_key + [None]
            ys += traj[:, i].tolist() + [None]
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name=name, line=dict(color=color, width=1), opacity=0.55, hoverinfo="skip"))
    fig.add_vline(x=step + 1, line=dict(color="rgba(120,120,120,0.9)", width=1.5, dash="dot"))
    fig.update_xaxes(title_text="Schritt + 1 (logarithmisch)", type="log")
    fig.update_yaxes(title_text="Meinung", range=[-0.02, 1.02])
    return _base(fig, height=340, bottom=60)


def build_staircase(rows, key):
    """Lager (key „camps“) bzw. größter Anteil in Prozent (key „largest“) über den Vertrauensradius, je Netztyp."""
    fig = go.Figure()
    for typ in dict.fromkeys(r["typ"] for r in rows):
        mine = sorted((r for r in rows if r["typ"] == typ), key=lambda r: r["eps"])
        scale = 100.0 if key == "largest" else 1.0
        fig.add_trace(go.Scatter(x=[r["eps"] for r in mine], y=[scale * r[key] for r in mine], mode="lines+markers", name=typ,
                                 line=dict(color=C.TYPE_COLORS[typ], width=4 if typ == C.T_COMPLETE else 2, dash="solid" if typ == C.T_COMPLETE else "dot")))
    eps = sorted({r["eps"] for r in rows})
    fig.update_xaxes(title_text="Vertrauensradius ε", tickvals=eps, ticktext=[de(e, 2) for e in eps])
    if key == "largest":
        fig.update_yaxes(title_text="größtes Lager (% der Betriebe)", range=[0, 102], ticksuffix=" %")
    else:
        fig.update_yaxes(title_text="Lager (Gruppen mit ≥ 5 % der Betriebe)", rangemode="tozero")
    return _base(fig, height=360, bottom=80)


def build_order(res):
    """Anteil der Läufe, in denen sich die Reihenfolge der Meinungen irgendwann umkehrt, je Netztyp."""
    rows = res["order"]
    ys = [100.0 * r["reversed"] / r["runs"] for r in rows]
    fig = go.Figure(go.Bar(x=[r["typ"] for r in rows], y=ys, marker_color=[C.TYPE_COLORS[r["typ"]] for r in rows], text=[f"{r['reversed']} von {r['runs']}" for r in rows], textposition="outside"))
    fig.update_xaxes(tickangle=-20)
    fig.update_yaxes(title_text="Läufe mit Umkehr (%)", range=[0, 115], ticksuffix=" %")
    return _base(fig, height=340, bottom=110)


def build_lorenz_equi(res):
    """Gleichabständiger Start im vollständigen Graphen: Lager über das feine Raster; Rauten = Konsens, der bei einem größeren Radius fehlt (er kehrt zurück)."""
    rows = res["equi"]
    back = set(comeback_eps(rows))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[r["eps"] for r in rows], y=[r["camps"] for r in rows], mode="lines", line=dict(color=C.COLOR_A, width=3, shape="hv"), name="Lager"))
    pts = [r for r in rows if r["eps"] in back]
    fig.add_trace(go.Scatter(x=[r["eps"] for r in pts], y=[r["camps"] for r in pts], mode="markers", name="Konsens kehrt zurück",
                             marker=dict(symbol="diamond", size=12, color=C.COLOR_B, line=dict(width=1.5, color="white"))))
    fig.update_xaxes(title_text="Vertrauensradius ε")
    fig.update_yaxes(title_text="Lager", rangemode="tozero", dtick=1)
    return _base(fig, height=320, bottom=60)


def build_lorenz_random(res):
    """Zufälliger Start im vollständigen Graphen: Anteil der Läufe mit Konsens über das Raster."""
    rows = res["random"]
    fig = go.Figure(go.Scatter(x=[r["eps"] for r in rows], y=[100.0 * r["p_consensus"] for r in rows], mode="lines+markers", line=dict(color=C.COLOR_C, width=3), name="Läufe mit Konsens"))
    fig.update_xaxes(title_text="Vertrauensradius ε")
    fig.update_yaxes(title_text="Läufe mit Konsens (%)", range=[-2, 102], ticksuffix=" %")
    return _base(fig, height=300, bottom=60)


def build_communities(rows):
    """Lager über den Anteil der Kanten innerhalb der Verbünde, je Vertrauensradius und Anfangsverteilung."""
    fig = go.Figure()
    combos = list(dict.fromkeys((r["eps"], r["mode"]) for r in rows))
    for k, (eps, mode) in enumerate(combos):
        mine = sorted((r for r in rows if r["eps"] == eps and r["mode"] == mode), key=lambda r: r["inside"])
        fig.add_trace(go.Scatter(x=[100.0 * r["inside"] for r in mine], y=[r["camps"] for r in mine], mode="lines+markers", name=f"ε = {de(eps, 2)}, Start: {mode}",
                                 line=dict(color=GROUP_COLORS[k % len(GROUP_COLORS)], width=3)))
    insides = sorted({r["inside"] for r in rows})
    fig.update_xaxes(title_text="Kanten innerhalb der Verbünde (%)", tickvals=[100.0 * x for x in insides], ticktext=[pct(x) for x in insides])
    fig.update_yaxes(title_text="Lager", rangemode="tozero")
    return _base(fig, height=360, bottom=90)
