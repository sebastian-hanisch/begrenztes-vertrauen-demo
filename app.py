"""Begrenztes Vertrauen: Lager und Splitter - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Elftes Stück der Reihe „Netzwerkanalyse“ und drittes des Anpassungs-Arms: jeder Betrieb mittelt seine Einschätzung nur mit Partnern, deren Einschätzung höchstens um den Vertrauensradius ε abweicht
(Hegselmann–Krause). Die Demo zeigt, wie viele Lager übrig bleiben, was das Netz ändert (ein Block mit Splittern statt weniger Lager), wo Reihenfolge und „Konsens kehrt zurück“ nicht allgemein gelten
und wann Verbünde Lager halten. Aufbau und Regeln stehen im DEMO-PLAYBOOK.md (§2).

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import bvt_constants as C
from bvt_evaluation import (
    Settings,
    analyse,
    community_rows,
    de,
    lorenz_rows,
    order_rows,
    pct,
    staircase_rows,
    verdict_communities,
    verdict_lorenz,
    verdict_main,
    verdict_order,
    verdict_staircase,
)
from bvt_layout import dunkles_design, kopf_css
from bvt_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from bvt_visualization import build_communities, build_lorenz_equi, build_lorenz_random, build_network, build_order, build_paths, build_staircase

st.set_page_config(page_title="Begrenztes Vertrauen – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _staircase(n, c):
    return staircase_rows(n, c)


@st.cache_data(show_spinner=False)
def _order(n, c):
    return order_rows(n, c)


@st.cache_data(show_spinner=False)
def _lorenz():
    return lorenz_rows()


@st.cache_data(show_spinner=False)
def _communities():
    return community_rows()


def experiment(name, label, key, compute, show, hint):
    """Teure Zusatzansicht erst auf Klick; das Ergebnis bleibt nur für genau diese Einstellungen stehen (Session State)."""
    state_key = f"exp_{name}"
    if st.button(label, key=f"run_{name}", help=hint):
        with st.spinner("Rechne …"):
            result = compute()
        st.session_state[state_key] = (key, result)
    state = st.session_state.get(state_key)
    if state is None:
        st.caption(f"Noch nicht gerechnet. {hint}")
        return
    if state[0] != key:
        st.info("Die Einstellungen haben sich seit der letzten Rechnung geändert. Bitte neu starten.")
        return
    show(state[1])


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in bvt_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🧭 Begrenztes Vertrauen: Lager und Splitter")
st.markdown(
    """
**Elftes Stück** der Reihe „Netzwerkanalyse“ und drittes des **Anpassungs-Arms**: wie in [Stück 9](https://sebastianhanisch-meinungsbildung-demo.streamlit.app/) mitteln die Betriebe ihre Einschätzung, aber **nur mit Partnern, deren Einschätzung nicht zu weit von der eigenen liegt**. Jeder Betrieb schätzt eine Zahl zwischen 0 und 1 (zum Beispiel „wie lange dauert die Umstellung auf das neue Verfahren“) und hört nur auf Partner innerhalb seines **Vertrauensradius ε** (Hegselmann–Krause). Damit ist der Konsens nicht mehr sicher: je nach Radius bleiben ein, zwei oder viele **Lager** übrig.

Die Kernfrage: **Wie viele Lager bleiben, und was ändert das Netz?** Der Hook: im **vollständigen Graphen** (jeder kennt jeden) ist die Zahl der Lager eine Treppe in ε, mit Konsens ab etwa 25 %; im **dünnen Netz** zerfällt die Meinung dagegen in einen großen Block und viele gestrandete **Splitter**, und der Konsens braucht einen viel größeren Radius. Zwei Vermutungen gelten nur eingeschränkt: die **Reihenfolge** der Meinungen bleibt nur im vollständigen Graphen erhalten, und dass der **Konsens bei sinkendem Radius zurückkehrt** (Lorenz 2006), zeigt sich nur bei gleichabständigem Start. Alle Ergebnisse sind **Modellbefunde**, keine Aussagen über die Wirklichkeit; „Polarisierung“ ist hier ein Modellbegriff.

Weiter unten: vier Experimente (**🔬**), der Abschnitt **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert begrenztes Vertrauen", expanded=True):
    st.markdown(
        """
1. **Meinung:** jeder Betrieb hat eine Einschätzung zwischen 0 und 1. Am **Anfang** bestimmen Sie, wie sie verteilt sind.
2. **Ein Schritt:** jeder Betrieb ersetzt seine Meinung durch den **Mittelwert** seiner eigenen und der Meinungen seiner Partner, aber **nur derer, die höchstens um ε abweichen**.
3. **Stillstand:** wenn sich nichts mehr ändert, steht das Netz still. Betriebe mit gleicher Meinung bilden ein **Lager**.
4. **Lager und Splitter:** ein **Lager** ist eine Gruppe mit gleicher Meinung und mindestens 5 % der Betriebe; kleinere Gruppen heißen **Splitter**. **Konsens** heißt: das größte Lager hat mindestens 99 % der Betriebe.
        """
    )
    st.markdown(
        """
| Begriff | Bedeutung hier |
|---|---|
| **Vertrauensradius ε** | größter Meinungsabstand, bei dem ein Betrieb noch auf einen Partner hört |
| **Lager** | Gruppe mit gleicher Endmeinung und mindestens 5 % der Betriebe |
| **Splitter** | Betrieb in einer kleinen Gruppe: im dünnen Netz oft ein Betrieb, den im Radius kein Partner erreicht |
| **Konsens** | das größte Lager hat mindestens 99 % der Betriebe |
| **ε größer als die Spanne** | jeder hört auf alle Partner: das ist die Mittelung aus Stück 9 mit Selbstgewicht 1 / (Partner + 1) |
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um einen Lauf zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Netz**")
    typ = st.selectbox("Netztyp", C.ALL_TYPES, key="netztyp_select", help="Welches Netz erzeugt wird; im vollständigen Graphen kennt jeder jeden.")
    n = st.slider("Betriebe n", *bounds("n_slider"), key="n_slider", help="Zahl der Betriebe (beim Gitter auf ein Quadrat gerundet; ausgewertet wird die größte zusammenhängende Gruppe).")
    c = st.slider("Partner je Betrieb c", *bounds("c_slider"), key="c_slider", help="Was c bedeutet, hängt vom Netztyp ab (siehe darunter).")
    st.caption(C.C_MEANING[typ])
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1, help="Bestimmt das Netz und die zufällige Anfangsverteilung.")
    st.button("🎲 Neuer Lauf", width="stretch", on_click=randomize_seed)
    st.markdown("**Begrenztes Vertrauen**")
    eps = st.slider("Vertrauensradius ε (%)", *bounds("eps_slider"), key="eps_slider", help="Größter Meinungsabstand (in Prozent der Skala von 0 bis 1), bei dem ein Betrieb noch auf einen Partner hört.")
    mode = st.selectbox("Anfangsverteilung", C.MODES, key="mode_select", help="Wie die Meinungen am Anfang verteilt sind.")
    st.caption(C.MODE_HELP[mode])

sync_query_params({"netztyp_select": typ, "n_slider": int(n), "c_slider": int(c), "seed_input": int(seed), "eps_slider": int(eps), "mode_select": mode})

settings = Settings(typ, int(n), int(c), int(seed), int(eps), mode)
with st.spinner("Lasse die Betriebe mitteln …"):
    an = _analysis(settings)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Wie viele Lager bleiben?")
big, largest, splitters, groups = an.camps
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Lager", f"{big}", delta="Konsens" if an.consensus else None, delta_color="off")
m2.metric("Größtes Lager", f"{pct(largest)} %", help="Anteil der Betriebe im größten Lager.")
m3.metric("Splitter", f"{splitters}", help="Betriebe in Gruppen mit weniger als 5 % der Betriebe.")
m4.metric("Gruppen", f"{groups}", help="Zahl aller Gruppen mit gleicher Endmeinung.")
m5.metric("Schritte", f"{an.steps}", delta=None if an.run["converged"] else "Obergrenze", delta_color="off")
steps = sorted(an.run["frames"])
step_key = "step_" + "_".join(str(v) for v in (typ, n, c, seed, eps, mode))
step = st.select_slider("Schritt", options=steps, value=steps[0], key=step_key, help="Blättert durch die Meinungsbildung: ganz links die Anfangsmeinungen, ganz rechts der Stillstand.")
st.markdown("**Das Netz im Lauf** (Farbe: Meinung im gewählten Schritt)")
if an.m < an.inst.n:
    st.caption(f"Ausgewertet wird die größte zusammenhängende Gruppe mit {an.m} von {an.inst.n} Betrieben.")
if an.a.sum() / 2 > 3000:
    st.caption("Der vollständige Graph hat zu viele Kanten für die Zeichnung; die Betriebe stehen auf einem Kreis.")
st.plotly_chart(build_network(an, step), width="stretch", key="net_chart")
st.markdown("**Bahnen der Meinungen über die Schritte** (eine Linie je Betrieb, gefärbt nach Lager des Endzustands; kleine Gruppen grau)")
st.plotly_chart(build_paths(an, step), width="stretch", key="paths_chart")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wie viele Lager bleiben?")
kind, text = verdict_main(an)
getattr(st, kind)(text)
st.caption("Ein einzelner Lauf ist ein Beispiel; die Experimente rechnen über feste Netze.")

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

n_exp, c_exp = settings.n, settings.c
st.subheader("🔬 Experiment 1: Die Treppe und das Netz")
st.caption(f"Lager und größtes Lager über den Vertrauensradius ε = {', '.join(de(e, 2) for e in C.STAIR_EPS)}, zufälliger Start, n = {n_exp}, c = {c_exp}, Median über {len(C.LIVE_SEEDS)} feste Netze je Netztyp (der vollständige Graph hat vier feste Anfangsverteilungen).")


def show_staircase(rows):
    st.markdown("**Lager** (Gruppen mit gleicher Meinung und mindestens 5 % der Betriebe)")
    st.plotly_chart(build_staircase(rows, "camps"), width="stretch", key="stair_camps_chart")
    st.markdown("**Größtes Lager** (Anteil der Betriebe)")
    st.plotly_chart(build_staircase(rows, "largest"), width="stretch", key="stair_largest_chart")
    kind_, text_ = verdict_staircase(rows)
    getattr(st, kind_)(text_)


experiment("staircase", "Treppe messen", (n_exp, c_exp), lambda: _staircase(n_exp, c_exp), show_staircase, "Rechnet 7 Netztypen bei 7 Radien, einige Sekunden.")

st.markdown("---")

st.subheader("🔬 Experiment 2: Bleibt die Reihenfolge? Und die Brücke zu Stück 9")
st.caption(f"Vertrauensradius {de(C.ORDER_EPS, 2)}, zufälliger Start, n = {n_exp}, c = {c_exp}: in wie vielen Läufen kehrt sich die Reihenfolge der Meinungen irgendwann um? Dazu ein Radius über der Spanne ({de(C.IDENTITY_EPS, 0)}): das ist die Mittelung aus Stück 9 mit Selbstgewicht.")


def show_order(res):
    st.plotly_chart(build_order(res), width="stretch", key="order_chart")
    kind_, text_ = verdict_order(res)
    getattr(st, kind_)(text_)


experiment("order", "Reihenfolge prüfen", (n_exp, c_exp), lambda: _order(n_exp, c_exp), show_order, "Rechnet 7 Netztypen mit je vier festen Netzen, wenige Sekunden.")

st.markdown("---")

st.subheader("🔬 Experiment 3: Kehrt der Konsens zurück?")
st.caption(f"Vollständiger Graph mit {C.LORENZ_N} Betrieben. Gleichabständiger Start: die Lager über ε von {de(C.LORENZ_GRID[0], 2)} bis {de(C.LORENZ_GRID[-1], 2)} in Schritten von 0,0025. Zufälliger Start: der Anteil der Läufe mit Konsens ({C.LORENZ_RANDOM_RUNS} Läufe je Radius, Schritte von 0,01).")


def show_lorenz(res):
    st.markdown("**Gleichabständiger Start: Lager über ε** (Rauten: Konsens, der bei einem größeren Radius fehlt)")
    st.plotly_chart(build_lorenz_equi(res), width="stretch", key="lorenz_equi_chart")
    st.markdown("**Zufälliger Start: Läufe mit Konsens über ε**")
    st.plotly_chart(build_lorenz_random(res), width="stretch", key="lorenz_random_chart")
    kind_, text_ = verdict_lorenz(res)
    getattr(st, kind_)(text_)


experiment("lorenz", "Raster messen", "fest", _lorenz, show_lorenz, "Rechnet 61 gleichabständige und 192 zufällige Läufe im vollständigen Graphen, einige Sekunden.")

st.markdown("---")

st.subheader("🔬 Experiment 4: Halten Verbünde Lager?")
st.caption(f"Sechs Verbünde ({C.COMM_N} Betriebe, c = {C.COMM_C}), Anteil der Kanten innerhalb der Verbünde von {pct(C.COMM_INSIDES[0])} % bis {pct(C.COMM_INSIDES[-1])} %, Vertrauensradius {', '.join(de(e, 2) for e in C.COMM_EPS)}; zufälliger Start gegen Start, bei dem jeder Verbund bei seiner eigenen Meinung beginnt. Median über {len(C.LIVE_SEEDS)} feste Netze.")


def show_communities(rows):
    st.plotly_chart(build_communities(rows), width="stretch", key="comm_chart")
    kind_, text_ = verdict_communities(rows)
    getattr(st, kind_)(text_)


experiment("communities", "Verbünde messen", "fest", _communities, show_communities, "Rechnet 20 Zellen mit je vier festen Netzen, etwa fünfzehn Sekunden.")

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Eine Dimension** | Die Meinung ist eine Zahl zwischen 0 und 1. Mit mehreren Dimensionen (mehrere Fragen) entstehen andere Lager, und der Abstand ist anders definiert. | – |
| **Gleicher Vertrauensradius für alle** | Betriebe mit verschiedenem Radius (offene und verschlossene) verändern die Lager. | – |
| **Synchrone Schritte, gleiche Gewichte** | Alle Betriebe mitteln gleichzeitig und gewichten jeden Vertrauten gleich. Mit asynchronen Schritten oder ungleichen Gewichten ändert sich der Verlauf. | – |
| **Festes Netz** | Das Netz ändert sich nicht mit den Meinungen. Wer sich nach Gleichgesinnten umsieht oder Kontakte abbricht, verändert die Struktur. | Stück 12 (Standortwahl) |
| **Lagerzählung hängt an Schwellen** | Ein Lager hat mindestens 5 % der Betriebe, Konsens heißt 99 %, zwei Meinungen gehören zusammen, wenn sie sich um weniger als 10⁻⁶ unterscheiden. Andere Schwellen zählen anders. | – |
| **Stichproben** | Mediane über vier feste Netze in der App (acht in der README); die Streuung zwischen den Netzen ist nicht ausgewiesen. Experiment 3 hängt an der Netzgröße und am Raster. | – |
| **Modellbefund** | Die Demo zeigt Verhalten im Modell, nicht die Wirkung in der Wirklichkeit. Ob der Kontakt mit anderen Meinungen echte Polarisierung verstärkt oder mildert, ist empirisch umstritten (Bail u. a. 2018); wie weit Meinungsmodelle echte Daten treffen, ist offen (Flache u. a. 2017). | – |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Vertraute.** Mit der Nachbarschaftsmatrix $A$ und dem Vertrauensradius $\varepsilon$ ist die Menge der Betriebe, auf die Betrieb $i$ hört,

$$N_i(t) = \{\, j : j = i \ \text{oder}\ A_{ij} = 1,\ |x_j(t) - x_i(t)| \le \varepsilon \,\}$$

**Schritt (Hegselmann–Krause, synchron).** Jeder Betrieb mittelt über seine Vertrauten:

$$x_i(t+1) = \frac{1}{|N_i(t)|} \sum_{j \in N_i(t)} x_j(t)$$

**Stillstand.** Das Netz steht still, wenn $x(t+1) = x(t)$ gilt. Dann haben alle Betriebe, die einander vertrauen, dieselbe Meinung; die Gruppen gleicher Meinung heißen Lager.

**Brücke zu Stück 9.** Ist $\varepsilon$ größer als die Spanne der Anfangsmeinungen, vertraut jeder allen Partnern, und die Iteration ist die Mittelung mit der Matrix $\tilde D^{-1}\tilde A$ mit $\tilde A = A + I$. Der Endwert ist

$$x_\infty = \frac{\sum_i (d_i + 1)\, x_i(0)}{\sum_i (d_i + 1)}$$

**Reihenfolge.** Im vollständigen Graphen bleibt die Reihenfolge der Meinungen erhalten; in einem Netz kann ein Betrieb mit nahen Partnern einen anderen überholen, der nur weit entfernte Partner hat.

**Literatur.**
- Hegselmann, R., Krause, U. (2002): *Opinion Dynamics and Bounded Confidence: Models, Analysis and Simulation.* Journal of Artificial Societies and Social Simulation 5(3).
- Lorenz, J. (2006): *Consensus Strikes Back in the Hegselmann-Krause Model of Continuous Opinion Dynamics Under Bounded Confidence.* Journal of Artificial Societies and Social Simulation 9(1), 8.
- Blondel, V. D., Hendrickx, J. M., Tsitsiklis, J. N. (2009): *On Krause's Multi-Agent Consensus Model With State-Dependent Connectivity.* IEEE Transactions on Automatic Control 54(11), 2586–2597.
- Bail, C. A. u. a. (2018): *Exposure to opposing views on social media can increase political polarization.* Proceedings of the National Academy of Sciences 115(37), 9216–9221.
- Flache, A. u. a. (2017): *Models of Social Influence: Towards the Next Frontiers.* Journal of Artificial Societies and Social Simulation 20(4).
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
