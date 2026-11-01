"""Jede Zahl aus der README und aus den Texten der App, nachgerechnet (DEMO-PLAYBOOK §4). Die Zufallssätze sind dieselben wie in Phase 0 (`random_rules`, feste Seeds)."""

import math
from fractions import Fraction

import ref_algorithm as A
import ref_constants as C
import ref_evaluation as ev
from ref_scenario import Rules, random_rules

FIB = Rules("AB", ("AA",))
SCHICHT = Rules("FSN", ("NF", "NNN"))
ANLAUF = Rules("ABC", ("AB", "BC", "CA", "AAA"))


def _core(rules):
    auto = A.build_automaton(rules)
    return auto, A.rational_form(auto)


def test_readme_hand_fractions():
    assert _core(FIB)[1].qr == [1, -1, -1] and _core(FIB)[1].pr == [1, 1]
    assert _core(SCHICHT)[1].qr == [1, -2, -1, -1] and _core(SCHICHT)[1].pr == [1, 1, 1]
    anlauf = _core(ANLAUF)[1]
    assert anlauf.qr == [1, -2, 1, -1, -1] and anlauf.pr == [1, 1, 1, 1, 1] and anlauf.valid_from == 5


def test_readme_largest_eigenvalues_and_ratios():
    expected = {"Fibonacci": (FIB, 1.618033988750, 0.3820), "Standard": (SCHICHT, 2.546818276884, 0.2460), "Anlauf": (ANLAUF, 1.897179401065, 0.5500)}
    for name, (rules, lam, ratio2) in expected.items():
        g = A.classify(_core(rules)[1].qr)
        assert abs(g.lam1 - lam) < 1e-9 and abs(g.ratio2 - ratio2) < 5e-5, name


def test_readme_ratio_errors_of_the_standard_case():
    auto, rat = _core(SCHICHT)
    g = A.classify(rat.qr)
    a = A.sequence(auto, 40)
    errs = {n: A.ratio_error(a, g.lam1, n) for n in (5, 10, 20)}
    assert 8.0e-4 < errs[5] < 9.5e-4 and 1.5e-7 < errs[10] < 1.9e-7 and errs[20] < 1e-11


def test_readme_speed_of_settling_and_the_rule_of_thumb():
    expected = {"Fibonacci": (FIB, 14, 14.4), "Standard": (SCHICHT, 10, 9.9), "Anlauf": (ANLAUF, 16, 23.1)}
    for name, (rules, first, estimate) in expected.items():
        res = ev.growth_experiment(*_core(rules))
        assert res["first_n"] == first, name
        assert abs(res["estimate"] - estimate) < 0.1, name
    anlauf = ev.growth_experiment(*_core(ANLAUF))
    assert anlauf["estimate"] / anlauf["first_n"] > 1.4                          # README: um ein Drittel und mehr zu hoch


def test_readme_guessed_order_against_degrees_over_300_random_sets():
    agree_denominator = agree_max = anlauf = finite = 0
    for seed in range(300):
        auto, rat = _core(random_rules(seed))
        rmax = rat.valid_from + 1
        guess, _ = A.smallest_recurrence(A.sequence(auto, 2 * rmax + 40), rmax)
        agree_denominator += guess == rat.deg_q
        agree_max += guess == rat.valid_from
        anlauf += rat.deg_p >= rat.deg_q
        finite += rat.deg_q == 0
        assert A.series_from_rational(rat.pr, rat.qr, 50) == [Fraction(x) for x in A.sequence(auto, 50)]
    assert (agree_denominator, agree_max, anlauf, finite) == (256, 300, 44, 18)


def test_readme_growth_classes_over_300_random_sets():
    res = ev.class_experiment()
    assert res["count"] == 300 == C.CLASS_SETS
    assert res["from_roots"] == res["from_seq"] == {"exponentiell": 201, "polynomiell": 86, "endlich": 13}
    assert res["match"] == 300 and res["multi_dominant"] == 5 and res["oscillating"] == 0


def test_readme_growth_classes_over_1000_random_sets_from_phase_zero():
    res = ev.class_experiment(count=1000)
    assert res["from_roots"] == res["from_seq"] == {"exponentiell": 673, "polynomiell": 283, "endlich": 44}
    assert res["match"] == 1000 and res["multi_dominant"] == 51 and res["oscillating"] == 1


def test_readme_digit_prediction_over_43_exponential_sets():
    tested = hits = 0
    for seed in range(60):
        auto, rat = _core(random_rules(20_000 + seed))
        g = A.classify(rat.qr)
        if g.kind != "exponentiell" or A.sequence(auto, 200)[200] == 0:
            continue
        tested += 1
        res = ev.digits_experiment(auto, rat)
        hits += all(r["predicted"] == r["exact"] for r in res["rows"])
    assert (tested, hits) == (43, 43)


def test_readme_standard_digits_and_constant():
    auto, rat = _core(SCHICHT)
    g = A.classify(rat.qr)
    a = A.sequence(auto, C.DIGIT_REF_N)
    log_c = A.log10_int(a[C.DIGIT_REF_N]) - C.DIGIT_REF_N * math.log10(g.lam1)
    assert abs(log_c - 0.0838468990) < 1e-8
    assert [(r["n"], r["predicted"], r["exact"]) for r in ev.digits_experiment(auto, rat)["rows"]] == [(1000, 407, 407), (10000, 4061, 4061)]


def test_readme_root_finder_quality_over_300_random_sets():
    worst, deviations = 0.0, []
    for seed in range(300):
        auto, rat = _core(random_rules(30_000 + seed))
        g = A.classify(rat.qr)
        worst = max(worst, A.residual(rat.qr, g.roots))
        if g.kind == "exponentiell":
            a = A.sequence(auto, 800)
            if a[799] and A.ratio_spread(a, n0=790, count=10) < 1e-6:
                deviations.append(abs(A.growth_ratio(a, 15) - g.lam1) / g.lam1)
    deviations.sort()
    assert worst < 1e-12 and len(deviations) >= 150 and deviations[len(deviations) // 2] < 1e-12 and deviations[-1] < 1e-9


def test_readme_cancellation_and_state_counts():
    assert _core(Rules("ABC", ("CA", "BBB", "AC")))[1].deg_q == 3 and A.build_automaton(Rules("ABC", ("CA", "BBB", "AC"))).size == 5
    sizes = {name: ev.analyse(ev.Settings(**p)).auto.size for name, p in C.PRESETS.items()}
    assert sizes == {"Standardfall: Schichtfolgen": 3, "Fibonacci: A, B ohne AA": 2, "Rekursion mit Anlauf": 5, "Viele Verbote, mehr Zustände": 11,
                     "Polynomielles Wachstum": 2, "Endliche Folge": 3}


def test_app_text_limits_come_from_the_constants():
    assert (C.PATTERN_MAX_COUNT, C.PATTERN_MAX_LEN, C.GUESS_RMAX, C.SPEED_EPS, C.SPEED_N_MAX) == (6, 6, 12, 1e-6, 400)
    assert C.CHECK_N == 40 and len(C.CHECK_POINTS) == 3 and C.CLASS_N_LOW == 200 and C.CLASS_N_HIGH == 400 and C.CLASS_SLOPE == 0.03 and C.RESIDUAL_WARN == 1e-6
