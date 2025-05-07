import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import requests

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Hypothekenrechner"

# Beispielhafte Zinssätze (in Prozent)
zinssaetze = {
    "SARON": 1.25,
    "Festhypothek 5 Jahre": 1.8,
    "Festhypothek 10 Jahre": 2.2
}

app.layout = dbc.Container([
    html.H1("Hypothekenrechner", className="my-4"),
    dbc.Row([
        dbc.Col([
            dbc.Label("Hypothekenbetrag (CHF)"),
            dbc.Input(id="betrag", type="number", value=500000, step=1000)
        ]),
        dbc.Col([
            dbc.Label("Laufzeit (Jahre)"),
            dcc.Dropdown(
                id="laufzeit",
                options=[{"label": f"{i} Jahre", "value": i} for i in range(1, 31)],
                value=25
            )
        ]),
        dbc.Col([
            dbc.Label("Zinssatztyp"),
            dcc.Dropdown(
                id="zinssatztyp",
                options=[{"label": k, "value": k} for k in zinssaetze.keys()],
                value="SARON"
            )
        ])
    ], className="mb-3"),
    dbc.Row([
        dbc.Col([
            dbc.Label("Amortisation pro Jahr (CHF)"),
            dbc.Input(id="amortisation", type="number", value=10000, step=1000)
        ]),
        dbc.Col([
            dbc.Label("Zinssatz (%)"),
            dbc.Input(id="zinssatz", type="number", value=zinssaetze["SARON"], step=0.01)
        ])
    ], className="mb-3"),
    dbc.Button("Berechnen", id="berechnen", color="primary", className="mb-3"),
    html.Div(id="ergebnis")
])

@app.callback(
    Output("zinssatz", "value"),
    Input("zinssatztyp", "value")
)
def update_zinssatz(typ):
    return zinssaetze.get(typ, 1.5)

@app.callback(
    Output("ergebnis", "children"),
    Input("berechnen", "n_clicks"),
    State("betrag", "value"),
    State("laufzeit", "value"),
    State("zinssatz", "value"),
    State("amortisation", "value")
)
def berechne_hypothek(n_clicks, betrag, laufzeit, zinssatz, amortisation):
    if not n_clicks:
        return ""
    if not all([betrag, laufzeit, zinssatz]):
        return dbc.Alert("Bitte alle Felder ausfüllen.", color="danger")

    jahreszins = zinssatz / 100
    monatlicher_zins = jahreszins / 12
    anzahl_monate = laufzeit * 12

    # Monatliche Zinszahlung (Annuität)
    if monatlicher_zins > 0:
        annuitaet = betrag * (monatlicher_zins / (1 - (1 + monatlicher_zins) ** -anzahl_monate))
    else:
        annuitaet = betrag / anzahl_monate

    # Gesamtkosten
    gesamt
