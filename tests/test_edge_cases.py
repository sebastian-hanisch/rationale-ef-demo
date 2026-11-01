"""Randfälle, an denen Kernroutinen erfahrungsgemäß brechen (DEMO-PLAYBOOK §12)."""

from fractions import Fraction

import pytest

import ref_algorithm as A
import ref_constants as C
import ref_evaluation as ev
from ref_scenario import Rules, make_rules, parse_patterns, random_rules


def _rat(rules):
    auto = A.build_automaton(rules)
    return auto, A.rational_form(auto)


def test_no_patterns_gives_the_geometric_series():
    auto, rat = _rat(Rules("ABC", ()))
    assert rat.q == [1, -3] and rat.pr == [1] and A.classify(rat.qr).lam1 == pytest.approx(3.0)


def test_everything_forbidden_leaves_only_the_empty_word():
    auto, rat = _rat(Rules("AB", ("A", "B")))
    assert rat.qr == [1] and rat.pr == [1] and rat.valid_from == 1 and A.classify(rat.qr).kind == "endlich"


def test_pattern_as_long_as_the_word_or_longer():
    auto, rat = _rat(Rules("AB", ("AAAAAA",)))
    assert A.series_from_rational(rat.pr, rat.qr, 8) == [Fraction(x) for x in A.sequence(auto, 8)]
    assert A.sequence(auto, 8)[5:8] == [32, 63, 125]                   # n = 7: 128 − (2 + 2 − 1) Wörter mit sechs A in Folge (Stellen 1–6 oder 2–7, AAAAAAA doppelt)


def test_single_state_automaton_has_degree_at_most_one():
    auto, rat = _rat(Rules("AB", ("A",)))                              # nur B erlaubt: a(n) = 1
    assert auto.size == 1 and rat.qr == [1, -1] and rat.pr == [1] and A.classify(rat.qr).kind == "polynomiell"


def test_negative_arguments_raise():
    auto, _ = _rat(Rules("AB", ("AA",)))
    for call in (lambda: A.sequence(auto, -1), lambda: A.count_matrix(auto, -1), lambda: A.log10_int(-5)):
        with pytest.raises(ValueError):
            call()
    with pytest.raises(ZeroDivisionError):
        A.poly_divmod([Fraction(1)], [])
    with pytest.raises(ValueError):
        A.build_automaton(Rules("AB", ("AX",)))


def test_polynomial_helpers_on_empty_inputs():
    assert A.poly_mul([], [Fraction(1)]) == [] and A.trim([]) == [] and A.poly_eval([], 3) == 0
    assert A.poly_gcd([Fraction(2), Fraction(2)], []) == [1, 1]        # gcd(2 + 2z, 0) = 1 + z


def test_series_from_a_polynomial_stops_after_the_degree():
    assert A.series_from_rational([Fraction(1), Fraction(2)], [Fraction(1)], 5) == [1, 2, 0, 0, 0, 0]


def test_dk_roots_without_degree_and_for_a_double_root():
    assert A.dk_roots([Fraction(1)]) == []
    roots = A.dk_roots([Fraction(1), Fraction(-2), Fraction(1)])       # (λ − 1)²
    assert len(roots) == 2 and all(abs(r - 1) < 1e-6 for r in roots)
    assert A.residual([Fraction(1)], []) == 0.0


def test_classify_sequence_guards_against_zero():
    auto, _ = _rat(Rules("AB", ("A", "B")))
    kind, a = A.classify_sequence(auto)
    assert kind == "endlich" and len(a) == 411
    auto, _ = _rat(Rules("AB", ("AB",)))
    assert A.classify_sequence(auto)[0] == "polynomiell"


def test_parse_patterns_and_make_rules():
    assert parse_patterns("NF, NNN", "FSN") == (("NF", "NNN"), [])
    assert parse_patterns("nf;nnn  NF", "FSN") == (("NF", "NNN"), [])
    patterns, problems = parse_patterns("NF, XY, AAAAAAA", "FSN")
    assert patterns == ("NF",) and len(problems) == 2
    many, problems = parse_patterns(", ".join(["F", "S", "N", "FF", "SS", "NN", "FS"]), "FSN")
    assert len(many) == C.PATTERN_MAX_COUNT and len(problems) == 1
    longest = "F" * C.PATTERN_MAX_LEN
    assert parse_patterns(longest, "FSN")[0] == (longest,) and parse_patterns(longest + "F", "FSN")[0] == ()
    rules, problems = make_rules("gibt es nicht", "NF")
    assert rules.alphabet == "FSN" and problems == []


def test_random_rules_are_deterministic_and_inside_the_documented_ranges():
    assert random_rules(7) == random_rules(7)
    for seed in range(200):
        r = random_rules(seed)
        assert r.alphabet in ("AB", "ABC") and 1 <= len(r.patterns) <= 4 and all(1 <= len(p) <= 4 and set(p) <= set(r.alphabet) for p in r.patterns)


def test_text_helpers():
    assert ev.poly_text([1, -2, -1, -1]) == "1 − 2z − z² − z³"
    assert ev.poly_text([Fraction(1), Fraction(1, 2), Fraction(-3, 2)]) == "1 + (1/2)z − (3/2)z²"
    assert ev.poly_text([1]) == "1" and ev.poly_text([]) == "0" and ev.poly_text([0, 1]) == "z" and ev.poly_text([0, -1]) == "−z"
    assert ev.recurrence_text([1, -2, -1, -1]) == "a(n) = 2·a(n−1) + a(n−2) + a(n−3)"
    assert ev.recurrence_text([1, 1, -1]) == "a(n) = −a(n−1) + a(n−2)" and ev.recurrence_text([1]) == "a(n) = 0"
    assert ev.recurrence_text([1, 0, -1]) == "a(n) = a(n−2)"
    assert ev.eigenvalue_text(complex(2.5468182769, 0)) == "2,5468"
    assert ev.eigenvalue_text(complex(-0.5, 0.25)) == "-0,5000 + 0,2500 i" and ev.eigenvalue_text(complex(1.0, -0.5)) == "1,0000 − 0,5000 i"
