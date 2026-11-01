"""Kennzahlen, Experimente und Verdikte. Jedes Verdikt ist eine reine Funktion (Art, Text); die App ruft st.<Art>(Text)."""

from dataclasses import dataclass
from fractions import Fraction

import ref_algorithm as A
import ref_constants as C
from ref_scenario import Rules, make_rules, random_rules


@dataclass(frozen=True)
class Settings:
    alphabet: str = C.DEFAULT_ALPHABET     # Bezeichnung aus C.ALPHABETS
    patterns: str = C.DEFAULT_PATTERNS     # Eingabetext der Verbotsmuster
    n: int = C.DEFAULT_N


@dataclass(frozen=True, eq=False)
class Analysis:
    settings: Settings
    rules: Rules
    parse_problems: list
    auto: A.Automaton
    rat: A.Rational
    growth: A.Growth
    seq: list                              # a(0), ..., a(n) als ganze Zahlen
    problems: list                         # Meldungen des unabhängigen Prüfers

    @property
    def count(self) -> int:
        return self.seq[-1]


def analyse(settings: Settings) -> Analysis:
    rules, parse_problems = make_rules(settings.alphabet, settings.patterns)
    auto = A.build_automaton(rules)
    rat = A.rational_form(auto)
    growth = A.classify(rat.qr)
    seq = A.sequence(auto, settings.n)
    problems = A.check_rational(auto, rat)
    res = A.residual(rat.qr, growth.roots)
    if res > C.RESIDUAL_WARN:
        problems.append(f"Die Eigenwerte sind ungenau (Rest {res:.1e}); Bild und Wachstumsangaben mit Vorsicht lesen")
    return Analysis(settings, rules, parse_problems, auto, rat, growth, seq, problems)


# ----------------------------------------------------------------------------- Formatierung

_SUPER = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


def de(x: float, digits: int = 2) -> str:
    """Zahl mit deutschem Dezimalkomma."""
    return f"{x:.{digits}f}".replace(".", ",")


def big_text(x: int) -> str:
    """Ganze Zahl lesbar: bis 12 Stellen mit Tausenderpunkt, darüber Mantisse mal Zehnerpotenz mit der Zahl der Stellen (ohne Stringumwandlung der ganzen Zahl)."""
    if x < 10 ** 12:
        return f"{x:,}".replace(",", ".")
    d, lead = A.leading_digits(x, 3)
    s = str(lead)
    return f"{s[0]},{s[1:3]}·10{str(d - 1).translate(_SUPER)} ({d} Stellen)"


def coef_text(c) -> str:
    c = Fraction(c)
    return str(c.numerator) if c.denominator == 1 else f"{c.numerator}/{c.denominator}"


def poly_text(coeffs, var: str = "z") -> str:
    """Polynom aufsteigend als Text: [1, -2, -1, -1] → „1 − 2z − z² − z³“; das Nullpolynom ist „0“."""
    parts = []
    for k, c in enumerate(coeffs):
        c = Fraction(c)
        if c == 0:
            continue
        mag = abs(c)
        body = "" if k > 0 and mag == 1 else coef_text(mag) if mag.denominator == 1 else f"({coef_text(mag)})"
        power = "" if k == 0 else var if k == 1 else var + str(k).translate(_SUPER)
        term = (body + power) or "1"
        parts.append(("−" if c < 0 else "+") + " " + term)
    if not parts:
        return "0"
    first = parts[0]
    text = (first[2:] if first[0] == "+" else "−" + first[2:])
    return " ".join([text] + parts[1:])


def eigenvalue_text(z: complex) -> str:
    """Eigenwert als Text: reell als Dezimalzahl, sonst a ± b i (Imaginärteil unter 1e-9 gilt als 0)."""
    if abs(z.imag) < 1e-9:
        return de(z.real, 4)
    return f"{de(z.real, 4)} {'+' if z.imag >= 0 else '−'} {de(abs(z.imag), 4)} i"


# ----------------------------------------------------------------------------- Probe der Reihe

def series_rows(a: Analysis, count: int = C.SERIES_SHOW) -> list[dict]:
    """Die ersten Glieder: gezählt (Stück 1) und aus dem Bruch P/Q entwickelt; beide müssen gleich sein."""
    k = max(0, min(count, 40) - 1)
    frac = A.series_from_rational(a.rat.pr, a.rat.qr, k)
    counted = A.sequence(a.auto, k)
    return [{"n": n, "gezählt": counted[n], "aus P/Q": frac[n], "gleich": Fraction(counted[n]) == frac[n]} for n in range(k + 1)]


# ----------------------------------------------------------------------------- Kernfrage

def verdict_summary(a: Analysis) -> tuple[str, str]:
    """Was der Nenner verrät: Rekursion, Anlauf, Wachstum und Klasse in einem Satz."""
    rat, g = a.rat, a.growth
    q = poly_text(rat.qr)
    order = (f"Die Rekursion der Ordnung {rat.deg_q} gilt ab n = {rat.valid_from}" +
             ("" if rat.valid_from == rat.deg_q else f"; davor gibt es einen Anlauf, weil der Zähler Grad {rat.deg_p} hat"))
    if g.kind == "endlich":
        return "info", (f"Der Nenner ist {q}: Es gibt keinen Eigenwert, die erzeugende Funktion ist ein Polynom vom Grad {rat.deg_p}. "
                        f"Ab n = {rat.deg_p + 1} gibt es keine gültige Folge mehr.")
    if g.kind == "polynomiell":
        return "info", (f"Der Nenner ist {q}. Der größte Eigenwert hat den Betrag 1: Die Zahl der Folgen wächst höchstens polynomiell. {order}.")
    return "success", (f"Der Nenner ist {q}. Der größte Eigenwert ist λ₁ = {de(g.lam1, 4)}: Mit jedem Zeichen mehr wächst die Zahl der gültigen Folgen auf das {de(g.lam1, 4)}fache "
                       f"(exponentiell). {order}.")


# ----------------------------------------------------------------------------- Experiment 2: ablesen statt raten

def read_experiment(auto: A.Automaton, rat: A.Rational, rmax: int = C.GUESS_RMAX) -> dict:
    """Kleinste Ordnung, die das Raten (Stück 1) findet, gegen die aus dem Bruch gelesene max(Nennergrad, Zählergrad + 1)."""
    reading = rat.valid_from
    if reading > rmax:
        return {"skipped": True, "reading": reading, "deg_q": rat.deg_q, "deg_p": rat.deg_p, "rmax": rmax, "guess": None, "agree": None}
    a = A.sequence(auto, 2 * (rmax + 2) + 40)
    guess, _ = A.smallest_recurrence(a, rmax)
    return {"skipped": False, "reading": reading, "deg_q": rat.deg_q, "deg_p": rat.deg_p, "rmax": rmax, "guess": guess, "agree": guess == reading}


def verdict_read(res: dict) -> tuple[str, str]:
    if res["skipped"]:
        return "info", (f"Aus dem Bruch gelesen wäre die Ordnung {res['reading']}; das Raten wird nur bis Ordnung {res['rmax']} versucht (Bruchrechnung), also bleibt hier nur das Ablesen.")
    base = f"Aus dem Bruch gelesen: Nennergrad {res['deg_q']}, Zählergrad {res['deg_p']}, also gilt die Rekursion ab n = {res['reading']}. "
    if res["guess"] is None:
        return "warning", base + f"Das Raten (Stück 1) findet bis Ordnung {res['rmax']} keine Rekursion."
    if res["agree"]:
        extra = ("" if res["reading"] == res["deg_q"] else
                 f" Das Raten findet Ordnung {res['guess']}, größer als der Nennergrad {res['deg_q']}: Der Zähler macht den Anlauf.")
        return "success", base + f"Das Raten findet als kleinste Ordnung {res['guess']}: gleich der gelesenen." + extra
    return "warning", base + f"Das Raten findet Ordnung {res['guess']}, die gelesene Ordnung ist {res['reading']}: Das darf nicht passieren."


# ----------------------------------------------------------------------------- Experiment 3: Wachstum aus den Eigenwerten

def growth_experiment(auto: A.Automaton, rat: A.Rational) -> dict:
    """Größter Eigenwert gegen den Quotienten a(n)/a(n−1): Fehler über n, erstes n mit Fehler < SPEED_EPS und die Faustformel dazu."""
    g = A.classify(rat.qr)
    a = A.sequence(auto, C.SPEED_N_MAX + C.OSC_N // 30)
    out = {"growth": g, "residual": A.residual(rat.qr, g.roots), "errors": [], "first_n": None, "estimate": None, "spread": A.ratio_spread(a)}
    if g.kind == "exponentiell":
        out["errors"] = [(n, A.ratio_error(a, g.lam1, n)) for n in range(2, C.RATIO_ERROR_N + 1)]
        out["first_n"] = A.first_n_within(a, g.lam1, C.SPEED_EPS, C.SPEED_N_MAX)
        out["estimate"] = A.speed_estimate(g.ratio2)
    return out


def verdict_growth(res: dict) -> tuple[str, str]:
    g = res["growth"]
    if g.kind == "endlich":
        return "info", "Die Folge ist endlich: Es gibt keinen Eigenwert, der Quotient a(n)/a(n−1) ist nach dem letzten Glied nicht definiert."
    if g.kind == "polynomiell":
        return "info", ("Der größte Eigenwert hat den Betrag 1, die Folge wächst höchstens polynomiell: Der Quotient a(n)/a(n−1) nähert sich 1, "
                        "wie schnell, hängt vom Grad des Polynoms ab, den diese Demo nicht liest.")
    text = f"Der größte Eigenwert ist {de(g.lam1, 6)}; der zweitgrößte hat den Betrag {de(g.ratio2 * g.lam1, 4)}, das Verhältnis ist {de(g.ratio2, 4)}. " if g.ratio2 is not None else ""
    if res["first_n"] is None:
        text += f"Der Quotient liegt bis n = {C.SPEED_N_MAX} nicht auf {C.SPEED_EPS:.0e} genau am Eigenwert"
        if res["spread"] is not None and res["spread"] > C.OSC_TOL:
            text += ": Er schwingt, weil mehrere Eigenwerte denselben Betrag haben."
        else:
            text += "."
        return "warning", text
    text += f"Der Quotient a(n)/a(n−1) ist ab n = {res['first_n']} auf {C.SPEED_EPS:.0e} genau am Eigenwert."
    if res["estimate"] is not None:
        text += f" Die Faustformel ln({C.SPEED_EPS:.0e}) / ln(Verhältnis) sagt {de(res['estimate'], 1)} voraus: nur eine grobe Abschätzung, die Konstante vor dem Abklingen fehlt."
    return "success", text


# ----------------------------------------------------------------------------- Experiment 4: Stellenzahl ohne Zählen

def digits_experiment(auto: A.Automaton, rat: A.Rational, sizes=C.DIGIT_SIZES) -> dict:
    """Stellenzahl von a(n) aus λ₁ und c vorhergesagt gegen die gezählte (nur bei exponentiellem Wachstum)."""
    g = A.classify(rat.qr)
    out = {"kind": g.kind, "lam1": g.lam1, "rows": []}
    if g.kind != "exponentiell":
        return out
    ref = A.sequence(auto, C.DIGIT_REF_N)
    for n in sizes:
        exact = A.digit_count(A.sequence(auto, n)[-1])
        out["rows"].append({"n": n, "predicted": A.predict_digits(ref, g.lam1, n), "exact": exact})
    return out


def verdict_digits(res: dict) -> tuple[str, str]:
    if res["kind"] != "exponentiell":
        return "info", "Ohne exponentielles Wachstum gibt es hier nichts vorherzusagen: Die Stellenzahl wächst nur logarithmisch oder gar nicht."
    hits = sum(1 for r in res["rows"] if r["predicted"] == r["exact"])
    parts = "; ".join(f"n = {r['n']}: vorhergesagt {r['predicted']}, gezählt {r['exact']}" for r in res["rows"])
    kind = "success" if hits == len(res["rows"]) else "warning"
    tail = "Beide stimmen." if kind == "success" else f"{len(res['rows']) - hits} von {len(res['rows'])} weichen ab."
    return kind, f"Aus λ₁ = {de(res['lam1'], 6)} und der Konstanten c (aus a({C.DIGIT_REF_N})): {parts}. {tail}"


# ----------------------------------------------------------------------------- Experiment 5: Wachstumsklassen

def class_experiment(count: int = C.CLASS_SETS, seed_base: int = C.CLASS_SEED_BASE) -> dict:
    """Klasse aus den Eigenwerten gegen Klasse aus der gezählten Folge (n = 200 bis 400) über `count` Zufallsregelsätze mit festen Seeds."""
    from_roots, from_seq, match = {}, {}, 0
    mismatches, multi_dominant, oscillating = [], 0, 0
    for seed in range(seed_base, seed_base + count):
        rules = random_rules(seed)
        auto = A.build_automaton(rules)
        rat = A.rational_form(auto)
        g = A.classify(rat.qr)
        kind_seq, a = A.classify_sequence(auto)
        from_roots[g.kind] = from_roots.get(g.kind, 0) + 1
        from_seq[kind_seq] = from_seq.get(kind_seq, 0) + 1
        if g.kind == kind_seq:
            match += 1
        else:
            mismatches.append(seed)
        multi_dominant += g.dominant > 1
        if kind_seq != "endlich":
            spread = A.ratio_spread(a)
            oscillating += spread is not None and spread > C.OSC_TOL
    return {"count": count, "from_roots": from_roots, "from_seq": from_seq, "match": match, "mismatches": mismatches,
            "multi_dominant": multi_dominant, "oscillating": oscillating}


def verdict_classes(res: dict) -> tuple[str, str]:
    fr = res["from_roots"]
    counts = ", ".join(f"{fr.get(k, 0)} {k}" for k in ("exponentiell", "polynomiell", "endlich"))
    text = (f"Von {res['count']} Zufallsregelsätzen: {counts}. Aus den Eigenwerten und aus der gezählten Folge ergibt sich bei {res['match']} dieselbe Klasse. "
            f"{res['multi_dominant']} Sätze haben mehrere Eigenwerte mit dem größten Betrag, bei {res['oscillating']} schwingt der Quotient a(n+1)/a(n) bei n = {C.OSC_N}.")
    if res["mismatches"]:
        return "warning", text + f" Abweichende Seeds: {', '.join(map(str, res['mismatches'][:5]))}."
    return "success", text


# ----------------------------------------------------------------------------- Spielwiese: wie weit trägt die Reihe?

def probe(a: Analysis, t: float, terms: int = C.PROBE_TERMS) -> dict:
    """Teilsumme Σ a(k) z₀ᵏ (k < terms) gegen den Bruch P(z₀)/Q(z₀) an z₀ = t / λ₁ (ohne exponentielles Wachstum: z₀ = t)."""
    g = a.growth
    z0 = t / g.lam1 if g.kind == "exponentiell" else t
    seq = A.sequence(a.auto, terms - 1)
    partial = sum(float(x) * z0 ** k for k, x in enumerate(seq))
    q = float(A.poly_eval(a.rat.qr, z0))
    p = float(A.poly_eval(a.rat.pr, z0))
    exact = None if abs(q) < 1e-12 else p / q
    return {"t": t, "z0": z0, "partial": partial, "exact": exact, "terms": terms, "radius": (1 / g.lam1) if g.kind == "exponentiell" else (1.0 if g.kind == "polynomiell" else None)}


def verdict_probe(res: dict) -> tuple[str, str]:
    r = res["radius"]
    if res["exact"] is None:
        return "warning", f"An z = {de(res['z0'], 4)} hat der Nenner eine Nullstelle: Der Bruch ist dort nicht definiert, die Teilsumme ({res['partial']:.4g}) wächst mit jedem Glied."
    rel = abs(res["partial"] - res["exact"]) / max(abs(res["exact"]), 1e-12)
    if r is not None and abs(res["z0"]) >= r:
        return "warning", (f"z = {de(res['z0'], 4)} liegt nicht innerhalb des Konvergenzradius {de(r, 4)} (kleinste Nullstelle von Q): Die Reihe konvergiert nicht, "
                           f"die Teilsumme {res['partial']:.4g} sagt nichts über den Bruchwert {res['exact']:.4g}.")
    if rel < 1e-6:
        return "success", f"Innerhalb des Konvergenzradius: Teilsumme {res['partial']:.6g}, Bruch {res['exact']:.6g}, relative Abweichung {rel:.1e}."
    return "info", f"Teilsumme {res['partial']:.6g}, Bruch {res['exact']:.6g}, relative Abweichung {rel:.1e}: Die Reihe ist mit {res['terms']} Gliedern noch nicht eingeschwungen."


def recurrence_text(qr) -> str:
    """Die lineare Rekursion aus dem gekürzten Nenner: a(n) = −Σ_{j ≥ 1} Q[j]·a(n−j); Grad 0 (endliche Folge) gibt „a(n) = 0“."""
    parts = []
    for j in range(1, len(qr)):
        c = -Fraction(qr[j])
        if c == 0:
            continue
        mag = abs(c)
        factor = "" if mag == 1 else (coef_text(mag) + "·" if mag.denominator == 1 else f"({coef_text(mag)})·")
        parts.append(("−" if c < 0 else "+") + " " + factor + f"a(n−{j})")
    if not parts:
        return "a(n) = 0"
    first = parts[0]
    return "a(n) = " + (first[2:] if first[0] == "+" else "−" + first[2:]) + ("" if len(parts) == 1 else " " + " ".join(parts[1:]))


def check_points_table(a: Analysis) -> list[dict]:
    """Q an drei Stellen: aus den Koeffizienten und als Determinante von I − z·M (Gauß-Elimination mit Brüchen); beide müssen gleich sein."""
    rows = []
    for num, den in C.CHECK_POINTS:
        z = Fraction(num, den)
        from_poly = A.poly_eval([Fraction(c) for c in a.rat.q], z)
        det = A.det_at(a.rat.matrix, z)
        rows.append({"z": f"{num}/{den}" if den != 1 else str(num), "Q(z)": coef_text(from_poly), "det(I − zM)": coef_text(det), "gleich": from_poly == det})
    return rows
