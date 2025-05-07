import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import requests
import os

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Hypothekenrechner"

# Aktuelle Zinssätze automatisch abrufen
def get_current_rates():
    try:
        saron = 1.25
        festhypothek_5 = 1.8
        festhypothek_10 = 2.2
        return saron, festhypothek_5, festhypothek_10
    except:
        return 1.25, 1.8, 2.2

saron, festhypothek_5, festhypothek_10 = get_current_rates()

app.layout = dbc.Container([
    html.H1("Hypothekenrechner", className="my-4"),
    dbc.Row([
        dbc.Col([dbc.Label("Kaufpreis der Liegenschaft (CHF)"), dbc.Input(id="kaufpreis", type="number", value=500000)]),
        dbc.Col([dbc.Label("Eigenkapital (CHF)"), dbc.Input(id="eigenkapital", type="number", value=100000)]),
        dbc.Col([dbc.Label("Jährliches Bruttoeinkommen (CHF)"), dbc.Input(id="einkommen", type="number", value=80000)])
    ], className="mb-3"),

    dbc.Row([
        dbc.Col([dbc.Label("Hypothekentyp"), dcc.Dropdown(id="hypothektyp", options=[
            {"label": "SARON", "value": "saron"},
            {"label": "5 Jahre Festhypothek", "value": "fest5"},
            {"label": "10 Jahre Festhypothek", "value": "fest10"}
        ], value="saron")]),
    ]),

    html.Br(),
    html.Div(id="ergebnis")
])

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

    if hypothektyp == "saron":
        zinssatz = saron
    elif hypothektyp == "fest5":
        zinssatz = festhypothek_5
    else:
        zinssatz = festhypothek_10

    jahreszins = hypothek * (zinssatz / 100)
    monatliche_zinszahlung = jahreszins / 12

    # Tragbarkeit berechnen (max 33% des Bruttoeinkommens)
    tragbarkeit = einkommen * 0.33
    tragbar = "Ja" if jahreszins <= tragbarkeit else "Nein"

    return html.Div([
        html.H4(f"Hypothekenbetrag: CHF {hypothek:,.2f}"),
        html.P(f"Zinssatz: {zinssatz:.2f}%"),
        html.P(f"Monatliche Zinszahlung: CHF {monatliche_zinszahlung:,.2f}"),
        html.P(f"Jährliche Zinszahlung: CHF {jahreszins:,.2f}"),
        html.Hr(),
        html.P(f"Tragbarkeit: {tragbar} (Max. Belastung: CHF {tragbarkeit:,.2f})")
    ])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(debug=False, host="0.0.0.0", port=port)
