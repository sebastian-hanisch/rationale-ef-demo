"""Szenario: Regelsätze für Folgen über einem kleinen Alphabet (verbotene Teilfolgen), dieselben wie in Stück 1 der Reihe, dazu Zufallssätze für Experiment 5."""

import random
import re
from dataclasses import dataclass

import ref_constants as C


@dataclass(frozen=True)
class Rules:
    """Alphabet und verbotene Teilfolgen: eine Folge ist gültig, wenn keines der Muster als zusammenhängende Teilfolge vorkommt."""
    alphabet: str
    patterns: tuple[str, ...]

    @property
    def k(self) -> int:
        return len(self.alphabet)


def alphabet_of(label: str) -> str:
    """Alphabet zur Auswahl im Regler; unbekannte Bezeichnungen fallen auf das Standardalphabet zurück."""
    return C.ALPHABETS.get(label, C.ALPHABETS[C.DEFAULT_ALPHABET])


def parse_patterns(text: str, alphabet: str) -> tuple[tuple[str, ...], list[str]]:
    """Verbotsmuster aus einem Eingabetext (getrennt durch Komma, Semikolon oder Leerraum), Groß-/Kleinschreibung egal.

    Gibt (Muster in Eingabereihenfolge ohne Doppelte, Meldungen) zurück. Ungültige Muster werden verworfen und gemeldet, nie still ersetzt."""
    patterns: list[str] = []
    problems: list[str] = []
    for raw in re.split(r"[,;\s]+", text[: C.PATTERN_TEXT_MAX * 4].upper()):
        if not raw:
            continue
        bad = sorted(set(raw) - set(alphabet))
        if bad:
            problems.append(f"„{raw}“ enthält Zeichen außerhalb des Alphabets ({' '.join(bad)}) und zählt nicht.")
            continue
        if len(raw) > C.PATTERN_MAX_LEN:
            problems.append(f"„{raw}“ ist länger als {C.PATTERN_MAX_LEN} Zeichen und zählt nicht.")
            continue
        if raw not in patterns:
            patterns.append(raw)
    if len(patterns) > C.PATTERN_MAX_COUNT:
        problems.append(f"Mehr als {C.PATTERN_MAX_COUNT} Muster: nur die ersten {C.PATTERN_MAX_COUNT} zählen.")
        patterns = patterns[: C.PATTERN_MAX_COUNT]
    return tuple(patterns), problems


def make_rules(alphabet_label: str, patterns_text: str) -> tuple[Rules, list[str]]:
    alphabet = alphabet_of(alphabet_label)
    patterns, problems = parse_patterns(patterns_text, alphabet)
    return Rules(alphabet, patterns), problems


def random_rules(seed: int) -> Rules:
    """Zufälliger Regelsatz für Experiment 5, deterministisch aus dem Seed: Alphabet A, B oder A, B, C; 1 bis 4 Verbote der Länge 1 bis 4."""
    rng = random.Random(seed)
    alphabet = rng.choice(("AB", "ABC", "ABC"))
    return Rules(alphabet, tuple("".join(rng.choice(alphabet) for _ in range(rng.randint(1, 4))) for _ in range(rng.randint(1, 4))))
