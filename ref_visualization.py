"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import math

import plotly.graph_objects as go

import ref_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=50, b=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def _circle(radius: float, points: int = 121):
    t = [2 * math.pi * i / (points - 1) for i in range(points)]
    return [radius * math.cos(x) for x in t], [radius * math.sin(x) for x in t]


def build_roots(growth):
    """Eigenwerte λ in der komplexen Ebene mit dem Einheitskreis (Betrag 1) und dem Kreis um den größten Betrag; der größte Eigenwert ist hervorgehoben.

    Die Pole der erzeugenden Funktion liegen bei z = 1/λ; je größer |λ|, desto näher am Ursprung."""
    fig = go.Figure()
    roots = list(growth.roots)
    limit = max([1.0] + [abs(z) for z in roots]) * 1.25
    x, y = _circle(1.0)
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name="Betrag 1", line=dict(color=C.COLOR_GRID, width=1.5, dash="dash"), hoverinfo="skip"))
    if growth.lam1 is not None and abs(growth.lam1 - 1.0) > 1e-9:
        x, y = _circle(growth.lam1)
        fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name="Betrag des größten Eigenwerts", line=dict(color=C.COLOR_DOMINANT, width=1.2, dash="dot"), hoverinfo="skip"))
    rest = [z for z in roots if growth.lam1 is None or abs(abs(z) - growth.lam1) >= C.CLASS_TOL]
    top = [z for z in roots if growth.lam1 is not None and abs(abs(z) - growth.lam1) < C.CLASS_TOL]
    if rest:
        fig.add_trace(go.Scatter(x=[z.real for z in rest], y=[z.imag for z in rest], mode="markers", name="Eigenwerte",
                                 marker=dict(size=10, color=C.COLOR_ROOT), hovertemplate="λ = %{x:.4f} %{y:+.4f} i<extra></extra>"))
    if top:
        fig.add_trace(go.Scatter(x=[z.real for z in top], y=[z.imag for z in top], mode="markers", name="größter Betrag",
                                 marker=dict(size=13, color=C.COLOR_DOMINANT, symbol="diamond"), hovertemplate="λ = %{x:.4f} %{y:+.4f} i<extra></extra>"))
    # Gleicher Maßstab: scaleanchor nur mit automatischem Bereich (ein fester `range` wird bei schmaler Anfangsbreite falsch hochgerechnet, DEMO-PLAYBOOK §3);
    # den Rand erzwingen zwei unsichtbare Marker an den Ecken.
    fig.add_trace(go.Scatter(x=[-limit, limit], y=[-limit, limit], mode="markers", marker=dict(size=1, opacity=0), hoverinfo="skip", showlegend=False))
    fig.update_xaxes(title_text="Realteil", zeroline=True)
    fig.update_yaxes(title_text="Imaginärteil", scaleanchor="x", scaleratio=1, zeroline=True)
    return _base(fig, 420)


def build_ratio_error(errors: list):
    """Relativer Fehler des Quotienten a(n)/a(n−1) gegen den größten Eigenwert über n (logarithmische Achse; Fehler 0 wird als 1e-17 gezeichnet)."""
    pts = [(n, max(e, 1e-17)) for n, e in errors if e is not None]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[n for n, _ in pts], y=[e for _, e in pts], mode="lines+markers", name="Fehler des Quotienten", line=dict(color=C.COLOR_LINE, width=2.5), marker=dict(size=5)))
    fig.add_hline(y=C.SPEED_EPS, line=dict(color=C.COLOR_DOMINANT, width=1.2, dash="dash"), annotation_text=f"{C.SPEED_EPS:.0e}", annotation_position="top right")
    fig.update_xaxes(title_text="n")
    fig.update_yaxes(title_text="relativer Fehler (logarithmisch)", type="log")
    return _base(fig)


def build_classes(res: dict):
    """Zahl der Zufallsregelsätze je Wachstumsklasse (aus den Eigenwerten und aus der gezählten Folge nebeneinander)."""
    kinds = ["exponentiell", "polynomiell", "endlich"]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=kinds, y=[res["from_roots"].get(k, 0) for k in kinds], name="aus den Eigenwerten", marker_color=C.COLOR_ROOT))
    fig.add_trace(go.Bar(x=kinds, y=[res["from_seq"].get(k, 0) for k in kinds], name="aus der gezählten Folge", marker_color=C.COLOR_LINE))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Regelsätze")
    return _base(fig, 320)
