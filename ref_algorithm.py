"""Kern der Demo (nur Standardbibliothek): die Zustandsrekursion aus Stück 1 als rationale erzeugende Funktion A(z) = P(z) / Q(z).

Jede Regel ist eine eigene Funktion mit expliziten Ein- und Ausgaben (DEMO-PLAYBOOK §1b):
`build_automaton` und `sequence` sind der Automat und die Zahlenfolge aus Stück 1, `transfer_matrix` und `q_polynomial` leiten den Nenner ab (Faddeev–LeVerrier mit
ganzen Zahlen), `rational_form` kürzt den Bruch, `dk_roots` sucht die Eigenwerte (Durand–Kerner), `classify` liest die Wachstumsklasse ab, `det_at` ist der
unabhängige Prüfer (Gauß-Elimination mit Brüchen) für Q. Polynome sind Listen von Koeffizienten, aufsteigend (Index = Potenz von z)."""

import math
from dataclasses import dataclass
from fractions import Fraction

import ref_constants as C
from ref_scenario import Rules


# ----------------------------------------------------------------------------- Automat und Zahlenfolge (wie in Stück 1)

@dataclass(frozen=True, eq=False)
class Automaton:
    alphabet: str
    states: tuple[str, ...]                          # erreichbare Zustände, kürzeste zuerst, leeres Wort = Startzustand
    trans: dict                                      # (Zustand, Zeichen) -> Folgezustand oder None (Verbot)

    @property
    def size(self) -> int:
        return len(self.states)


def build_automaton(rules: Rules) -> Automaton:
    """Zustand = längstes Ende des bisher gelesenen Wortes, das ein echter Anfang eines Verbots ist (leeres Wort inklusive)."""
    for p in rules.patterns:
        if not p or set(p) - set(rules.alphabet):
            raise ValueError(f"ungültiges Verbotsmuster {p!r}")
    prefixes = {p[:i] for p in rules.patterns for i in range(len(p))}

    def step(state: str, c: str):
        t = state + c
        if any(t.endswith(p) for p in rules.patterns):
            return None
        for i in range(len(t) + 1):
            if t[i:] in prefixes:
                return t[i:]
        return ""

    reached = {""}
    todo = [""]
    trans = {}
    while todo:
        z = todo.pop()
        for c in rules.alphabet:
            t = step(z, c)
            trans[(z, c)] = t
            if t is not None and t not in reached:
                reached.add(t)
                todo.append(t)
    return Automaton(rules.alphabet, tuple(sorted(reached, key=lambda s: (len(s), s))), trans)


def sequence(auto: Automaton, n: int, number=int) -> list:
    """a(0), ..., a(n): Zahl der gültigen Wörter jeder Länge. `number` ist int (exakt) oder float."""
    if n < 0:
        raise ValueError("n darf nicht negativ sein")
    vec = {z: number(0) for z in auto.states}
    vec[""] = number(1)
    out = [number(1)]
    for _ in range(n):
        new = {z: number(0) for z in auto.states}
        for z, w in vec.items():
            if w == 0:
                continue
            for c in auto.alphabet:
                t = auto.trans[(z, c)]
                if t is not None:
                    new[t] += w
        vec = new
        out.append(sum(vec.values()))
    return out


def count_matrix(auto: Automaton, n: int) -> int:
    """a(n) als Matrixpotenz der Übergangsmatrix (ganze Zahlen): zweiter Rechenweg neben `sequence`."""
    if n < 0:
        raise ValueError("n darf nicht negativ sein")
    m = transfer_matrix(auto)
    size = len(m)
    result = [[int(i == j) for j in range(size)] for i in range(size)]
    base, e = m, n
    while e:
        if e & 1:
            result = _mat_mul(result, base)
        base = _mat_mul(base, base)
        e >>= 1
    return sum(result[0])


def digit_count(x: int) -> int:
    """Zahl der Dezimalstellen einer ganzen Zahl x ≥ 0, ohne sie in einen String zu wandeln (Python begrenzt die Umwandlung auf 4300 Stellen)."""
    if x < 0:
        raise ValueError("x darf nicht negativ sein")
    d = max(1, int(x.bit_length() * 0.30102999566398))
    while 10 ** d <= x:
        d += 1
    while d > 1 and 10 ** (d - 1) > x:
        d -= 1
    return d


def leading_digits(x: int, count: int) -> tuple[int, int]:
    """(Zahl der Stellen von x, die ersten `count` Stellen als ganze Zahl; x selbst, wenn es nicht länger ist). Ohne Umwandlung in einen String."""
    d = digit_count(x)
    return d, (x if d <= count else x // 10 ** (d - count))


def log10_int(x: int) -> float:
    """log10 einer positiven ganzen Zahl beliebiger Größe (float(x) liefe ab 1e308 über)."""
    if x <= 0:
        raise ValueError("x muss positiv sein")
    d, lead = leading_digits(x, 15)
    return d - digit_count(lead) + math.log10(lead)


def growth_ratio(a: list[int], digits: int = 12) -> float | None:
    """a(n) / a(n-1) für die letzten beiden Glieder, auch für riesige ganze Zahlen; None ohne Vorgänger oder bei a(n-1) = 0."""
    if len(a) < 2 or a[-2] == 0:
        return None
    scale = 10 ** digits
    return (a[-1] * scale // a[-2]) / scale


def solve_recurrence(a: list[int], r: int):
    """Koeffizienten c_1..c_r mit a(n) = Σ c_j a(n−j) aus den Gliedern a(0)..a(2r−1) (Brüche); None, wenn das System singulär ist (Raten aus Stück 1)."""
    if r < 1 or len(a) < 2 * r:
        return None
    m = [[Fraction(a[n - j]) for j in range(1, r + 1)] + [Fraction(a[n])] for n in range(r, 2 * r)]
    for i in range(r):
        p = next((k for k in range(i, r) if m[k][i] != 0), None)
        if p is None:
            return None
        m[i], m[p] = m[p], m[i]
        d = m[i][i]
        m[i] = [x / d for x in m[i]]
        for k in range(r):
            if k != i and m[k][i] != 0:
                f = m[k][i]
                m[k] = [x - f * y for x, y in zip(m[k], m[i])]
    return [m[i][r] for i in range(r)]


def fits_until(a: list[int], c) -> int | None:
    """Größtes n, bis zu dem die Rekursion mit den Koeffizienten c alle Glieder ab n = len(c) trifft; len(a) − 1, wenn sie alle trifft."""
    r = len(c)
    last_ok = None
    for n in range(r, len(a)):
        if a[n] != sum(c[j - 1] * a[n - j] for j in range(1, r + 1)):
            return last_ok if last_ok is not None else r - 1
        last_ok = n
    return len(a) - 1


def smallest_recurrence(a: list[int], rmax: int):
    """Kleinste Ordnung r ≤ rmax, deren aus 2r Gliedern bestimmte Rekursion alle weiteren Glieder von a trifft (Raten wie in Stück 1); (r, Koeffizienten) oder (None, None)."""
    for r in range(1, rmax + 1):
        if len(a) < 2 * r + 1:
            break
        c = solve_recurrence(a, r)
        if c is not None and fits_until(a, c) == len(a) - 1:
            return r, c
    return None, None


# ----------------------------------------------------------------------------- Polynome über Q

def trim(p) -> list:
    p = list(p)
    while p and p[-1] == 0:
        p.pop()
    return p


def poly_mul(a, b) -> list:
    if not a or not b:
        return []
    out = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def poly_divmod(a, b):
    """(Quotient, Rest) der Polynomdivision über den Brüchen; b ≠ 0."""
    a, b = trim(a), trim(b)
    if not b:
        raise ZeroDivisionError("Division durch das Nullpolynom")
    q = [Fraction(0)] * max(1, len(a) - len(b) + 1)
    r = list(a)
    while len(r) >= len(b) and r:
        c = r[-1] / b[-1]
        k = len(r) - len(b)
        q[k] = c
        for i, y in enumerate(b):
            r[i + k] -= c * y
        r = trim(r)
    return trim(q), r


def poly_gcd(a, b) -> list:
    """Größter gemeinsamer Teiler, monisch; gcd(0, b) = b normiert."""
    a, b = trim(a), trim(b)
    while b:
        _, r = poly_divmod(a, b)
        a, b = b, r
    return [x / a[-1] for x in a]


def poly_eval(p, z):
    """Wert des Polynoms an der Stelle z (Horner)."""
    v = 0
    for c in reversed(p):
        v = v * z + c
    return v


# ----------------------------------------------------------------------------- Übergangsmatrix, Nenner, Zähler

def transfer_matrix(auto: Automaton) -> list[list[int]]:
    """M[i][j] = Zahl der Zeichen, die den Zustand i in den Zustand j führen (verbotene Übergänge zählen nicht)."""
    idx = {z: i for i, z in enumerate(auto.states)}
    m = [[0] * auto.size for _ in range(auto.size)]
    for (z, _c), t in auto.trans.items():
        if t is not None:
            m[idx[z]][idx[t]] += 1
    return m


def _mat_mul(a, b):
    n = len(a)
    return [[sum(a[i][k] * b[k][j] for k in range(n)) for j in range(n)] for i in range(n)]


def q_polynomial(m: list[list[int]]) -> list[int]:
    """Q(z) = det(I − zM) nach Faddeev–LeVerrier mit ganzen Zahlen: Koeffizienten von z⁰ bis zˢ (s = Zahl der Zustände), Q(0) = 1."""
    n = len(m)
    coeffs = [1]
    mk = [[0] * n for _ in range(n)]
    for k in range(1, n + 1):
        mk = [[sum(m[i][t] * mk[t][j] for t in range(n)) + (coeffs[-1] if i == j else 0) for j in range(n)] for i in range(n)]
        am = _mat_mul(m, mk)
        tr = sum(am[i][i] for i in range(n))
        if tr % k:
            raise ArithmeticError("Spur nicht durch k teilbar: Faddeev–LeVerrier verlangt ganze Zahlen")
        coeffs.append(-tr // k)
    return coeffs


def det_at(m: list[list[int]], z: Fraction) -> Fraction:
    """det(I − z·M) durch Gauß-Elimination mit Brüchen: unabhängiger Rechenweg für `q_polynomial`."""
    n = len(m)
    a = [[Fraction(int(i == j)) - z * m[i][j] for j in range(n)] for i in range(n)]
    det = Fraction(1)
    for i in range(n):
        p = next((k for k in range(i, n) if a[k][i] != 0), None)
        if p is None:
            return Fraction(0)
        if p != i:
            a[i], a[p] = a[p], a[i]
            det = -det
        det *= a[i][i]
        for k in range(i + 1, n):
            f = a[k][i] / a[i][i]
            if f:
                a[k] = [x - f * y for x, y in zip(a[k], a[i])]
    return det


@dataclass(frozen=True, eq=False)
class Rational:
    """Die erzeugende Funktion A(z) = P/Q als Bruch, ungekürzt (p, q) und gekürzt (pr, qr, Nenner normiert auf Q(0) = 1)."""
    size: int
    matrix: list
    q: list
    p: list
    pr: list
    qr: list

    @property
    def deg_q(self) -> int:
        """Grad des gekürzten Nenners = Ordnung der kleinsten linearen Rekursion."""
        return len(self.qr) - 1

    @property
    def deg_p(self) -> int:
        """Grad des gekürzten Zählers (der Zähler ist nie null, da a(0) = 1)."""
        return len(self.pr) - 1

    @property
    def valid_from(self) -> int:
        """Die Rekursion der Ordnung deg_q gilt für alle n ab diesem Wert (der Anlauf endet davor)."""
        return max(self.deg_q, self.deg_p + 1)


def rational_form(auto: Automaton) -> Rational:
    """A(z) = e₀ᵀ (I − zM)⁻¹ 1 = P/Q mit Q = det(I − zM); P aus Q·A abgeschnitten, danach gekürzt."""
    s = auto.size
    m = transfer_matrix(auto)
    q = [Fraction(c) for c in q_polynomial(m)]
    a = [Fraction(x) for x in sequence(auto, 2 * s + 12)]
    prod = poly_mul(q, a)[: len(a)]
    p = trim(prod[:s])
    if any(c != 0 for c in prod[s:]):
        raise ArithmeticError("Q·A ist kein Polynom vom Grad < Zustandszahl")
    g = poly_gcd(p, trim(q))
    pr, rp = poly_divmod(p, g)
    qr, rq = poly_divmod(trim(q), g)
    if rp or rq:
        raise ArithmeticError("gcd teilt nicht")
    c = qr[0]
    return Rational(s, m, [int(x) for x in q], p, [x / c for x in pr], [x / c for x in qr])


def series_from_rational(pr, qr, n: int) -> list[Fraction]:
    """Die ersten n + 1 Glieder der Reihe von P/Q (Q(0) = 1): a(k) = P[k] − Σ_{j ≥ 1} Q[j]·a(k − j)."""
    out: list[Fraction] = []
    for k in range(n + 1):
        v = pr[k] if k < len(pr) else Fraction(0)
        for j in range(1, min(k, len(qr) - 1) + 1):
            v -= qr[j] * out[k - j]
        out.append(v)
    return out


def check_rational(auto: Automaton, rat: Rational, n: int = C.CHECK_N, points=C.CHECK_POINTS) -> list[str]:
    """Unabhängiger Prüfer (läuft auch in der App): Meldungen, leer wenn alles stimmt. Reihe aus P/Q gegen die Zustandsrekursion, Q gegen die Determinante, Q(0) = 1."""
    problems = []
    if series_from_rational(rat.pr, rat.qr, n) != [Fraction(x) for x in sequence(auto, n)]:
        problems.append("Die Reihe aus P/Q weicht von der Zählung ab")
    for num, den in points:
        z = Fraction(num, den)
        if poly_eval([Fraction(c) for c in rat.q], z) != det_at(rat.matrix, z):
            problems.append(f"Q({num}/{den}) weicht von der Determinante ab")
    if rat.q[0] != 1 or rat.qr[0] != 1:
        problems.append("Q(0) ist nicht 1")
    return problems


# ----------------------------------------------------------------------------- Eigenwerte und Wachstum

def dk_roots(qr, iterations: int = C.ROOT_ITERATIONS, tol: float = C.ROOT_STEP_TOL) -> list[complex]:
    """Eigenwerte λ: die Nullstellen des monischen Polynoms λ^d Q_r(1/λ) nach Durand–Kerner (d = Grad von Q_r). Die Pole von A(z) liegen bei z = 1/λ.

    Näherungen; Mehrfachnullstellen konvergieren langsamer. `residual` prüft das Ergebnis."""
    d = len(qr) - 1
    if d == 0:
        return []
    coeffs = [complex(c) for c in qr]

    def f(x):
        v = 0j
        for c in coeffs:
            v = v * x + c
        return v

    roots = [(0.4 + 0.9j) ** k for k in range(d)]
    for _ in range(iterations):
        delta = 0.0
        for i in range(d):
            den = 1 + 0j
            for j in range(d):
                if j != i:
                    den *= roots[i] - roots[j]
            if den == 0:
                den = 1e-12
            step = f(roots[i]) / den
            roots[i] -= step
            delta = max(delta, abs(step))
        if delta < tol:
            break
    return roots


def residual(qr, roots) -> float:
    """Größter relativer Rest |λ^d Q_r(1/λ)| / max(1, |λ|^d) an den berechneten Eigenwerten (0 ohne Eigenwerte)."""
    d = len(qr) - 1
    worst = 0.0
    for lam in roots:
        v = 0j
        for c in qr:
            v = v * lam + complex(c)
        worst = max(worst, abs(v) / max(1.0, abs(lam) ** d))
    return worst


@dataclass(frozen=True)
class Growth:
    kind: str                  # "endlich", "polynomiell" oder "exponentiell"
    roots: tuple               # Eigenwerte, nach Betrag absteigend
    lam1: float | None         # Betrag des größten Eigenwerts (None ohne Eigenwerte)
    ratio2: float | None       # |λ₂| / |λ₁| für den zweitgrößten Eigenwert (None, wenn es keinen gibt)
    dominant: int              # Zahl der Eigenwerte mit dem Betrag des größten


def classify(qr, tol: float = C.CLASS_TOL) -> Growth:
    """Wachstumsklasse aus den Eigenwerten: kein Eigenwert → endlich; größter Betrag < 1 → endlich; ≈ 1 → polynomiell; > 1 → exponentiell."""
    roots = tuple(sorted(dk_roots(qr), key=lambda z: -abs(z)))
    if not roots:
        return Growth("endlich", (), None, None, 0)
    rho = abs(roots[0])
    dominant = sum(1 for z in roots if abs(abs(z) - rho) < tol)
    ratio2 = abs(roots[1]) / rho if len(roots) > 1 and rho > 0 else None
    kind = "endlich" if rho < 1 - tol else ("polynomiell" if rho < 1 + tol else "exponentiell")
    return Growth(kind, roots, rho, ratio2, dominant)


def classify_sequence(auto: Automaton, n_low: int = C.CLASS_N_LOW, n_high: int = C.CLASS_N_HIGH, slope: float = C.CLASS_SLOPE) -> tuple[str, list]:
    """Wachstumsklasse aus der gezählten Folge: a(n_high) = 0 → endlich; Steigung von ln a(n) zwischen n_low und n_high über `slope` → exponentiell, sonst polynomiell.

    Gibt (Klasse, Folge bis n_high + 10) zurück."""
    a = sequence(auto, n_high + 10)
    if a[n_high] == 0:
        return "endlich", a
    if a[n_low] == 0:
        return "exponentiell", a                     # nicht bei endlichen Automaten; Schutz gegen log(0)
    g = (math.log(a[n_high]) - math.log(a[n_low])) / (n_high - n_low)
    return ("exponentiell" if g > slope else "polynomiell"), a


def ratio_spread(a: list[int], n0: int = C.OSC_N, count: int = 10) -> float | None:
    """Relative Schwankung (Spannweite / Mittel) der Quotienten a(n+1)/a(n) für n = n0 .. n0 + count − 1; None, wenn ein Quotient fehlt (a(n) = 0)."""
    rs = []
    for n in range(n0, n0 + count):
        if a[n] == 0:
            return None
        rs.append(growth_ratio(a[: n + 2], 15))
    mean = sum(rs) / len(rs)
    return (max(rs) - min(rs)) / mean


def ratio_error(a: list[int], lam1: float, n: int) -> float | None:
    """Relativer Fehler des Quotienten a(n)/a(n−1) gegen λ₁; None, wenn a(n−1) = 0."""
    r = growth_ratio(a[: n + 1], 15)
    return None if r is None else abs(r - lam1) / lam1


def first_n_within(a: list[int], lam1: float, eps: float, n_max: int):
    """Kleinstes n ≥ 2, ab dem der Quotient a(n)/a(n−1) auf eps genau gegen λ₁ liegt, bis n_max; None, wenn es keins gibt."""
    for n in range(2, min(n_max, len(a) - 1) + 1):
        e = ratio_error(a, lam1, n)
        if e is not None and e < eps:
            return n
    return None


def speed_estimate(ratio2: float | None, eps: float = C.SPEED_EPS) -> float | None:
    """Faustformel für das Einschwingtempo: ln(eps) / ln(|λ₂|/|λ₁|); nur für 0 < Verhältnis < 1."""
    if ratio2 is None or not 0 < ratio2 < 1:
        return None
    return math.log(eps) / math.log(ratio2)


def predict_digits(a: list[int], lam1: float, n: int, ref_n: int = C.DIGIT_REF_N) -> int | None:
    """Stellenzahl von a(n) ohne zu zählen: ⌊n·log₁₀ λ₁ + log₁₀ c⌋ + 1 mit c = a(ref_n)/λ₁^ref_n; None, wenn a(ref_n) = 0."""
    if a[ref_n] == 0:
        return None
    log_c = log10_int(a[ref_n]) - ref_n * math.log10(lam1)
    return math.floor(n * math.log10(lam1) + log_c) + 1
