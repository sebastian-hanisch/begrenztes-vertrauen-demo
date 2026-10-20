"""Kern: Meinungsbildung mit begrenztem Vertrauen (Hegselmann–Krause) auf ungerichteten Netzen (numpy, dichte Matrizen für n ≤ 200).

Jeder Betrieb ersetzt seine Meinung durch den Mittelwert aller Meinungen von sich und seinen Partnern, die höchstens um den Vertrauensradius ε von der eigenen abweichen:
x_i(t + 1) = Σ_j M_ij x_j(t) / Σ_j M_ij mit M_ij = 1, wenn j = i oder j Partner von i, und |x_j − x_i| ≤ ε. Das Netz steht still, wenn sich nichts mehr ändert; die Meinungen bilden dann Lager
(Gruppen mit gleicher Meinung). Für ε größer als die Spanne ist das die DeGroot-Mittelung mit Selbstgewicht 1 / (d_i + 1).

Netze sind 0/1-Nachbarschaftsmatrizen (symmetrisch, Diagonale 0). Zufall nur über `numpy.random.default_rng(Seed)`."""

import os

# Dichte Matrizen bis 200 × 200: ein BLAS-Thread genügt. Mehrere Threads machen kleine Rechnungen auf ausgelasteten Rechnern hundertfach langsamer.
for _var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

import numpy as np

EPS_TOL = 1e-15           # Toleranz beim Vergleich |Δ| ≤ ε (Gleichheit an der Grenze zählt als vertraut)
GAP = 1e-6                # Meinungen mit kleinerem Abstand gehören zum selben Lager
ORDER_TOL = 1e-12         # Toleranz der Ordnungsprüfung

# --- Netze ----------------------------------------------------------------------------------------------------------------------------------------


def complete_matrix(n):
    """Vollständiger Graph: jeder kennt jeden."""
    return np.ones((n, n)) - np.eye(n)


def matrix_to_adj(a):
    return tuple(tuple(np.flatnonzero(row).tolist()) for row in a)


def largest_component(adj):
    """Knoten der größten Zusammenhangskomponente, aufsteigend (Gleichstand: die mit dem kleinsten Knoten)."""
    n = len(adj)
    seen = [False] * n
    best = []
    for s in range(n):
        if seen[s]:
            continue
        comp = [s]
        seen[s] = True
        for x in comp:
            for w in adj[x]:
                if not seen[w]:
                    seen[w] = True
                    comp.append(w)
        if len(comp) > len(best):
            best = comp
    return sorted(best)


def induced_matrix(adj, nodes):
    """Nachbarschaftsmatrix des Teilnetzes auf `nodes` (neue Nummern = Position in `nodes`)."""
    idx = {v: i for i, v in enumerate(nodes)}
    a = np.zeros((len(nodes), len(nodes)))
    for v in nodes:
        for w in adj[v]:
            if w in idx:
                a[idx[v], idx[w]] = 1.0
    return a


def sbm_matrix(n, q, c, inside, seed):
    """Blockmodell: q gleich große Gruppen (Knoten i gehört zu Gruppe i · q // n), mittlerer Grad c, Anteil `inside` der Kanten innerhalb der Gruppen. Rückgabe (Nachbarschaftsmatrix, Gruppe je Knoten)."""
    lab = np.arange(n) * q // n
    same = lab[:, None] == lab[None, :]
    n_in = (same.sum() - n) / 2.0
    n_out = n * (n - 1) / 2.0 - n_in
    m = c * n / 2.0
    p_in = min(1.0, inside * m / n_in) if n_in > 0 else 0.0
    p_out = min(1.0, (1.0 - inside) * m / n_out) if n_out > 0 else 0.0
    prob = np.where(same, p_in, p_out)
    u = np.random.default_rng(int(seed)).random((n, n))
    upper = np.triu(u < prob, 1).astype(float)
    return upper + upper.T, lab


# --- Hegselmann–Krause ----------------------------------------------------------------------------------------------------------------------------


def step(a, x, eps):
    """Ein synchroner Schritt: Mittelwert über sich und die Partner innerhalb des Vertrauensradius."""
    x = np.asarray(x, dtype=float)
    m = (a + np.eye(len(a))) * (np.abs(x[:, None] - x[None, :]) <= eps + EPS_TOL)
    return (m @ x) / m.sum(axis=1)


def frame_schedule(max_steps, frames):
    """Schritte, deren Meinungen aufgehoben werden: 0, 1, 2, … und danach geometrisch bis `max_steps` (höchstens etwa `frames` Stück)."""
    steps = {0, 1}
    steps |= {int(round(v)) for v in np.geomspace(1, max(1, max_steps), frames)}
    return sorted(s for s in steps if 0 <= s <= max_steps)


def run(a, x0, eps, tol, max_steps, frames=None):
    """Iteration bis zum Stillstand (größte Änderung unter `tol`) oder `max_steps`. Rückgabe: steps, converged, x (Endzustand), frames (Schritt -> Meinungen für die Schritte aus `frames` und den letzten),
    first_reversal (erster Schritt, in dem sich die Reihenfolge der Meinungen gegenüber dem Anfang umkehrt, oder None). Der Stillstandsschritt (keine Änderung) zählt nicht als Schritt."""
    x = np.array(x0, dtype=float)
    order = np.argsort(x, kind="stable")
    wanted = set(frames or ())
    kept = {0: x.copy()} if 0 in wanted else {}
    reversal = None
    steps = 0
    converged = False
    while steps < max_steps:
        nx = step(a, x, eps)
        if np.max(np.abs(nx - x)) < tol:
            converged = True
            x = nx
            break
        x = nx
        steps += 1
        if reversal is None and np.any(np.diff(x[order]) < -ORDER_TOL):
            reversal = steps
        if steps in wanted:
            kept[steps] = x.copy()
    kept[steps] = x.copy()
    return {"steps": steps, "converged": converged, "x": x, "frames": kept, "first_reversal": reversal}


# --- Lager ----------------------------------------------------------------------------------------------------------------------------------------


def group_sizes(x, gap=GAP):
    """Größen der Gruppen gleicher Meinung (Meinungen mit Abstand ≤ gap in der sortierten Folge gehören zusammen), nach Meinung aufsteigend."""
    s = np.sort(np.asarray(x, dtype=float))
    cuts = np.flatnonzero(np.diff(s) > gap) + 1
    return [len(part) for part in np.split(s, cuts)]


def group_labels(x, gap=GAP):
    """Gruppennummer je Betrieb (0 = kleinste Meinung)."""
    x = np.asarray(x, dtype=float)
    order = np.argsort(x, kind="stable")
    labels = np.zeros(len(x), dtype=int)
    labels[order] = np.concatenate(([0], np.cumsum(np.diff(x[order]) > gap)))
    return labels


def camps(x, share=0.05, gap=GAP):
    """(Zahl der Lager = Gruppen mit mindestens `share` der Betriebe, größter Anteil, Zahl der Betriebe in kleineren Gruppen (Splitter), Zahl aller Gruppen)."""
    sizes = group_sizes(x, gap)
    n = len(x)
    big = [s for s in sizes if s >= share * n]
    return len(big), max(sizes) / n, n - sum(big), len(sizes)


# --- Brücke zu Stück 9 ----------------------------------------------------------------------------------------------------------------------------


def consensus_formula(a, x0):
    """Endwert für ε größer als die Spanne (DeGroot mit Selbstgewicht 1 / (d + 1)): Σ (d_i + 1) x_i(0) / Σ (d_i + 1)."""
    w = a.sum(axis=1) + 1.0
    return float(np.dot(w, np.asarray(x0, dtype=float)) / w.sum())


# --- Anfangsverteilungen --------------------------------------------------------------------------------------------------------------------------


def initial_opinions(mode, n, rng, labels=None, blocks=6):
    """Anfangsmeinungen in [0, 1]: „Zufällig gleichverteilt“, „Gleichabständig“ (n gleich weit entfernte Werte in zufälliger Reihenfolge), „Nach Verbünden ausgerichtet“ (Mitte des Verbunds (g + ½) / blocks plus Rauschen 0,04;
    ohne `labels` sechs gleich große Nummernblöcke), „Zwei Lager“ (halb um 0,25, halb um 0,75, Rauschen 0,04)."""
    if mode == "Zufällig gleichverteilt":
        return rng.random(n)
    if mode == "Gleichabständig":
        x = np.empty(n)
        x[rng.permutation(n)] = np.linspace(0.0, 1.0, n)
        return x
    if mode == "Nach Verbünden ausgerichtet":
        lab = np.arange(n) * blocks // n if labels is None else np.asarray(labels)
        return np.clip((lab + 0.5) / blocks + 0.04 * rng.standard_normal(n), 0.0, 1.0)
    if mode == "Zwei Lager":
        low = np.zeros(n, dtype=bool)
        low[rng.permutation(n)[: n // 2]] = True
        return np.clip(np.where(low, 0.25, 0.75) + 0.04 * rng.standard_normal(n), 0.0, 1.0)
    raise ValueError(f"unbekannter Modus: {mode}")
