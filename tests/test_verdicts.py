"""Verdikte und Formatierung an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier.

Ein Verdikt ist eine reine Funktion (Art, Text) und bekommt Zeilen, nicht Seeds. Damit prüft der Test die Grenzen und jede genannte Zahl direkt."""

import ref_algorithm as A
import ref_constants as C
import ref_evaluation as ev
from ref_scenario import Rules

STD = ("F, S, N (Früh, Spät, Nacht)", "NF, NNN")


def _analysis(alphabet: str, patterns: str, n: int = 12):
    return ev.analyse(ev.Settings(alphabet, patterns, n))


def test_big_text_groups_digits_and_switches_to_powers_of_ten_at_12_digits():
    assert ev.big_text(0) == "0" and ev.big_text(1234567) == "1.234.567" and ev.big_text(999_999_999_999) == "999.999.999.999"
    assert ev.big_text(10 ** 12) == "1,00·10¹² (13 Stellen)" and ev.big_text(10 ** 5000) == "1,00·10⁵⁰⁰⁰ (5001 Stellen)"


def test_de_formats_with_decimal_comma():
    assert ev.de(2.54681827, 4) == "2,5468" and ev.de(0.5, 1) == "0,5"


def test_summary_verdict_for_the_three_kinds():
    kind, text = ev.verdict_summary(_analysis(*STD))
    assert kind == "success"
    assert text == ("Der Nenner ist 1 − 2z − z² − z³. Der größte Eigenwert ist λ₁ = 2,5468: Mit jedem Zeichen mehr wächst die Zahl der gültigen Folgen auf das 2,5468fache "
                    "(exponentiell). Die Rekursion der Ordnung 3 gilt ab n = 3.")
    kind, text = ev.verdict_summary(_analysis("A, B, C", "AB, BC, CA, AAA"))
    assert kind == "success" and "Die Rekursion der Ordnung 4 gilt ab n = 5; davor gibt es einen Anlauf, weil der Zähler Grad 4 hat." in text
    kind, text = ev.verdict_summary(_analysis("A, B", "AB"))
    assert kind == "info" and text.startswith("Der Nenner ist 1 − 2z + z². Der größte Eigenwert hat den Betrag 1:") and "Ordnung 2 gilt ab n = 2." in text
    kind, text = ev.verdict_summary(_analysis("A, B", "AA, BB, AB, BA"))
    assert kind == "info" and text == ("Der Nenner ist 1: Es gibt keinen Eigenwert, die erzeugende Funktion ist ein Polynom vom Grad 1. Ab n = 2 gibt es keine gültige Folge mehr.")


def test_series_rows_pair_counted_and_fraction_terms():
    rows = ev.series_rows(_analysis(*STD))
    assert [r["gezählt"] for r in rows[:6]] == [1, 3, 8, 20, 51, 130] and all(r["gleich"] for r in rows) and len(rows) == C.SERIES_SHOW
    assert ev.series_rows(_analysis(*STD), count=1)[0]["n"] == 0 and len(ev.series_rows(_analysis(*STD), count=1)) == 1


def test_check_points_table_has_equal_values():
    rows = ev.check_points_table(_analysis(*STD))
    assert [r["z"] for r in rows] == ["1/3", "-2/5", "3/7"] and all(r["gleich"] for r in rows)
    assert rows[0]["Q(z)"] == "5/27" == rows[0]["det(I − zM)"]                 # 27/27 − 18/27 − 3/27 − 1/27 an z = 1/3


def test_verdict_read_cases():
    base = {"skipped": False, "deg_q": 3, "deg_p": 2, "rmax": 12, "reading": 3, "guess": 3, "agree": True}
    kind, text = ev.verdict_read(base)
    assert kind == "success" and text == ("Aus dem Bruch gelesen: Nennergrad 3, Zählergrad 2, also gilt die Rekursion ab n = 3. Das Raten findet als kleinste Ordnung 3: gleich der gelesenen.")
    kind, text = ev.verdict_read(dict(base, deg_q=4, deg_p=4, reading=5, guess=5))
    assert kind == "success" and text.endswith(" Das Raten findet Ordnung 5, größer als der Nennergrad 4: Der Zähler macht den Anlauf.")
    kind, text = ev.verdict_read(dict(base, guess=4, agree=False))
    assert kind == "warning" and "Das Raten findet Ordnung 4, die gelesene Ordnung ist 3" in text
    kind, text = ev.verdict_read(dict(base, guess=None, agree=None))
    assert kind == "warning" and "bis Ordnung 12 keine Rekursion" in text
    kind, text = ev.verdict_read(dict(base, skipped=True, reading=20, guess=None, agree=None))
    assert kind == "info" and "Ordnung 20" in text and "bis Ordnung 12 versucht" in text


def test_read_experiment_on_the_presets():
    for rules, expected in ((Rules("AB", ("AA",)), 2), (Rules("FSN", ("NF", "NNN")), 3), (Rules("ABC", ("AB", "BC", "CA", "AAA")), 5)):
        auto = A.build_automaton(rules)
        res = ev.read_experiment(auto, A.rational_form(auto))
        assert res["reading"] == res["guess"] == expected and res["agree"] and not res["skipped"]
    big = A.build_automaton(Rules("FSN", ("NF", "NNN", "FFFF", "SFS", "SSSS", "NSN")))
    assert ev.read_experiment(big, A.rational_form(big), rmax=3)["skipped"] is True


def test_verdict_growth_cases():
    g = A.Growth("exponentiell", (2.5468 + 0j,), 2.5468182769, 0.246, 1)
    res = {"growth": g, "first_n": 10, "estimate": 9.9, "spread": 1e-12}
    kind, text = ev.verdict_growth(res)
    assert kind == "success" and text == ("Der größte Eigenwert ist 2,546818; der zweitgrößte hat den Betrag 0,6265, das Verhältnis ist 0,2460. "
                                          "Der Quotient a(n)/a(n−1) ist ab n = 10 auf 1e-06 genau am Eigenwert. Die Faustformel ln(1e-06) / ln(Verhältnis) sagt 9,9 voraus: "
                                          "nur eine grobe Abschätzung, die Konstante vor dem Abklingen fehlt.")
    kind, text = ev.verdict_growth(dict(res, first_n=None, spread=0.5))
    assert kind == "warning" and text.endswith("nicht auf 1e-06 genau am Eigenwert: Er schwingt, weil mehrere Eigenwerte denselben Betrag haben.")
    assert ev.verdict_growth(dict(res, first_n=None, spread=None))[1].endswith("am Eigenwert.")
    assert ev.verdict_growth({"growth": A.Growth("endlich", (), None, None, 0)})[0] == "info"
    assert ev.verdict_growth({"growth": A.Growth("polynomiell", (1 + 0j, 1 + 0j), 1.0, 1.0, 2)})[0] == "info"


def test_growth_experiment_on_fibonacci():
    auto = A.build_automaton(Rules("AB", ("AA",)))
    res = ev.growth_experiment(auto, A.rational_form(auto))
    assert res["growth"].kind == "exponentiell" and res["first_n"] == 14 and abs(res["estimate"] - 14.4) < 0.05 and len(res["errors"]) == C.RATIO_ERROR_N - 1
    assert res["errors"][0][0] == 2 and res["residual"] < 1e-12


def test_verdict_digits_cases():
    rows = [{"n": 1000, "predicted": 407, "exact": 407}, {"n": 10000, "predicted": 4061, "exact": 4061}]
    kind, text = ev.verdict_digits({"kind": "exponentiell", "lam1": 2.5468182769, "rows": rows})
    assert kind == "success" and text == ("Aus λ₁ = 2,546818 und der Konstanten c (aus a(200)): n = 1000: vorhergesagt 407, gezählt 407; n = 10000: vorhergesagt 4061, gezählt 4061. Beide stimmen.")
    rows[1]["predicted"] = 4062
    kind, text = ev.verdict_digits({"kind": "exponentiell", "lam1": 2.5468182769, "rows": rows})
    assert kind == "warning" and text.endswith("1 von 2 weichen ab.")
    assert ev.verdict_digits({"kind": "polynomiell", "lam1": 1.0, "rows": []})[0] == "info"


def test_digits_experiment_standard_and_unrestricted():
    auto = A.build_automaton(Rules("FSN", ("NF", "NNN")))
    res = ev.digits_experiment(auto, A.rational_form(auto))
    assert [(r["n"], r["predicted"], r["exact"]) for r in res["rows"]] == [(1000, 407, 407), (10000, 4061, 4061)]
    auto = A.build_automaton(Rules("ABC", ()))                                        # 3^10000 hat 4772 Stellen: über der Umwandlungsgrenze von Python
    res = ev.digits_experiment(auto, A.rational_form(auto))
    assert [(r["n"], r["predicted"], r["exact"]) for r in res["rows"]] == [(1000, 478, 478), (10000, 4772, 4772)]
    auto = A.build_automaton(Rules("AB", ("AB",)))
    assert ev.digits_experiment(auto, A.rational_form(auto))["rows"] == []


def test_verdict_classes_cases():
    res = {"count": 300, "from_roots": {"exponentiell": 201, "polynomiell": 86, "endlich": 13}, "from_seq": {"exponentiell": 201, "polynomiell": 86, "endlich": 13},
           "match": 300, "mismatches": [], "multi_dominant": 5, "oscillating": 0}
    kind, text = ev.verdict_classes(res)
    assert kind == "success" and text == ("Von 300 Zufallsregelsätzen: 201 exponentiell, 86 polynomiell, 13 endlich. Aus den Eigenwerten und aus der gezählten Folge ergibt sich bei 300 dieselbe Klasse. "
                                         "5 Sätze haben mehrere Eigenwerte mit dem größten Betrag, bei 0 schwingt der Quotient a(n+1)/a(n) bei n = 300.")
    kind, text = ev.verdict_classes(dict(res, match=298, mismatches=[10001, 10007]))
    assert kind == "warning" and text.endswith("Abweichende Seeds: 10001, 10007.")


def test_class_experiment_small_run_is_consistent():
    res = ev.class_experiment(count=20, seed_base=10000)
    assert sum(res["from_roots"].values()) == 20 == sum(res["from_seq"].values()) and res["match"] == 20 - len(res["mismatches"])


def test_probe_and_its_verdict():
    a = _analysis("A, B", "AA")                                                      # λ₁ = φ, Radius 1/φ
    inside = ev.probe(a, 0.5)
    assert abs(inside["z0"] - 0.5 / ((1 + 5 ** 0.5) / 2)) < 1e-9 and abs(inside["partial"] - inside["exact"]) < 1e-9
    assert ev.verdict_probe(inside)[0] == "success"
    outside = ev.probe(a, 1.5)
    kind, text = ev.verdict_probe(outside)
    assert kind == "warning" and "Konvergenzradius 0,6180" in text
    at_pole = ev.probe(a, 1.0)
    assert ev.verdict_probe(at_pole)[0] == "warning"
    finite = ev.probe(_analysis("A, B", "AA, BB, AB, BA"), 0.5)                      # P(z) = 1 + 2z an z = 0,5 gleich 2
    assert abs(finite["exact"] - 2.0) < 1e-12 and abs(finite["partial"] - 2.0) < 1e-12 and finite["radius"] is None
    assert ev.verdict_probe(finite)[0] == "success"
    just_started = ev.probe(a, 0.95, terms=5)                                         # zu wenige Glieder: noch nicht eingeschwungen
    assert ev.verdict_probe(just_started)[0] == "info"
