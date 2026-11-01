"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

ALPHABETS = {
    "F, S, N (Früh, Spät, Nacht)": "FSN",
    "A, B": "AB",
    "A, B, C": "ABC",
}
DEFAULT_ALPHABET = "F, S, N (Früh, Spät, Nacht)"
DEFAULT_PATTERNS = "NF, NNN"                 # keine Früh direkt nach Nacht, höchstens zwei Nächte in Folge
N_MIN, N_MAX, DEFAULT_N = 1, 60, 12          # Länge der Folgen für die Zahlenreihe und die Probe
PATTERN_MAX_COUNT, PATTERN_MAX_LEN = 6, 6    # höchstens 6 Verbote mit je höchstens 6 Zeichen: der Automat hat dann höchstens 31 Zustände
PATTERN_TEXT_MAX = 60                        # längere Eingaben aus der Adresszeile werden abgeschnitten
SERIES_SHOW = 14                             # so viele Glieder zeigt die Probe „Reihe aus P/Q gegen Zählung“
CHECK_N = 40                                 # bis hierher prüft die App die Reihe aus P/Q gegen die Zustandsrekursion
CHECK_POINTS = ((1, 3), (-2, 5), (3, 7))     # (Zähler, Nenner) der Stellen, an denen die App Q gegen die Determinante prüft

ROOT_ITERATIONS = 2000                       # Durand–Kerner: höchstens so viele Runden
ROOT_STEP_TOL = 1e-15                        # Abbruch, wenn kein Wert sich mehr um mehr als das ändert
RESIDUAL_WARN = 1e-6                         # darüber warnt die App vor einer ungenauen Nullstelle
CLASS_TOL = 1e-5                             # Betrag einer Nullstelle gilt als 1 beziehungsweise als gleich groß, wenn er höchstens so weit abweicht
SPEED_EPS = 1e-6                             # Genauigkeit, bei der das Einschwingtempo gemessen wird
SPEED_N_MAX = 400                            # so weit sucht die App nach dem ersten n, bei dem der Quotient auf SPEED_EPS genau ist
RATIO_ERROR_N = 40                           # so viele n zeigt das Diagramm des Quotientenfehlers
DIGIT_REF_N = 200                            # aus a(n) bei diesem n wird die Konstante c bestimmt
DIGIT_SIZES = (1000, 10000)                  # Längen, für die die Stellenzahl vorhergesagt und gezählt wird
CLASS_SETS = 300                             # Zahl der Zufallsregelsätze in Experiment 5
CLASS_SEED_BASE = 10000                      # feste Seeds: nie ein einzelner Satz als Befund
CLASS_N_LOW, CLASS_N_HIGH = 200, 400         # Längen, aus deren Verhältnis die Wachstumsklasse der Folge bestimmt wird
CLASS_SLOPE = 0.03                           # Steigung von ln a(n) (n = 200 bis 400), ab der die Folge als exponentiell gilt
OSC_N = 300                                  # ab hier (zehn Glieder) wird geprüft, ob der Quotient schwingt
OSC_TOL = 1e-4                               # relative Schwankung, ab der der Quotient als schwingend gilt
GUESS_RMAX = 12                              # größte Ordnung, die das Raten (Stück 1) versucht
PROBE_TERMS = 300                            # Glieder der Teilsumme in der Spielwiese

COLOR_ROOT = "#2F6B65"
COLOR_DOMINANT = "#c0504d"
COLOR_LINE = "#4c78a8"
COLOR_GRID = "rgba(150,150,150,0.55)"

PRESETS = {
    "Standardfall: Schichtfolgen": {"alphabet": DEFAULT_ALPHABET, "patterns": "NF, NNN", "n": 12},
    "Fibonacci: A, B ohne AA": {"alphabet": "A, B", "patterns": "AA", "n": 12},
    "Rekursion mit Anlauf": {"alphabet": "A, B, C", "patterns": "AB, BC, CA, AAA", "n": 12},
    "Viele Verbote, mehr Zustände": {"alphabet": DEFAULT_ALPHABET, "patterns": "NF, NNN, FFFF, SFS, SSSS, NSN", "n": 12},
    "Polynomielles Wachstum": {"alphabet": "A, B", "patterns": "AB", "n": 12},
    "Endliche Folge": {"alphabet": "A, B", "patterns": "AA, BB, AB, BA", "n": 6},
}
PRESET_HELP = {
    "Standardfall: Schichtfolgen": "Früh, Spät, Nacht ohne „Nacht, dann Früh“ und ohne drei Nächte in Folge. Der Nenner hat Grad 3, der Zähler Grad 2.",
    "Fibonacci: A, B ohne AA": "Folgen aus A und B ohne zwei A hintereinander: Nenner 1 − z − z², Zähler 1 + z, größter Eigenwert der goldene Schnitt.",
    "Rekursion mit Anlauf": "Drei Symbole, vier Verbote: Zähler- und Nennergrad sind gleich, die Rekursion gilt erst ab n = 5. Erklärt, warum Raten (Stück 1) die Ordnung 5 findet.",
    "Viele Verbote, mehr Zustände": "Sechs Verbote bis Länge 4: elf Zustände, ein Nenner höheren Grades und viele Nullstellen im Bild.",
    "Polynomielles Wachstum": "A, B ohne AB: nur Wörter der Form B…BA…A, also n + 1 Stück. Der Nenner ist (1 − z)², der größte Eigenwert ist 1 (doppelt).",
    "Endliche Folge": "A, B ohne AA, BB, AB, BA: nach zwei Zeichen gibt es nichts mehr. Der Nenner ist 1, die erzeugende Funktion ein Polynom.",
}
