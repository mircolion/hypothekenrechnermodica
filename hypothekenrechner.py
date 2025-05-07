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
        # SARON von der SNB abrufen (Beispiel, kann angepasst werden)
        saron_response = requests.get('https://www.snb.ch/en/ifor/finmkt/id/finmkt_saron').json()
        saron_rate = saron_response['saron'] if 'saron' in saron_response else 0.2

        # Fiktive Festhypothekenzinsen (können durch APIs ersetzt werden)
        fest_5 = 1.8
        fest_10 = 2.2

        return {'SARON': saron_rate, 'Festhypothek 5 Jahre': fest_5, 'Festhypothek 10 Jahre': fest_10}
    except:
        return {'SARON': 0.2, 'Festhypothek 5 Jahre': 1.8, 'Festhypothek 10 Jahre': 2.2}

zinssaetze = get_current_rates()

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

app.layout = html.Div(style=background_style, children=[
    html.Div(style={"backgroundColor": "rgba(255,255,255,0.85)", "borderRadius": "12px", "padding": "20px"}, children=[
        html.H1("Hypothekenrechner", className="my-4"),

        dbc.Row([
            dbc.Col([dbc.Label("Hypothekenbetrag (CHF)"), dbc.Input(id="betrag", type="number", value=500000)]),
            dbc.Col([dbc.Label("Laufzeit (Jahre)"), dcc.Dropdown(id="laufzeit", options=[{"label": f"{i} Jahre", "value": i} for i in range(1, 31)], value=25)])
        ]),

        dbc.Row([
            dbc.Col([dbc.Label("Zinssatztyp"), dcc.Dropdown(id="zinssatztyp", options=[{"label": k, "value": k} for k in zinssaetze.keys()], value="SARON")]),
            dbc.Col([dbc.Label("Zinssatz (%)"), dbc.Input(id="zinssatz", type="number", value=zinssaetze["SARON"])])
        ]),

        dbc.Button("Berechnen", id="berechnen", color="success", className="mt-3"),
        html.Div(id="ergebnis")
    ])
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
    State("zinssatz", "value")
)
def berechne_hypothek(n_clicks, betrag, laufzeit, zinssatz):
    if not n_clicks or not betrag or not laufzeit or not zinssatz:
        return dbc.Alert("Bitte alle Felder ausfüllen.", color="danger")

    jahreszins = zinssatz / 100
    monatlicher_zins = jahreszins / 12
    anzahl_monate = laufzeit * 12

    annuitaet = betrag * monatlicher_zins / (1 - (1 + monatlicher_zins) ** -anzahl_monate)
    gesamtkosten = annuitaet * anzahl_monate

    return dbc.Card([
        dbc.CardBody([
            html.H4("Ergebnisse", className="card-title"),
            html.P(f"Monatliche Zahlung: CHF {annuitaet:,.2f}"),
            html.P(f"Gesamtkosten über {laufzeit} Jahre: CHF {gesamtkosten:,.2f}")
        ])
    ])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run_server(debug=False, host="0.0.0.0", port=port)
