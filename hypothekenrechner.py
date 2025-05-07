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
        saron = 1.25  # Hier könnte der SARON automatisch über eine API abgerufen werden
        festhypothek_5 = 1.8  # Beispielwerte
        festhypothek_10 = 2.2
        return saron, festhypothek_5, festhypothek_10
    except:
        return 1.25, 1.8, 2.2

saron, festhypothek_5, festhypothek_10 = get_current_rates()

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
    dbc.Container([
        html.H1("Hypothekenrechner"),
        html.Hr(),

        dbc.Row([
            dbc.Col([
                dbc.Label("Kaufpreis der Liegenschaft (CHF)"),
                dbc.Input(id='kaufpreis', type='number', value=800000)
            ]),
            dbc.Col([
                dbc.Label("Eigenkapital (CHF)"),
                dbc.Input(id='eigenkapital', type='number', value=200000)
            ])
        ]),

        html.Br(),

        dbc.Row([
            dbc.Col([
                dbc.Label("Zinstyp"),
                dcc.Dropdown(
                    id='zinssatztyp',
                    options=[
                        {"label": "SARON", "value": "SARON"},
                        {"label": "Festhypothek 5 Jahre", "value": "Festhypothek 5"},
                        {"label": "Festhypothek 10 Jahre", "value": "Festhypothek 10"}
                    ],
                    value="SARON"
                )
            ]),
            dbc.Col([
                dbc.Label("Zinssatz (%)"),
                dcc.Input(id='zinssatz', type='number', value=saron, readOnly=True)
            ])
        ]),

        html.Br(),

        dbc.Button("Berechnen", id='berechnen', color='success', style={"fontFamily": "Arial Narrow"}),
        html.Br(), html.Br(),
        html.Div(id='ergebnis')
    ])
])

@app.callback(
    Output('zinssatz', 'value'),
    Input('zinssatztyp', 'value')
)
def update_zinssatz(typ):
    if typ == "SARON":
        return saron
    elif typ == "Festhypothek 5":
        return festhypothek_5
    elif typ == "Festhypothek 10":
        return festhypothek_10

@app.callback(
    Output('ergebnis', 'children'),
    Input('berechnen', 'n_clicks'),
    State('kaufpreis', 'value'),
    State('eigenkapital', 'value'),
    State('zinssatz', 'value')
)
def berechne_hypothek(n_clicks, kaufpreis, eigenkapital, zinssatz):
    if not n_clicks:
        return ""

    hypothek = kaufpreis - eigenkapital
    jahreszins = zinssatz / 100
    jahreskosten = hypothek * jahreszins
    monatliche_kosten = jahreskosten / 12

    tragbarkeit = (monatliche_kosten * 12) / (0.33 * kaufpreis)

    return dbc.Card([
        dbc.CardBody([
            html.H4("Ergebnisse", className="card-title"),
            html.P(f"Hypothekenbetrag: CHF {hypothek:,.2f}"),
            html.P(f"Monatliche Zinskosten: CHF {monatliche_kosten:,.2f}"),
            html.P(f"Tragbarkeit: {tragbarkeit:.2%}")
        ])
    ])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(debug=False, host="0.0.0.0", port=port)
