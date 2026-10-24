"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

# --- Netztypen -----------------------------------------------------------------------------------------------------------------------------------
T_COMPLETE = "Vollständig (jeder kennt jeden)"
T_RANDOM = "Zufallsnetz"
T_POWER = "Potenzgesetz-Netz"
T_BA = "Skalenfreies Netz (BA)"
T_COMMUNITIES = "Verbünde"
T_RING = "Ring mit Abkürzungen"
T_GRID = "Gitter"
GENERATED_TYPES = (T_RANDOM, T_POWER, T_BA, T_COMMUNITIES, T_RING, T_GRID)
ALL_TYPES = (T_COMPLETE,) + GENERATED_TYPES
BLOCKS = 6

C_MEANING = {
    T_COMPLETE: "ohne Wirkung: im vollständigen Graphen kennt jeder jeden",
    T_RANDOM: "mittlerer Grad des Zufallsnetzes",
    T_POWER: "mittlerer Grad (Gradfolge mit Potenzgesetz-Exponent 2,5, Konfigurationsmodell)",
    T_BA: "zwei Kanten je neuem Knoten, also m = c / 2 gerundet (jeder Knoten hat mindestens m Nachbarn)",
    T_COMMUNITIES: "mittlerer Grad; 80 % der Kanten bleiben im eigenen Verbund (6 Verbünde)",
    T_RING: "Nachbarn auf dem Ring (c gerade gerundet), dazu Abkürzungen mit 5 % je Ringkante",
    T_GRID: "Nachbarschaft: unter 6 vier Nachbarn, 6 bis 7 mit einer Diagonale, ab 8 mit beiden Diagonalen",
}

N_MIN, N_MAX, DEFAULT_N = 40, 200, 100
C_MIN, C_MAX, DEFAULT_C = 3, 12, 6
SEED_MAX, DEFAULT_SEED = 999999, 35
EPS_MIN, EPS_MAX, DEFAULT_EPS = 1, 100, 20         # Vertrauensradius in Prozent der Skala [0, 1]
SWEEP_SEEDS = tuple(range(100000, 100008))         # feste Netze für alle Messreihen: nie ein einzelner Seed als Befund
LIVE_SEEDS = SWEEP_SEEDS[:4]                       # so viele feste Netze je Zelle rechnet die App live (die README-Zahlen nutzen alle acht)

# --- Anfangsverteilungen ---------------------------------------------------------------------------------------------------------------------------
M_RANDOM, M_EQUI, M_COMM, M_CAMPS = "Zufällig gleichverteilt", "Gleichabständig", "Nach Verbünden ausgerichtet", "Zwei Lager"
MODES = (M_RANDOM, M_EQUI, M_COMM, M_CAMPS)
DEFAULT_MODE = M_RANDOM
MODE_HELP = {
    M_RANDOM: "Jeder Betrieb beginnt mit einer zufälligen Zahl zwischen 0 und 1.",
    M_EQUI: "Die Zahlen sind gleich weit voneinander entfernt (0 bis 1) und auf die Betriebe zufällig verteilt.",
    M_COMM: "Jeder Verbund beginnt bei seiner eigenen Mitte (sechs Stufen zwischen 0 und 1) mit kleinem Rauschen; ohne Verbünde im Netz sind es sechs gleich große Nummernblöcke.",
    M_CAMPS: "Die Hälfte der Betriebe beginnt um 0,25, die andere Hälfte um 0,75 (kleines Rauschen).",
}

# --- Messungen -----------------------------------------------------------------------------------------------------------------------------------
TOL = 1e-12                                         # Stillstand: größte Änderung eines Schritts
MAX_STEPS = 20000                                   # Schutz: Obergrenze der Schritte (Gitter bei ε = 0,2 braucht einige Tausend)
FRAMES = 120                                        # Zahl der Bilder im Schritt-Regler und in den Bahnen
BIG_SHARE = 0.05                                    # ein Lager hat mindestens so viel Anteil der Betriebe; kleinere Gruppen heißen Splitter
CONSENSUS_SHARE = 0.99                              # Konsens: das größte Lager hat mindestens so viel Anteil
STAIR_EPS = (0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5)   # Vertrauensradien in Experiment 1
ORDER_EPS = 0.2                                     # Vertrauensradius in Experiment 2 (Ordnung)
IDENTITY_EPS = 2.0                                  # größer als jede Spanne: DeGroot-Fall
LORENZ_N = 400                                      # Betriebe im vollständigen Graphen in Experiment 3
LORENZ_GRID = tuple(round(0.1 + 0.0025 * i, 4) for i in range(61))          # 0,10 bis 0,25
LORENZ_RANDOM_GRID = tuple(round(0.1 + 0.01 * i, 2) for i in range(16))     # 0,10 bis 0,25
LORENZ_RANDOM_RUNS = 12
COMM_N, COMM_C = 240, 12
COMM_INSIDES = (0.5, 0.8, 0.9, 0.95, 0.99)
COMM_EPS = (0.1, 0.25)

# --- Darstellung ---------------------------------------------------------------------------------------------------------------------------------
COLOR_EDGE = "rgba(120,120,120,0.30)"
COLOR_A = "#2F6B65"
COLOR_B = "#c4623b"
COLOR_C = "#6b5b95"
TYPE_COLORS = {T_COMPLETE: "#333333", T_RANDOM: "#2F6B65", T_POWER: "#c4623b", T_BA: "#6b5b95", T_COMMUNITIES: "#9d755d", T_RING: "#4c78a8", T_GRID: "#8c8c8c"}

PRESETS = {
    "Vollständiger Graph: die Treppe (Voreinstellung)": {"netztyp": T_COMPLETE, "n": DEFAULT_N, "c": DEFAULT_C, "seed": DEFAULT_SEED, "eps": DEFAULT_EPS, "mode": DEFAULT_MODE},
    "Dünnes Netz: ein Block und viele Splitter": {"netztyp": T_RANDOM, "n": 150, "c": DEFAULT_C, "seed": DEFAULT_SEED, "eps": 25, "mode": DEFAULT_MODE},
    "Gleichabständig: der Konsens kehrt zurück": {"netztyp": T_COMPLETE, "n": DEFAULT_N, "c": DEFAULT_C, "seed": DEFAULT_SEED, "eps": 19, "mode": M_EQUI},
    "Zwei Lager bleiben": {"netztyp": T_COMPLETE, "n": DEFAULT_N, "c": DEFAULT_C, "seed": DEFAULT_SEED, "eps": 30, "mode": M_CAMPS},
    "Verbünde halten Lager": {"netztyp": T_COMMUNITIES, "n": 120, "c": C_MAX, "seed": DEFAULT_SEED, "eps": 10, "mode": M_COMM},
    "Reihenfolge kehrt sich um": {"netztyp": T_POWER, "n": DEFAULT_N, "c": DEFAULT_C, "seed": DEFAULT_SEED, "eps": 25, "mode": DEFAULT_MODE},
}
PRESET_HELP = {
    "Vollständiger Graph: die Treppe (Voreinstellung)": "Jeder kennt jeden, zufällige Meinungen und Vertrauensradius 20 %: es bleiben zwei Lager (die Treppe: kleiner Radius, viele Lager; bei etwa 25 % meist ein Konsens).",
    "Dünnes Netz: ein Block und viele Splitter": "Im dünnen Zufallsnetz mit Vertrauensradius 25 % bleibt ein großer Block, der Rest sind gestrandete Einzelne, die niemand im Vertrauensradius erreicht.",
    "Gleichabständig: der Konsens kehrt zurück": "Gleich weit verteilte Meinungen im vollständigen Graphen: bei 19 % gibt es Konsens, obwohl bei 20 % zwei Lager bleiben (Lorenz 2006).",
    "Zwei Lager bleiben": "Zwei Lager mit Abstand 0,5 und Vertrauensradius 30 %: sie erreichen einander nie.",
    "Verbünde halten Lager": "Die sechs Verbünde beginnen bei verschiedenen Meinungen: bei Vertrauensradius 10 % bleibt jeder Verbund sein eigenes Lager.",
    "Reihenfolge kehrt sich um": "Im Netz (anders als im vollständigen Graphen) überholen Betriebe einander: die Reihenfolge der Meinungen kehrt sich um.",
}
DEFAULT_PRESET_NAME = "Vollständiger Graph: die Treppe (Voreinstellung)"
