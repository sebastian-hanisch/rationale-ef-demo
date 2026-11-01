"""PDF-Export der aktuellen Regeln mit Nenner, Zähler, Rekursion und Wachstum (fpdf2). Kernschriften sind latin-1: Umlaute gehen, Sonderzeichen werden ersetzt."""

from __future__ import annotations

from fpdf import FPDF

from ref_evaluation import Analysis, de, poly_text, recurrence_text

_REPLACE = {"→": "->", "–": "-", "—": "-", "−": "-", "≤": "<=", "≥": ">=", "·": "*", "€": "EUR", "„": '"', "“": '"', "λ": "lambda", "₁": "1", "₂": "2"}
MAX_ROWS = 40


def _s(text) -> str:
    out = str(text)
    for old, new in _REPLACE.items():
        out = out.replace(old, new)
    for sup, digit in zip("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789"):
        out = out.replace(sup, "^" + digit)
    return out.encode("latin-1", "replace").decode("latin-1")


def build_pdf(a: Analysis) -> bytes:
    s, g, rat = a.settings, a.growth, a.rat
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, _s("Erzeugende Funktion einer Zählfolge"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    patterns = ", ".join(a.rules.patterns) if a.rules.patterns else "keine"
    pdf.multi_cell(0, 5, _s(f"Alphabet: {' '.join(a.rules.alphabet)}. Verbotene Teilfolgen: {patterns}. Alles simuliert."), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    lines = [
        f"Zustände des Automaten: {a.auto.size}.",
        f"Nenner Q(z) = {poly_text(rat.qr)} (Grad {rat.deg_q}).",
        f"Zähler P(z) = {poly_text(rat.pr)} (Grad {rat.deg_p}).",
        f"Rekursion: {recurrence_text(rat.qr)}, gültig ab n = {rat.valid_from}.",
        f"Wachstumsklasse: {g.kind}" + (f", größter Eigenwert {de(g.lam1, 6)}." if g.lam1 is not None else "."),
    ]
    for line in lines:
        pdf.multi_cell(0, 5, _s(line), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    head, widths = ["n", "a(n)"], [22, 100]
    pdf.set_font("Helvetica", "B", 9)
    for h, w in zip(head, widths):
        pdf.cell(w, 6, _s(h), border=1)
    pdf.ln()
    pdf.set_font("Helvetica", "", 9)
    for n in range(min(len(a.seq), MAX_ROWS)):
        for v, w in zip([str(n), str(a.seq[n]) if len(str(a.seq[n])) < 60 else "..."], widths):
            pdf.cell(w, 5.5, _s(v), border=1)
        pdf.ln()
    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 4, _s(f"Länge n bis {s.n}. Q(z) = det(I - zM) mit der Übergangsmatrix M des Automaten. Quelle: rationale-ef-demo, Sebastian Hanisch."), new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())
