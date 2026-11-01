"""Gemeinsame Fixtures: die Mini-Instanzen, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ref_scenario import Rules  # noqa: E402


@pytest.fixture
def fib():
    """Wörter aus A und B ohne AA. Zustände „“ und „A“; M = [[1, 1], [1, 0]] (B bleibt oder führt zurück, A führt nach „A“, von „A“ aus nur B zurück).
    Handrechnung: I − zM = [[1 − z, −z], [−z, 1]], Q = (1 − z) − z² = 1 − z − z²; (1 + z)/(1 − z − z²) = 1 + 2z + 3z² + 5z³ + …"""
    return Rules("AB", ("AA",))


@pytest.fixture
def schicht():
    """Schichtfolgen aus F, S, N ohne NF und NNN. Zustände „“, „N“, „NN“; M = [[2, 1, 0], [1, 0, 1], [1, 0, 0]].
    Handrechnung: det [[1−2z, −z, 0], [−z, 1, −z], [−z, 0, 1]] = (1−2z) + z(−z − z²) = 1 − 2z − z² − z³; P = Q·(1 + 3z + 8z² + 20z³ + …) abgeschnitten = 1 + z + z²."""
    return Rules("FSN", ("NF", "NNN"))
