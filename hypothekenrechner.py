import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import requests
import os

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Hypothekenrechner"

# Hintergrundbild und Layout-Stil
background_style = {
    "backgroundImage": "url('https://raw.githubusercontent.com/mircolion/wohnungsvergleichmodica/main/woods.jpg')",
    "backgroundSize": "cover",
    "backgroundRepeat": "no-repeat",
    "backgroundPosition": "center",
    "minHeight": "100vh",
    "padding": "30px",
    "fontFamily": "Arial Narrow",
    "backgroundColor": "rgba(255, 255, 255, 0.25)",
    "backgroundBlendMode": "lighten"
}

app.layout = dbc.Container([
    html.H1("Hypothekenrechner", className="my-4"),
    dbc.Row([
        dbc.Col([dbc.Label("Kaufpreis der Liegenschaft (CHF)", style={"fontWeight": "bold"}), dbc.Input(id="kaufpreis", type="number", value=500000)]),
        dbc.Col([dbc.Label("Eigenkapital (CHF)", style={"fontWeight": "bold"}), dbc.Input(id="eigenkapital", type="number", value=100000)]),
        dbc.Col([dbc.Label("Jährliches Bruttoeinkommen (CHF)", style={"fontWeight": "bold"}), dbc.Input(id="einkommen", type="number", value=80000)])
    ], className="mb-3"),

    dbc.Row([
        dbc.Col([dbc.Label("Hypothekentyp", style={"fontWeight": "bold"}), dcc.Dropdown(id="hypothektyp", options=[
            {"label": "SARON", "value": "saron"},
            {"label": "5 Jahre Festhypothek", "value": "fest5"},
            {"label": "10 Jahre Festhypothek", "value": "fest10"}
        ], value="saron")]),
    ]),

    html.Br(),
    html.Div(id="ergebnis")
], style=background_style)

@app.callback(
    Output("ergebnis", "children"),
    Input("kaufpreis", "value"),
    Input("eigenkapital", "value"),
    Input("einkommen", "value"),
    Input("hypothektyp", "value")
)
def update_ergebnis(kaufpreis, eigenkapital, einkommen, hypothektyp):
    if not all([kaufpreis, eigenkapital, einkommen]):
        return "Bitte alle Felder ausfüllen."

    hypothek = kaufpreis - eigenkapital
    if hypothek <= 0:
        return "Eigenkapital deckt den Kaufpreis vollständig."

    zinssatz_1 = 5.0
    zinssatz_2 = 6.0
    belehnung = 0.8

    hypothek_1 = hypothek * 0.66
    hypothek_2 = hypothek * 0.14

    jahreszins_1 = hypothek_1 * (zinssatz_1 / 100)
    jahreszins_2 = hypothek_2 * (zinssatz_2 / 100)
    gesamtkosten = jahreszins_1 + jahreszins_2 + (kaufpreis * 0.01)

    nebenzinsen = kaufpreis * 0.01

    tragbarkeit = einkommen * 0.33
    tragbar = "Ja" if gesamtkosten <= tragbarkeit else "Nein"

    return html.Div([
        html.H4(f"Hypothekenbetrag: CHF {hypothek:,.2f}", style={"fontWeight": "bold"}),
        html.P(f"1. Hypothek: CHF {hypothek_1:,.2f} @ {zinssatz_1:.2f}%", style={"fontWeight": "bold"}),
        html.P(f"2. Hypothek: CHF {hypothek_2:,.2f} @ {zinssatz_2:.2f}%", style={"fontWeight": "bold"}),
        html.P(f"Monatliche Kosten: CHF {(gesamtkosten / 12):,.2f}", style={"fontWeight": "bold"}),
        html.P(f"Jährliche Kosten: CHF {gesamtkosten:,.2f}", style={"fontWeight": "bold"}),
        html.P(f"Nebenkosten: CHF {nebenzinsen:,.2f}", style={"fontWeight": "bold"}),
        html.Hr(),
        html.P(f"Tragbarkeit: {tragbar} (Max. Belastung: CHF {tragbarkeit:,.2f})", style={"fontWeight": "bold"})
    ])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(debug=False, host="0.0.0.0", port=port)
