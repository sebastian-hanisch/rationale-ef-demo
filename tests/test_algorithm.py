"""Kern gegen Handrechnung (DEMO-PLAYBOOK §1b): Mini-Instanzen aus conftest.py, jeder Erwartungswert als Rechnung."""

import math
from fractions import Fraction

import pytest

import ref_algorithm as A
from ref_scenario import Rules


def _rat(rules):
    auto = A.build_automaton(rules)
    return auto, A.rational_form(auto)


def test_transfer_matrices_by_hand(fib, schicht):
    assert A.transfer_matrix(A.build_automaton(fib)) == [[1, 1], [1, 0]]
    assert A.transfer_matrix(A.build_automaton(schicht)) == [[2, 1, 0], [1, 0, 1], [1, 0, 0]]


def test_fibonacci_fraction_by_hand(fib):
    auto, rat = _rat(fib)
    assert rat.q == [1, -1, -1] and rat.pr == [1, 1] and rat.qr == [1, -1, -1]
    assert rat.deg_q == 2 and rat.deg_p == 1 and rat.valid_from == 2
    assert A.series_from_rational(rat.pr, rat.qr, 6) == [1, 2, 3, 5, 8, 13, 21]


def test_schicht_fraction_by_hand(schicht):
    auto, rat = _rat(schicht)
    assert rat.q == [1, -2, -1, -1] and rat.pr == [1, 1, 1] and rat.qr == [1, -2, -1, -1]
    assert rat.deg_q == 3 and rat.deg_p == 2 and rat.valid_from == 3
    prod = A.poly_mul([Fraction(c) for c in rat.q], [Fraction(x) for x in A.sequence(auto, 8)])[:4]
    assert prod == [1, 1, 1, 0]                                      # (1 + 3z + 8z² + 20z³)(1 − 2z − z² − z³) bis z³


def test_anlauf_preset_has_numerator_degree_equal_to_denominator_degree():
    auto, rat = _rat(Rules("ABC", ("AB", "BC", "CA", "AAA")))
    assert rat.qr == [1, -2, 1, -1, -1] and rat.pr == [1, 1, 1, 1, 1]
    assert rat.deg_q == rat.deg_p == 4 and rat.valid_from == 5 and rat.size == 5       # fünf Zustände, aber Nennergrad 4


def test_polynomial_growth_and_finite_cases_by_hand():
    _, rat = _rat(Rules("AB", ("AB",)))                              # a(n) = n + 1, Q = (1 − z)², P = 1
    assert rat.qr == [1, -2, 1] and rat.pr == [1]
    assert A.series_from_rational(rat.pr, rat.qr, 5) == [1, 2, 3, 4, 5, 6]
    _, rat = _rat(Rules("AB", ("AA", "BB", "AB", "BA")))             # 1, 2, 0, 0, …
    assert rat.qr == [1] and rat.pr == [1, 2] and rat.valid_from == 2


def test_cancellation_reduces_the_fraction():
    """Hat das Verbotssystem überflüssige Zustände, kürzen sich Faktoren: Der gekürzte Nenner hat dann niedrigeren Grad als die Zustandszahl."""
    auto, rat = _rat(Rules("ABC", ("AB", "BC", "CA", "AAA")))
    assert rat.deg_q < auto.size
    rules = Rules("AB", ("AAB", "ABA"))
    auto, rat = _rat(rules)
    assert A.series_from_rational(rat.pr, rat.qr, 10) == [A.sequence(auto, 10)[n] for n in range(11)]


def test_det_at_by_hand(fib):
    m = A.transfer_matrix(A.build_automaton(fib))
    assert A.det_at(m, Fraction(1, 2)) == Fraction(1, 4)             # 1 − 1/2 − 1/4
    assert A.det_at(m, Fraction(0)) == 1 and A.det_at(m, Fraction(1)) == -1       # 1 − 1 − 1


def test_poly_helpers_by_hand():
    f = Fraction
    q, r = A.poly_divmod([f(-1), f(0), f(1)], [f(-1), f(1)])        # (z² − 1) : (z − 1) = z + 1
    assert q == [1, 1] and r == []
    assert A.poly_gcd([f(-1), f(0), f(1)], [f(2), f(-3), f(1)]) == [-1, 1]      # gcd(z² − 1, z² − 3z + 2) = z − 1 (monisch)
    assert A.poly_eval([f(1), f(2), f(3)], f(2)) == 17               # 1 + 4 + 12
    assert A.trim([1, 0, 0]) == [1] and A.trim([0]) == []


def test_eigenvalues_of_fibonacci_are_the_golden_ratio_and_its_conjugate(fib):
    _, rat = _rat(fib)
    g = A.classify(rat.qr)
    phi = (1 + math.sqrt(5)) / 2
    assert g.kind == "exponentiell" and abs(g.lam1 - phi) < 1e-12
    assert abs(g.ratio2 - 1 / phi ** 2) < 1e-12                       # |λ₂| / λ₁ = (1/φ) / φ
    assert sorted(z.real for z in g.roots) == pytest.approx([1 - phi, phi])
    assert A.residual(rat.qr, g.roots) < 1e-12


def test_classes_of_the_hand_cases():
    assert A.classify([Fraction(1)]).kind == "endlich" and A.classify([Fraction(1)]).lam1 is None
    g = A.classify([Fraction(1), Fraction(-2), Fraction(1)])         # (1 − z)²: doppelter Eigenwert 1
    assert g.kind == "polynomiell" and g.dominant == 2 and abs(g.lam1 - 1) < 1e-6


def test_speed_estimate_and_prediction_by_hand():
    assert abs(A.speed_estimate(0.1, 1e-6) - 6.0) < 1e-12           # ln(1e-6) / ln(0,1)
    assert A.speed_estimate(None) is None and A.speed_estimate(1.0) is None and A.speed_estimate(0.0) is None
    ref = [1, 2, 4, 8, 16]                                            # a(n) = 2ⁿ, c = 1
    assert A.predict_digits(ref, 2.0, 4, ref_n=4) == 2               # 16 hat 2 Stellen
    assert A.predict_digits(ref, 2.0, 10, ref_n=4) == 4              # 1024
    assert A.predict_digits([1, 0, 0], 2.0, 2, ref_n=2) is None


def test_digit_helpers_and_growth_ratio():
    assert A.digit_count(0) == 1 and A.digit_count(999) == 3 and A.digit_count(1000) == 4 and A.digit_count(3 ** 10000) == 4772
    assert A.leading_digits(12345, 3) == (5, 123) and A.leading_digits(10 ** 5000, 3) == (5001, 100)
    assert abs(A.log10_int(1000) - 3.0) < 1e-12 and abs(A.log10_int(3 ** 10000) - 10000 * math.log10(3)) < 1e-6
    assert A.growth_ratio([1, 2, 3, 5, 8, 13]) == 1.625 and A.growth_ratio([0, 0]) is None
    with pytest.raises(ValueError):
        A.digit_count(-1)
    with pytest.raises(ValueError):
        A.log10_int(0)


def test_check_rational_accepts_the_truth_and_flags_wrong_numbers(schicht):
    auto, rat = _rat(schicht)
    assert A.check_rational(auto, rat) == []
    wrong_q = A.Rational(rat.size, rat.matrix, [1, -2, -1, -2], rat.p, rat.pr, rat.qr)
    assert any("Determinante" in p for p in A.check_rational(auto, wrong_q))
    wrong_p = A.Rational(rat.size, rat.matrix, rat.q, rat.p, [1, 1, 2], rat.qr)
    assert any("Reihe" in p for p in A.check_rational(auto, wrong_p))


def test_ratio_helpers_on_the_fibonacci_sequence(fib):
    auto = A.build_automaton(fib)
    a = A.sequence(auto, 60)
    phi = (1 + math.sqrt(5)) / 2
    assert A.ratio_error(a, phi, 40) < 1e-12 and A.ratio_error([1, 0, 0], 2.0, 2) is None
    n = A.first_n_within(a, phi, 1e-6, 60)
    assert n is not None and A.ratio_error(a, phi, n) < 1e-6 and A.ratio_error(a, phi, n - 1) >= 1e-6
    assert A.first_n_within(a, phi, 1e-30, 30) is None
    assert A.ratio_spread(a, n0=40, count=10) < 1e-9
    assert A.ratio_spread([1, 0, 0] * 20, n0=0, count=3) is None
