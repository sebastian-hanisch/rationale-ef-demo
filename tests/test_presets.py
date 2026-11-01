"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, jedes Preset zeigt etwas anderes."""

import ref_constants as C
import ref_evaluation as ev
import ref_presets as P
from ref_scenario import make_rules


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_regler_bounds():
    for name, preset in C.PRESETS.items():
        assert preset["alphabet"] in C.ALPHABETS, name
        assert C.N_MIN <= preset["n"] <= C.N_MAX, name
        assert len(preset["patterns"]) <= C.PATTERN_TEXT_MAX, name


def test_every_preset_parses_without_a_message_and_passes_the_checker():
    for name, preset in C.PRESETS.items():
        assert make_rules(preset["alphabet"], preset["patterns"])[1] == [], name
        assert ev.analyse(ev.Settings(**preset)).problems == [], name


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS["Standardfall: Schichtfolgen"]) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_presets_show_the_three_growth_classes_and_the_run_in():
    """Kein totes Preset: jedes zeigt etwas anderes (Klasse, Anlauf, Zustandszahl)."""
    seen = {}
    for name, preset in C.PRESETS.items():
        a = ev.analyse(ev.Settings(**preset))
        seen[name] = (a.growth.kind, a.rat.deg_q, a.rat.deg_p, a.auto.size)
    assert len(set(seen.values())) == len(C.PRESETS)
    assert seen["Polynomielles Wachstum"][0] == "polynomiell" and seen["Endliche Folge"][0] == "endlich"
    anlauf = seen["Rekursion mit Anlauf"]
    assert anlauf[2] >= anlauf[1] and anlauf[3] > anlauf[1]                      # Zählergrad ≥ Nennergrad; weniger Nennergrad als Zustände
    assert seen["Viele Verbote, mehr Zustände"][3] == 11
