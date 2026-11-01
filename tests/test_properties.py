"""Eigenschaften (ORACLE-PLAYBOOK §5): Aussagen, die für jeden Regelsatz gelten, auf festen Zufallsständen."""

import os
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest

import ref_algorithm as A
from ref_scenario import Rules, random_rules

ROOT = Path(__file__).resolve().parent.parent


def _rat(rules: Rules):
    auto = A.build_automaton(rules)
    return auto, A.rational_form(auto)


@pytest.mark.parametrize("seed", range(40))
def test_fraction_is_reduced_normalised_and_bounded(seed):
    auto, rat = _rat(random_rules(seed))
    assert rat.q[0] == 1 and rat.qr[0] == 1                           # Q(0) = 1
    assert rat.deg_q <= auto.size and rat.deg_p <= auto.size - 1
    g = A.poly_gcd(rat.pr, rat.qr)
    assert g == [1], seed                                              # teilerfremd (gcd = 1, monisch)
    assert rat.pr and rat.pr[0] == 1                                   # a(0) = 1


@pytest.mark.parametrize("seed", range(40))
def test_renaming_symbols_and_reordering_patterns_do_not_change_the_fraction(seed):
    rules = random_rules(seed)
    base = _rat(rules)[1]
    swap = str.maketrans("AB", "BA")
    renamed = Rules(rules.alphabet.translate(swap), tuple(p.translate(swap) for p in rules.patterns))
    reordered = Rules(rules.alphabet, tuple(reversed(rules.patterns)) + rules.patterns)
    for other in (renamed, reordered):
        rat = _rat(other)[1]
        assert (rat.qr, rat.pr) == (base.qr, base.pr), seed


@pytest.mark.parametrize("seed", range(40))
def test_an_additional_pattern_never_increases_the_largest_eigenvalue(seed):
    rules = random_rules(seed)
    more = Rules(rules.alphabet, rules.patterns + (rules.alphabet[0] * 3,))
    g1 = A.classify(_rat(rules)[1].qr)
    g2 = A.classify(_rat(more)[1].qr)
    l1 = g1.lam1 or 0.0
    l2 = g2.lam1 or 0.0
    assert l2 <= l1 + 1e-7, (seed, l1, l2)


@pytest.mark.parametrize("seed", range(40))
def test_finite_exactly_when_the_denominator_is_one(seed):
    auto, rat = _rat(random_rules(seed))
    a = A.sequence(auto, 60)
    finite = a[60] == 0
    assert (rat.deg_q == 0) == finite, seed
    assert (A.classify(rat.qr).kind == "endlich") == finite, seed


def test_a_real_cancellation_case():
    """Q = 1 − 2z − z² + 2z⁴ und P = 1 + z − z³ − z⁴ haben den gemeinsamen Faktor 1 + z: gekürzt Grad 3 und 3."""
    auto, rat = _rat(Rules("ABC", ("CA", "BBB", "AC")))
    assert rat.q == [1, -2, -1, 0, 2, 0] and len(A.trim(rat.p)) - 1 == 4
    assert rat.qr == [1, -1, -2, -2] and rat.pr == [1, 2, 2, 1]
    assert A.series_from_rational(rat.p, [Fraction(c) for c in rat.q], 20) == A.series_from_rational(rat.pr, rat.qr, 20)


def test_result_does_not_depend_on_the_hash_seed():
    """Mengen von Zeichenketten ordnen sich je Prozess anders (Hash-Randomisierung): dasselbe Szenario in zwei Prozessen muss denselben Bruch geben."""
    code = (
        "import ref_algorithm as A; from ref_scenario import Rules; "
        "r = Rules('ABC', ('AB', 'BC', 'CA', 'AAA', 'BBBC')); a = A.build_automaton(r); rat = A.rational_form(a); "
        "print(a.states, rat.matrix, rat.q, rat.pr, rat.qr)"
    )
    outs = []
    for hash_seed in ("1", "2"):
        env = dict(os.environ, PYTHONHASHSEED=hash_seed)
        outs.append(subprocess.run([sys.executable, "-c", code], cwd=ROOT, env=env, capture_output=True, text=True, check=True).stdout)
    assert outs[0] == outs[1] and outs[0].strip()
