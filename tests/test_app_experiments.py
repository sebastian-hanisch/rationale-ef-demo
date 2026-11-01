"""AppTest-Durchläufe der Experimente, des Permalinks und der Spielwiese (die allgemeinen Rauchtests stehen in test_app.py)."""

import os
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import ref_constants as C

APP = str(Path(__file__).resolve().parent.parent / "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))


def _app(query: dict | None = None) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    for key, value in (query or {}).items():
        at.query_params[key] = value
    at.run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def test_standard_case_shows_the_hand_values_and_no_error():
    at = _app()
    assert not at.error
    metrics = {m.label: m.value for m in at.metric}
    assert metrics["Zustände"] == "3" and metrics["Grad des Nenners (gekürzt)"] == "3" and metrics["Grad des Zählers (gekürzt)"] == "2"
    assert metrics["Größter Eigenwert λ₁"] == "2,5468"
    assert any("Q(z) = 1 − 2z − z² − z³" in m.value and "a(n) = 2·a(n−1) + a(n−2) + a(n−3)" in m.value for m in at.markdown)


def test_experiments_one_to_four_show_their_verdicts_without_a_click():
    at = _app()
    texts = " | ".join(e.value for e in list(at.success) + list(at.info) + list(at.warning))
    assert "Die Reihe aus dem Bruch stimmt" in texts and "Das Raten findet als kleinste Ordnung 3" in texts
    assert "Der größte Eigenwert ist 2,546818" in texts and "vorhergesagt 407, gezählt 407" in texts


def test_class_experiment_runs_on_click():
    at = _app()
    at.button(key="class_run").click().run(timeout=TIMEOUT)
    assert not at.exception and not at.error
    assert any(f"Von {C.CLASS_SETS} Zufallsregelsätzen" in s.value for s in at.success)


def test_probe_slider_inside_and_outside_the_radius():
    at = _app()
    at.slider(key="probe_t").set_value(0.5).run(timeout=TIMEOUT)
    assert any("Innerhalb des Konvergenzradius" in s.value for s in at.success)
    at.slider(key="probe_t").set_value(1.5).run(timeout=TIMEOUT)
    assert not at.exception and any("konvergiert nicht" in w.value for w in at.warning)


def test_permalink_loads_and_clamps_the_values():
    at = _app({"alphabet": "A, B", "patterns": "AA", "n": "9999"})
    assert at.sidebar.selectbox(key="alphabet_select").value == "A, B"
    assert at.sidebar.text_input(key="patterns_input").value == "AA"
    assert at.sidebar.slider(key="n_slider").value == C.N_MAX


def test_permalink_with_garbage_is_ignored_or_cut():
    at = _app({"alphabet": "kein Alphabet", "patterns": "X" * 500, "n": "abc"})
    assert at.sidebar.selectbox(key="alphabet_select").value == C.DEFAULT_ALPHABET
    assert len(at.sidebar.text_input(key="patterns_input").value) <= C.PATTERN_TEXT_MAX
    assert at.sidebar.slider(key="n_slider").value == C.DEFAULT_N


def test_invalid_patterns_are_reported_and_do_not_crash():
    at = _app()
    at.sidebar.text_input(key="patterns_input").set_value("QQ, NF, AAAAAAAA").run(timeout=TIMEOUT)
    assert not at.exception
    assert len(at.warning) >= 2 and any("außerhalb des Alphabets" in w.value for w in at.warning)


@pytest.mark.parametrize("patterns, expected", [("F, S, N", "Es gibt keinen Eigenwert"), ("", "Der größte Eigenwert ist λ₁ = 3,0000")])
def test_extreme_rule_sets_render_their_summary(patterns, expected):
    at = _app()
    at.sidebar.text_input(key="patterns_input").set_value(patterns).run(timeout=TIMEOUT)
    assert not at.exception and not at.error
    assert any(expected in e.value for e in list(at.success) + list(at.info))


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_every_preset_renders_without_error_or_checker_message(name):
    at = _app()
    at.sidebar.button(key=f"preset_{name}").click().run(timeout=TIMEOUT)
    assert not at.exception and not at.error, name


def test_pdf_can_be_made_for_the_extreme_settings():
    for query in ({"n": "1"}, {"n": "60"}, {"patterns": "F, S, N"}, {"patterns": ""}):
        at = _app(query)
        at.button(key="pdf_make").click().run(timeout=TIMEOUT)
        assert not at.exception, query


@pytest.mark.parametrize("alphabet", list(C.ALPHABETS))
def test_every_alphabet_renders(alphabet):
    at = _app({"alphabet": alphabet, "patterns": ""})
    assert not at.exception and not at.error
