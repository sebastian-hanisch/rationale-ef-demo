"""Rationale erzeugende Funktion – der Nenner verrät es - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 2 der Reihe „Abzählen und erzeugende Funktionen“: Die Zustandsrekursion aus Stück 1 ist eine rationale Funktion A(z) = P(z)/Q(z) mit Q(z) = det(I − zM).
Aus dem gekürzten Bruch liest die Demo Rekursion, Anlauf, Wachstum, Stellenzahl und Wachstumsklasse ab, statt zu raten oder zu zählen.
Aufbau und Regeln: DEMO-PLAYBOOK.md (§2).

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import ref_algorithm as A
import ref_constants as C
from ref_evaluation import (
    Settings,
    analyse,
    big_text,
    check_points_table,
    class_experiment,
    de,
    digits_experiment,
    eigenvalue_text,
    growth_experiment,
    poly_text,
    probe,
    read_experiment,
    recurrence_text,
    series_rows,
    verdict_classes,
    verdict_digits,
    verdict_growth,
    verdict_probe,
    verdict_read,
    verdict_summary,
)
from ref_layout import dunkles_design, kopf_css
from ref_pdf_export import build_pdf
from ref_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    sidebar_presets,
    sync_query_params,
)
from ref_scenario import make_rules
from ref_visualization import build_classes, build_ratio_error, build_roots

st.set_page_config(page_title="Rationale erzeugende Funktion – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


def _core(alphabet, patterns):
    auto = A.build_automaton(make_rules(alphabet, patterns)[0])
    return auto, A.rational_form(auto)


@st.cache_data(show_spinner=False)
def _read(alphabet, patterns):
    return read_experiment(*_core(alphabet, patterns))


@st.cache_data(show_spinner=False)
def _growth(alphabet, patterns):
    return growth_experiment(*_core(alphabet, patterns))


@st.cache_data(show_spinner=False)
def _digits(alphabet, patterns):
    return digits_experiment(*_core(alphabet, patterns))


@st.cache_data(show_spinner=False)
def _classes():
    return class_experiment()


def verdict(pair):
    kind, text = pair
    getattr(st, kind)(text)


def state_name(z):
    return "Start" if z == "" else z


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in ref_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🧩 Rationale erzeugende Funktion – der Nenner verrät es")
st.markdown(
    """
**Was steckt in der Zählfolge?** In Stück 1 hat die Rekursion über einen **Zustand** die Folgen gezählt. Fasst man alle Zahlen a(0), a(1), a(2), … zu einer **erzeugenden Funktion** zusammen,
ist sie ein **Bruch aus zwei Polynomen**: A(z) = P(z) / Q(z). Der **Nenner** Q(z) = det(I − zM) lässt sich aus der Übergangsmatrix M **ohne Zählen** ausrechnen und verrät die
**Rekursion** (statt sie zu raten), den **Anlauf** (der Zähler), das **Wachstum** (der größte Eigenwert) und sogar die **Stellenzahl** weit entfernter Glieder.

Weiter unten: **fünf Experimente** (**🔬**), eine **🎲 Spielwiese**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert der Bruch", expanded=True):
    st.markdown(
        """
1. **Übergangsmatrix M:** Der Automat aus Stück 1 hat Zustände; M[i][j] zählt, wie viele Zeichen von Zustand i nach Zustand j führen (verbotene Übergänge zählen nicht).
2. **Nenner:** Q(z) = det(I − zM). Das ist ein Polynom, dessen Koeffizienten man aus den Spuren der Potenzen von M ausrechnet, ohne eine einzige Folge zu zählen.
3. **Zähler:** P(z) ist das, was übrig bleibt, wenn man Q(z) mit der Reihe a(0) + a(1)z + a(2)z² + … malnimmt; es hat höchstens Grad (Zustandszahl − 1). Danach kürzen.
4. **Ablesen:** Q liefert die Rekursion a(n) = −Q₁·a(n−1) − Q₂·a(n−2) − …, gültig ab n = max(Nennergrad, Zählergrad + 1). Die Nullstellen von Q liefern das Wachstum: a(n) wächst wie λ₁ⁿ, wobei λ₁ der größte Eigenwert ist.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Regeln** (dieselben wie in Stück 1)")
    alphabet = st.selectbox("Alphabet", list(C.ALPHABETS), key="alphabet_select", help="Die Zeichen, aus denen die Folgen bestehen.")
    patterns = st.text_input("Verbotene Teilfolgen", key="patterns_input", max_chars=C.PATTERN_TEXT_MAX,
                             help=f"Durch Komma getrennt, nur Zeichen des Alphabets, höchstens {C.PATTERN_MAX_COUNT} Muster mit je höchstens {C.PATTERN_MAX_LEN} Zeichen. "
                                  "Beispiel „NF, NNN“: nie Früh direkt nach Nacht, nie drei Nächte hintereinander.")
    n = st.slider("Länge n", *bounds("n_slider"), key="n_slider", help="Wie viele Glieder der Zahlenfolge die Probe und die Anzahl unten zeigen.")

sync_query_params({"alphabet_select": alphabet, "patterns_input": patterns, "n_slider": int(n)})

settings = Settings(alphabet, patterns, int(n))
a = _analysis(settings)
for message in a.parse_problems:
    st.warning(message)
if a.problems:   # unabhängiger Prüfer, nicht nur im Test: lieber eine Fehlermeldung als eine stille falsche Zahl
    st.error("Der Bruch besteht den Prüfer nicht: " + "; ".join(a.problems))

rat, g = a.rat, a.growth
alphabet_key, patterns_key = a.settings.alphabet, ", ".join(a.rules.patterns)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Zustände", f"{a.auto.size}", help="Größe der Übergangsmatrix M.")
m2.metric("Grad des Nenners (gekürzt)", f"{rat.deg_q}", help="Ordnung der kleinsten linearen Rekursion für die Zahlenfolge.")
m3.metric("Grad des Zählers (gekürzt)", f"{rat.deg_p}", help="Ist er mindestens so groß wie der Nennergrad, gibt es einen Anlauf: Die Rekursion gilt erst ab Zählergrad + 1.")
m4.metric("Größter Eigenwert λ₁", "–" if g.lam1 is None else de(g.lam1, 4),
          help=f"Wachstumsfaktor pro Zeichen. Klasse: {g.kind}. Der größte Eigenwert ist der Kehrwert der kleinsten Nullstelle des Nenners.")
st.plotly_chart(build_roots(g), width="stretch", key="main_chart")
st.caption("Die Eigenwerte λ (Nullstellen von λ^d · Q(1/λ)) in der komplexen Ebene. Ihr Betrag bestimmt das Wachstum: Betrag über 1 heißt exponentiell, genau 1 polynomiell. "
           "Rot: der größte Betrag (kann mehrfach vorkommen). Gestrichelt: Betrag 1.")

st.markdown("### Der Bruch")
st.markdown(f"**Nenner:** Q(z) = {poly_text(rat.qr)}  \n**Zähler:** P(z) = {poly_text(rat.pr)}  \n**Rekursion:** {recurrence_text(rat.qr)}, gültig ab n = {rat.valid_from}")
if (len(A.trim(rat.q)) - 1, len(rat.p) - 1) != (rat.deg_q, rat.deg_p):
    st.caption(f"Vor dem Kürzen: Q hatte Grad {len(A.trim(rat.q)) - 1}, P hatte Grad {len(rat.p) - 1}.")

with st.expander("Übergangsmatrix M anzeigen"):
    st.dataframe(
        [{"von \\ nach": state_name(z), **{state_name(w): rat.matrix[i][j] for j, w in enumerate(a.auto.states)}} for i, z in enumerate(a.auto.states)],
        hide_index=True, width="stretch",
    )

if st.button("📄 PDF der aktuellen Regeln erstellen", key="pdf_make"):
    st.session_state["pdf_made"] = (settings, build_pdf(a))
made = st.session_state.get("pdf_made")
if made and made[0] == settings:
    st.download_button("⬇️ PDF herunterladen", data=made[1], file_name="erzeugende-funktion.pdf", mime="application/pdf", key="pdf_download")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Was verrät der Nenner, ohne dass man zählt?")
verdict(verdict_summary(a))

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 1: Von der Matrix zum Bruch")
st.caption(f"Die ersten {C.SERIES_SHOW} Glieder: gezählt (Rekursion über Zustände, Stück 1) und aus dem Bruch P/Q entwickelt. Darunter die unabhängige Probe für Q: "
           "die Determinante von I − zM an drei Stellen, mit Brüchen durch Gauß-Elimination gerechnet.")
st.dataframe([{"n": r["n"], "gezählt": big_text(r["gezählt"]), "aus P/Q": big_text(int(r["aus P/Q"])) if r["aus P/Q"].denominator == 1 else str(r["aus P/Q"]),
               "gleich": "ja" if r["gleich"] else "nein"} for r in series_rows(a)], hide_index=True, width="stretch")
st.dataframe([{**r, "gleich": "ja" if r["gleich"] else "nein"} for r in check_points_table(a)], hide_index=True, width="stretch")
if a.problems:
    st.error("Die Probe schlägt fehl: " + "; ".join(a.problems))
else:
    st.success(f"Die Reihe aus dem Bruch stimmt für n = 0 bis {C.CHECK_N} mit der Zählung überein, und Q stimmt an {len(C.CHECK_POINTS)} Stellen mit der Determinante überein.")

st.markdown("---")

st.subheader("🔬 Experiment 2: Rekursion ablesen statt raten")
st.caption(f"Stück 1 (Experiment 4) hat die Rekursion aus den ersten Gliedern geraten und oft eine größere Ordnung gefunden als erwartet. Hier die Erklärung: "
           f"Die kleinste geratene Ordnung ist max(Nennergrad, Zählergrad + 1). Das Raten wird nur bis Ordnung {C.GUESS_RMAX} versucht.")
read_res = _read(alphabet_key, patterns_key)
st.dataframe([{"Nennergrad": read_res["deg_q"], "Zählergrad": read_res["deg_p"], "gelesen: max(Nenner, Zähler + 1)": read_res["reading"],
               "geraten (kleinste Ordnung)": "nicht versucht" if read_res["skipped"] else ("keine" if read_res["guess"] is None else read_res["guess"])}],
             hide_index=True, width="stretch")
verdict(verdict_read(read_res))

st.markdown("---")

st.subheader("🔬 Experiment 3: Wachstum aus den Eigenwerten")
st.caption(f"Der größte Eigenwert gegen den Quotienten a(n)/a(n−1): relativer Fehler über n. Die Geschwindigkeit des Einschwingens hängt am **zweitgrößten** Eigenwert. "
           f"Gemessen wird bis n = {C.SPEED_N_MAX}.")
growth_res = _growth(alphabet_key, patterns_key)
st.dataframe([{"Eigenwert": eigenvalue_text(z), "Betrag": de(abs(z), 6)} for z in growth_res["growth"].roots] or [{"Eigenwert": "keiner (Nenner 1)", "Betrag": "–"}],
             hide_index=True, width="stretch")
if growth_res["errors"]:
    st.plotly_chart(build_ratio_error(growth_res["errors"]), width="stretch", key="ratio_chart")
verdict(verdict_growth(growth_res))

st.markdown("---")

st.subheader("🔬 Experiment 4: Stellenzahl ohne Zählen")
st.caption(f"Aus λ₁ und der Konstanten c (aus a({C.DIGIT_REF_N})) wird die Stellenzahl von a(n) vorhergesagt: ⌊n·log₁₀ λ₁ + log₁₀ c⌋ + 1. Verglichen mit der gezählten Stellenzahl bei n = "
           f"{' und '.join(str(x) for x in C.DIGIT_SIZES)}.")
digits_res = _digits(alphabet_key, patterns_key)
if digits_res["rows"]:
    st.dataframe([{"n": r["n"], "vorhergesagt": r["predicted"], "gezählt": r["exact"], "gleich": "ja" if r["predicted"] == r["exact"] else "nein"} for r in digits_res["rows"]],
                 hide_index=True, width="stretch")
verdict(verdict_digits(digits_res))

st.markdown("---")

st.subheader("🔬 Experiment 5: Wachstumsklassen über Zufallsregelsätze")
st.caption(f"{C.CLASS_SETS} Zufallsregelsätze (feste Seeds ab {C.CLASS_SEED_BASE}, A, B oder A, B, C, 1 bis 4 Verbote der Länge 1 bis 4). Klasse aus den Eigenwerten gegen Klasse aus der "
           f"gezählten Folge (Steigung von ln a(n) zwischen n = {C.CLASS_N_LOW} und {C.CLASS_N_HIGH}). Rechnet einige Sekunden.")
if st.button("🔬 Experiment 5 rechnen", key="class_run"):
    st.session_state["class_res"] = _classes()
class_res = st.session_state.get("class_res")
if class_res:
    st.plotly_chart(build_classes(class_res), width="stretch", key="class_chart")
    verdict(verdict_classes(class_res))
else:
    st.info("Noch nicht gerechnet.")

st.markdown("---")

# --- Spielwiese ----------------------------------------------------------------------------------------------------------------------------

st.subheader("🎲 Spielwiese: Wie weit trägt die Reihe?")
st.caption(f"Die Teilsumme der ersten {C.PROBE_TERMS} Glieder, Σ a(k)·zᵏ, gegen den Bruch P(z)/Q(z) an z = t/λ₁ (bei Klasse polynomiell oder endlich: z = t). "
           "Bei t < 1 stimmen beide überein, bei t ≥ 1 liegt z an oder hinter der kleinsten Nullstelle von Q und die Reihe konvergiert nicht.")
t = st.slider("t (Anteil des Konvergenzradius)", 0.1, 1.5, 0.5, 0.05, key="probe_t")
verdict(verdict_probe(probe(a, float(t))))

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    f"""
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Nur Regeln mit endlichem Automaten** | Die erzeugende Funktion ist nur dann ein Bruch aus Polynomen, wenn der Zustand klein und endlich bleibt. Bei Strukturen mit Verschachtelung (Klammern, Bäume) ist sie es nicht (Catalan-Zahlen). | Stück 3 der Reihe: symbolische Methode |
| **Wachstum nur aus dem größten Eigenwert** | Bei mehreren Eigenwerten mit gleichem Betrag schwingt der Quotient, bei mehrfachen kommt ein polynomieller Faktor dazu; diese Demo liest nur die Klasse, nicht den Grad. | Stück 9 der Reihe: Asymptotik |
| **Nullstellen sind Näherungen** | Durand–Kerner liefert Näherungen; die App warnt, wenn der Rest über {C.RESIDUAL_WARN:.0e} liegt. Mehrfachnullstellen konvergieren langsamer. | – |
| **Einschwingtempo nur als Faustregel** | ln(ε)/ln(Verhältnis der Eigenwerte) lässt die Konstante vor dem Abklingen weg und kann um ein Drittel danebenliegen. | – |
| **Wachstumsklassen aus einer Schwelle** | Polynomiell und exponentiell trennt die Steigung von ln a(n) bei {C.CLASS_SLOPE}; das gilt für diese kleinen Automaten, nicht allgemein. | – |
| **Schichtfolgen sind nur der Rahmen** | Echte Dienstplanung ist ein Optimierungsproblem; hier wird nur gezählt. | – |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Problem.** Wie in Stück 1: ein Alphabet und verbotene Teilfolgen, $a(n)$ die Zahl der Wörter der Länge $n$ ohne Verbot. Der Automat hat die Zustandsmenge $Z$ mit $|Z| = s$ und die Übergangsmatrix $M \in \mathbb{N}^{s \times s}$ ($M_{zt}$ = Zahl der Zeichen von $z$ nach $t$).

**Zahl der Wörter als Matrixpotenz.** $a(n) = e_0^{\top} M^n \mathbf{1}$ ($e_0$ der Startzustand, $\mathbf{1}$ der Vektor aus Einsen).

**Erzeugende Funktion.** $A(z) = \sum_{n \ge 0} a(n) z^n = e_0^{\top} (I - zM)^{-1} \mathbf{1} = \dfrac{P(z)}{Q(z)}$ mit $Q(z) = \det(I - zM)$ und $\deg P < s$ (Cramersche Regel: $P$ ist die Summe der Einträge der ersten Zeile von $\operatorname{adj}(I - zM)$).

**Nenner ohne Zählen.** $Q(z) = \sum_{k=0}^{s} c_k z^k$ mit $c_0 = 1$ und $c_k = -\frac{1}{k}\operatorname{tr}(M M_k)$ nach Faddeev–LeVerrier ($M_1 = I$, $M_{k+1} = M M_k + c_k I$); alle $c_k$ sind ganze Zahlen.

**Rekursion.** Aus $Q(z) A(z) = P(z)$ folgt für $n > \deg P$: $a(n) = -\sum_{j=1}^{d} q_j\, a(n-j)$ mit $d = \deg Q$ (gekürzt, $q_0 = 1$). Gilt $\deg P \ge d$, gibt es einen Anlauf: Die Rekursion gilt erst ab $n = \deg P + 1$. Gemessen: Die kleinste Rekursion der Ordnung $r$, die ab $n = r$ alle Glieder trifft (Stück 1, Raten), hat $r = \max(d, \deg P + 1)$.

**Wachstum.** Die Eigenwerte $\lambda_i$ sind die Nullstellen von $\lambda^d Q(1/\lambda)$, die Pole von $A$ liegen bei $z = 1/\lambda_i$. Für nichtnegative Matrizen ist der Spektralradius $\lambda_1 = \rho(M)$ selbst ein Eigenwert (Perron–Frobenius), und $a(n)$ wächst wie $c \lambda_1^n$ (bei einfachem dominantem Eigenwert) mit einem Fehler der Ordnung $(|\lambda_2|/\lambda_1)^n$ im Quotienten $a(n+1)/a(n)$. Stellenzahl: $\lfloor n \log_{10} \lambda_1 + \log_{10} c \rfloor + 1$.

**Literatur** (Titel und Fundstelle aus dem Gedächtnis, nicht eingesehen).
R. P. Stanley: *Enumerative Combinatorics, Volume 1*, 2. Auflage, Cambridge University Press 2012, Kapitel 4 (rationale erzeugende Funktionen und lineare Rekursionen mit konstanten Koeffizienten).
P. Flajolet und R. Sedgewick: *Analytic Combinatorics*, Cambridge University Press 2009, Kapitel I und IV (symbolische Methode, Singularitätsanalyse, rationale Funktionen).
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
