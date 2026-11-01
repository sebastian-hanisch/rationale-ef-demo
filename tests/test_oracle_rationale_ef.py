"""Orakel-Tests: Nenner, Zähler und Eigenwerte gegen unabhängige Rechenwege (DEMO-PLAYBOOK §12, ORACLE-PLAYBOOK §5).

Unabhängig heißt: die Determinante von I − zM durch Gauß-Elimination mit Brüchen (statt Faddeev–LeVerrier), die Zustandsrekursion und die Matrixpotenz für die Folge
(statt der Reihe aus P/Q), das Raten der Rekursion aus Stück 1 (statt Ablesen), der Quotient a(n)/a(n−1) bei großem n (statt der Nullstellensuche) und bekannte Zahlen
aus der Literatur (goldener Schnitt, Tribonacci-Konstante). Feste Zufallsstände, zusammen unter 10 Sekunden."""

import math
from fractions import Fraction

import pytest

import ref_algorithm as A
from ref_scenario import Rules, random_rules


def _core(seed):
    rules = random_rules(seed)
    auto = A.build_automaton(rules)
    return rules, auto, A.rational_form(auto)


@pytest.mark.parametrize("seed", range(40))
def test_q_equals_the_determinant_at_rational_points(seed):
    _, auto, rat = _core(seed)
    q = [Fraction(c) for c in rat.q]
    for z in (Fraction(1, 3), Fraction(-2, 5), Fraction(3, 7), Fraction(5, 2), Fraction(-1)):
        assert A.poly_eval(q, z) == A.det_at(rat.matrix, z), (seed, z)


@pytest.mark.parametrize("seed", range(40))
def test_series_from_the_fraction_equals_recursion_and_matrix_power(seed):
    _, auto, rat = _core(seed)
    frac = A.series_from_rational(rat.pr, rat.qr, 40)
    assert frac == [Fraction(x) for x in A.sequence(auto, 40)], seed
    for n in (0, 1, 7, 25, 40):
        assert frac[n] == A.count_matrix(auto, n), (seed, n)


@pytest.mark.parametrize("seed", range(40))
def test_smallest_guessed_order_equals_max_of_denominator_degree_and_numerator_degree_plus_one(seed):
    """Orakel: das Raten aus Stück 1 (Gleichungssystem aus den ersten Gliedern) gegen das Ablesen aus dem Bruch."""
    _, auto, rat = _core(seed)
    rmax = rat.valid_from + 1
    a = A.sequence(auto, 2 * rmax + 40)
    guess, _ = A.smallest_recurrence(a, rmax)
    assert guess == rat.valid_from, (seed, rat.deg_q, rat.deg_p)


def test_largest_eigenvalue_equals_the_limit_of_the_ratio_and_is_a_real_eigenvalue():
    """Orakel: der Quotient a(800)/a(799) gegen den Betrag des größten Eigenwerts, nur für exponentielle, nicht schwingende Sätze (mindestens 20 von 60 müssen es sein)."""
    checked = 0
    for seed in range(60):
        _, auto, rat = _core(seed)
        g = A.classify(rat.qr)
        if g.kind != "exponentiell":
            continue
        a = A.sequence(auto, 810)
        if A.ratio_spread(a, n0=790, count=10) > 1e-9:
            continue
        checked += 1
        assert abs(A.growth_ratio(a[:801], 15) - g.lam1) / g.lam1 < 1e-9, seed
        assert any(abs(z.imag) < 1e-9 and abs(z.real - g.lam1) < 1e-9 for z in g.roots), seed       # Perron–Frobenius: der Spektralradius ist selbst ein Eigenwert
        assert A.residual(rat.qr, g.roots) < 1e-9, seed
    assert checked >= 20


def test_golden_ratio_and_tribonacci_constant_from_the_literature():
    rat = A.rational_form(A.build_automaton(Rules("AB", ("AA",))))
    assert abs(A.classify(rat.qr).lam1 - (1 + math.sqrt(5)) / 2) < 1e-12
    rat = A.rational_form(A.build_automaton(Rules("AB", ("AAA",))))
    assert rat.qr == [1, -1, -1, -1] and rat.pr == [1, 1, 1]
    assert abs(A.classify(rat.qr).lam1 - 1.8392867552141612) < 1e-12                       # Tribonacci-Konstante


def test_words_without_ab_have_the_double_eigenvalue_one():
    """a(n) = n + 1 hat die erzeugende Funktion 1/(1 − z)²: ein doppelter Eigenwert 1, also polynomiell."""
    rat = A.rational_form(A.build_automaton(Rules("AB", ("AB",))))
    assert rat.qr == [1, -2, 1] and A.classify(rat.qr).kind == "polynomiell"
