# Rationale erzeugende Funktion – der Nenner verrät es – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-rationale-ef-demo.streamlit.app/)** -->

Stück 2 von 16 der Reihe **„Abzählen und erzeugende Funktionen“** in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“ (die Linie wird erst vollständig veröffentlicht). Vorgänger ist `aufzaehlen-rekursion-demo` (Stück 1): Dort zählt die Rekursion über einen Zustand Folgen mit verbotenen Teilfolgen. Diese Demo fasst dieselben Zahlen a(0), a(1), … zur **erzeugenden Funktion** zusammen und zeigt, dass sie ein **Bruch aus zwei Polynomen** ist, dessen Nenner man ohne Zählen ausrechnet. Dieselben Regler und Presets wie in Stück 1 (Alphabet, verbotene Teilfolgen, Länge), dazu ein Bild der Eigenwerte in der komplexen Ebene. Kante zu Stück 1: Raten zeigt kein Wachstum und keinen Grund für den Anlauf. Schichtfolgen sind nur der Rahmen: Dienstplanung ist ein Optimierungsproblem, hier wird nur gezählt.

## Warum dieses Problem

Was verrät der Bruch P(z) / Q(z) über die Zählfolge? Der Nenner Q(z) = det(I − zM) lässt sich ohne Zählen berechnen; den Zähler P gewinnt die App aus den ersten gezählten Gliedern. Vier Dinge: die **Rekursion** (die Koeffizienten von Q), den **Anlauf** (der Grad des Zählers P), das **Wachstum** (der größte Eigenwert, der Kehrwert der kleinsten Nullstelle von Q) und die **Wachstumsklasse** (endlich, polynomiell, exponentiell). Daraus folgt sogar die Stellenzahl weit entfernter Glieder.

## Befunde und Korrekturen gegenüber dem Plan

- **Hook bestätigt, Faustformel nur grob.** Der Plan sagte „größter Eigenwert ablesbar ohne zu zählen“: bestätigt (Experiment 3). Die Faustformel für das Einschwingtempo ln(10⁻⁶)/ln(|λ₂|/λ₁) trifft bei zwei von drei Beispielen (14,4 und 9,9 gegen gemessen 14 und 10), beim Anlauf-Preset sagt sie 23,1 voraus und gemessen sind 16: Die Konstante vor dem Abklingen fehlt. Im Text steht sie deshalb als Faustregel.
- **Neuer Befund gegenüber der Gliederung:** Der Zählergrad erklärt, warum das Raten aus Stück 1 eine größere Ordnung findet als erwartet: kleinste geratene Ordnung = max(Nennergrad, Zählergrad + 1) in 300 von 300 Zufallssätzen (Test mit den Seeds 0 bis 299).
- **Zufallssätze in der App:** 300 Sätze (feste Seeds ab 10 000) statt der 1000 aus Phase 0, damit die Rechnung in der App einige Sekunden dauert; die 1000 aus Phase 0 sind im Test nachgerechnet (siehe Befunde).
- **Experimente 1 bis 4 laufen ohne Knopf**, Experiment 5 nur auf Klick (Sekunden).
- **Presets:** zu den vier aus Stück 1 kamen „Polynomielles Wachstum“ (A, B ohne AB) und „Endliche Folge“ (A, B ohne AA, BB, AB, BA); das Preset „Zu lang zum Aufzählen“ aus Stück 1 fehlt hier, da diese Demo keine Aufzählung misst.
- **Browser-Lehre:** Ein Diagramm mit gleichem Maßstab (`scaleanchor`) in einem schmalen oder verdeckten Vorschau-Tab (Breite 16 px) bekam absurde Achsenbereiche (±400 und ±1500) und Konsolenfehler `<text> attribute y: Expected length, "-Infinity"`. Im frisch geöffneten Vordergrund-Tab (Breite 554 px) stimmen die Bereiche und die Konsole ist leer; deshalb prüft man Diagramme nur in einem frischen Tab. Der Bereich wird über zwei unsichtbare Eckmarker erzwungen, nicht über einen festen `range`.

## Modell

Wie in Stück 1: Alphabet, bis zu sechs Verbote von je höchstens sechs Zeichen, `a(n)` = Zahl der Wörter der Länge n ohne Verbot. Der Automat hat die Zustände (längstes Ende des Wortes, das ein echter Anfang eines Verbots ist); `M[i][j]` zählt die Zeichen von Zustand i nach Zustand j. Dann gilt A(z) = Σ a(n) zⁿ = e₀ᵀ (I − zM)⁻¹ **1** = P(z)/Q(z) mit Q(z) = det(I − zM), berechnet nach Faddeev–LeVerrier mit ganzen Zahlen (`q_polynomial`); P ist Q·A, abgeschnitten, danach mit Brüchen gekürzt (`rational_form`). Die Eigenwerte (Nullstellen von λ^d · Q(1/λ)) bestimmt Durand–Kerner in `complex` (`dk_roots`); sie dienen nur der Anzeige und den Vorhersagen. Die Formeln stehen im 📐-Expander der App.

## Methodik

- **Nenner und Zähler exakt:** ganze Zahlen und `fractions`, keine Gleitkommarechnung für Q und P.
- **Unabhängiger Prüfer in der App** (`check_rational`): die Reihe aus P/Q gegen die Zustandsrekursion bis n = 40, Q gegen die Determinante von I − zM an drei Stellen (Gauß-Elimination mit Brüchen), Q(0) = 1; bei Abweichung zeigt die App einen Fehler statt einer Zahl, bei einem Rest der Nullstellensuche über 10⁻⁶ eine Warnung.
- **Ablesen gegen Raten:** das Raten aus Stück 1 (`smallest_recurrence`: Gleichungssystem aus den ersten 2r Gliedern) gegen die aus dem Bruch gelesene Ordnung.
- **Klassen:** aus den Eigenwerten (`classify`: kein Eigenwert oder Betrag unter 1 endlich, Betrag 1 polynomiell, darüber exponentiell) gegen die aus der gezählten Folge (`classify_sequence`: Steigung von ln a(n) zwischen n = 200 und 400 über 0,03).
- **Stellenzahl:** ⌊n·log₁₀ λ₁ + log₁₀ c⌋ + 1 mit c aus a(200), ohne Umwandlung großer ganzer Zahlen in Text (`digit_count`, `leading_digits`; Python begrenzt die Umwandlung auf 4300 Stellen, siehe Stück 1).

## Befunde (gemessen, keine Behauptungen)

Jede Zahl steht in `tests/test_claims.py`, `tests/test_verdicts.py`, `tests/test_algorithm.py` oder `tests/test_oracle_rationale_ef.py`. Die Zufallssätze sind `random_rules(seed)` mit festen Seeds. Es gibt in dieser Demo keine Zeitmessung.

| Frage | Befund |
|---|---|
| Handinstanzen | Fibonacci (A, B ohne AA): Q = 1 − z − z², P = 1 + z. Standardfall (NF, NNN): Q = 1 − 2z − z² − z³, P = 1 + z + z² (Q von Hand: det [[1−2z, −z, 0], [−z, 1, −z], [−z, 0, 1]]). Anlauf-Preset (AB, BC, CA, AAA): Q = 1 − 2z + z² − z³ − z⁴, P = 1 + z + z² + z³ + z⁴, fünf Zustände, aber Nennergrad 4 |
| Reihe aus P/Q gegen Zustandsrekursion | 0 Abweichungen auf 300 Zufallssätzen bis n = 50; Q gegen die Determinante an je fünf rationalen Stellen auf 40 Sätzen gleich |
| Kleinste geratene Ordnung gegen Nennergrad | gleich in 256 von 300 Sätzen; die übrigen 44 haben Zählergrad ≥ Nennergrad (darunter 18 endliche Folgen). **Kleinste geratene Ordnung = max(Nennergrad, Zählergrad + 1) in 300 von 300** |
| Größter Eigenwert | Fibonacci 1,618033988750; Standard 2,546818276884; Anlauf 1,897179401065; Fibonacci ist der goldene Schnitt, die Wörter ohne AAA haben die Tribonacci-Konstante 1,8392867552141612 |
| Quotient a(n)/a(n−1) gegen den Eigenwert | Standardfall: relativer Fehler etwa 8,6·10⁻⁴ (n = 5), 1,7·10⁻⁷ (n = 10), 7,9·10⁻¹³ (n = 20); der Betrag des größten Eigenwerts stimmt auf 300 Zufallssätzen auf 10⁻⁹ mit a(800)/a(799) überein (Median unter 10⁻¹², nur nicht schwingende exponentielle Sätze) |
| Einschwingtempo | Verhältnis der Beträge λ₂ zu λ₁ = 0,3820 (Fibonacci), 0,2460 (Standard), 0,5500 (Anlauf); Fehler unter 10⁻⁶ erstmals bei n = 14, 10, 16; Faustformel 14,4, 9,9, 23,1 |
| Wachstumsklassen, 300 Sätze (Seeds ab 10 000) | exponentiell 201, polynomiell 86, endlich 13; aus den Eigenwerten und aus der Folge **300 von 300** gleich; 5 Sätze mit mehreren Eigenwerten vom größten Betrag; der Quotient schwingt in 0 |
| Wachstumsklassen, 1000 Sätze (Phase 0) | 673 exponentiell, 283 polynomiell, 44 endlich, 1000 von 1000 gleich; 51 Sätze mit mehreren größten Eigenwerten, der Quotient schwingt in 1 |
| Stellenzahl vorhersagen | richtig in **43 von 43** exponentiellen Sätzen bei n = 1000 und n = 10 000. Standard: log₁₀ c = 0,0838468990, vorhergesagt und gezählt 407 und 4061 Stellen; ohne Verbote 478 und 4772. Die Konstante c kommt aus dem gezählten a(200). In 1342 weiteren exponentiellen Zufallssätzen (Seeds ab 70 000, unabhängige Nachprüfung) stimmte die Vorhersage in 1339; die 3 Ausfälle: 2 Fehler der Nullstellensuche, 1 Satz mit doppeltem größtem Eigenwert (2093 statt 2094 Stellen) |
| Nullstellensuche | größter relativer Rest unter 10⁻¹² über 300 Sätze (Phase 0: 1,2·10⁻¹⁵); bei dreifacher Nullstelle λ = 1 (Q = (1 − z)³) scheitert Durand–Kerner, siehe Grenzen |
| Kürzen | Beispiel (A, B, C; CA, BBB, AC): Q = 1 − 2z − z² + 2z⁴ und P = 1 + z − z³ − z⁴ haben den Faktor 1 + z gemeinsam; gekürzt Grad 3 und 3 (fünf Zustände) |
| Presets | Zustandszahlen 3, 2, 5, 11, 2, 3; Klassen: Polynomielles Wachstum ist polynomiell (Q = (1 − z)²), Endliche Folge endlich (Q = 1, P = 1 + 2z) |

## Ehrliche Grenzen

- **Die Matrixmethode setzt einen endlichen Automaten voraus.** Verschachtelte Strukturen (Klammern, Bäume) ergeben keinen Bruch aus Polynomen (Catalan-Zahlen): Stück 3. Ein Regelwerk ohne endlichen Automaten kann eine rationale Zählfolge haben (etwa aⁿbⁿ mit 1/(1 − z²)); die Demo behandelt es nicht.
- **Wachstum nur aus dem größten Eigenwert.** Mehrere Eigenwerte gleichen Betrags können den Quotienten schwingen lassen (in 1 von 1000 Zufallssätzen beobachtet, kein exponentieller Fall darunter), mehrfache bringen einen polynomiellen Faktor; die Demo liest nur die Klasse, nicht den Grad des Polynoms (Stück 9).
- **Nullstellen sind Näherungen** (Durand–Kerner). Mehrfachnullstellen konvergieren langsamer oder gar nicht: Bei der dreifachen Nullstelle λ = 1 (Q = (1 − z)³, etwa Verbote ABAA und ABB über A, B) scheitert das Verfahren. In 6000 Zufallssätzen traten 9 solche Fälle auf; beim Vergleich der Klassen blieben deshalb in 3000 weiteren Sätzen 2997 von 3000 gleich. Die App warnt „Eigenwerte ungenau“, zeigt aber trotzdem eine falsche Klasse „exponentiell“, einen falschen größten Eigenwert (etwa 1,41 statt 1) und eine falsche Stellenzahl (124 statt 6 bei n = 1000). Das ist ein bekannter Fehler der Demo, nicht behoben. Die ursprüngliche Prüfung an 1300 Zufallssätzen hat diese Fälle nicht erfasst, gezielt konstruierte Fälle fehlten.
- **Die Klassen hängen an der Schwelle 0,03** für die Steigung von ln a(n) (n = 200 bis 400). Für kleine Automaten trennt sie sauber (1000 von 1000), das ist eine Beobachtung, kein Beweis.
- **„Kleinste geratene Ordnung = max(Nennergrad, Zählergrad + 1)“** ist ein Messbefund an Zufallssätzen; die Ableitung aus Q·A = P liegt nahe, wird hier nicht bewiesen.
- **Konvergenzradius der Spielwiese:** die Teilsumme nutzt 300 Glieder; nahe am Radius ist sie noch nicht eingeschwungen, die App sagt es.
- Alles simuliert, keine echten Dienstpläne.

## Verifikation

- **Kern:** Q und P der drei Handinstanzen, goldener Schnitt und Tribonacci-Konstante, Polynomhilfen an Handwerten, Determinante an rationalen Stellen als unabhängiger Rechenweg, Reihe aus P/Q gegen Zustandsrekursion und Matrixpotenz, das Raten aus Stück 1 gegen das Ablesen, Quotient bei n = 800 gegen den Eigenwert (Perron–Frobenius: der größte Eigenwert ist selbst ein Eigenwert).
- **Eigenschaften:** gekürzt teilerfremd, Q(0) = 1, Gradschranken, Umbenennen der Zeichen und Reihenfolge der Verbote ändern den Bruch nicht, ein Verbot mehr vergrößert den größten Eigenwert nie, endlich genau bei Nenner 1, gleiches Ergebnis in zwei Prozessen mit verschiedenem `PYTHONHASHSEED`.
- **Randfälle:** keine Verbote (geometrische Reihe), alles verboten, Verbot länger als die Folge, Automat mit einem Zustand, negative Argumente, Nullpolynom und leere Eingaben der Polynomhilfen, Doppelwurzel, Parser der Verbote an den Grenzen.
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler an Minimum und Maximum), Experimente ohne Klick, Experiment 5 auf Klick, Spielwiese innerhalb und außerhalb des Radius, jedes Preset, Permalink mit Müll und Grenzwerten, ungültige Muster, alles verboten, ohne Verbote, PDF an den Rändern; Footer-Test.
- **Layout:** Schnellstart oben in der Seitenleiste, fester Kopf, aktives Preset hervorgehoben; jede Änderung eines Reglers hebt die Markierung auf (`tests/test_layout.py`).
- **Browser:** frischer Vordergrund-Tab ohne Konsoleneinträge (Standard, Preset mit elf Zuständen, Experiment 5 per Klick); Achsenbereiche des Eigenwertbildes geprüft.
- **Nicht gemacht:** Mutationstests (seit 2026-10-28 nicht mehr verlangt), Docker-Lauf der Linux-CI (Docker fehlt auf diesem Rechner; die CI nach dem Push entscheidet), Handy-Breite (Layout wie Stück 1, nicht erneut geprüft).

381 Tests (`pytest tests`).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: Ergebnis, Bruch, Kernfrage, fünf Experimente, Spielwiese, Grenzen, Formeln |
| `ref_algorithm.py` | Kern: Automat, Zahlenfolge, Übergangsmatrix, Nenner, Zähler, Kürzen, Determinante, Eigenwerte, Klassen, Stellenzahl, Raten |
| `ref_constants.py` | Regler-Grenzen, Schwellen, Farben, Presets |
| `ref_evaluation.py` | Kennzahlen, Experimente, Verdikte, Formatierung, Probe der Reihe |
| `ref_layout.py` | Fester Kopf (Stylesheet) |
| `ref_pdf_export.py` | PDF der aktuellen Regeln (fpdf2) |
| `ref_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben) |
| `ref_scenario.py` | Regeln, Parser der Verbotsmuster, Zufallsregelsätze |
| `ref_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Handwerte, Orakel, Eigenschaften, Randfälle, Verdikte, Claims, Presets, Layout, AppTest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Aus einer Konstruktion eine erzeugende Funktion herleiten** (Baukasten, Catalan-Zahlen): Stück 3.
- **Partialbruchzerlegung und geschlossene Formel** (Binet) im Detail: nur der Satz a(n) ≈ c·λ₁ⁿ.
- **Grad des polynomiellen Wachstums** und Asymptotik allgemein (Singularitätsanalyse): Stück 9.
- **Zählen nach Parameter** (genau j Nachtschichten): Stück 8.
- **Verwandte Determinanten-Zähler:** `random-spanning-tree-demo` (Kirchhoff), Kasteleyn-Plan, Permanente-Plan: Nachbarn mit anderem Ziel (Determinante des Graphen, nicht von I − zM); die Demo verweist nur.
- **Ein Computer-Algebra-System als zweiter Rechenweg:** nicht gebaut; die Gegenproben sind Gauß-Elimination mit Brüchen und die Zustandsrekursion.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

Streamlit Cloud: Python-Version nach der Voreinstellung der Plattform (lokal `3.14`, CI `3.12`); der Code nutzt nur Merkmale, die in `3.12` laufen.

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und fpdf2.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
