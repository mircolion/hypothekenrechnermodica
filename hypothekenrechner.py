import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import requests
import os
import pdfkit

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Hypothekenrechner"

app.layout = dbc.Container([
    html.H1("Hypothekenrechner", className="my-4", style={"fontWeight": "bold"}),

    dbc.Row([
        dbc.Col([dbc.Label("Name", style={"fontWeight": "bold"}), dbc.Input(id="name", type="text")]),
        dbc.Col([dbc.Label("Adresse des Objekts", style={"fontWeight": "bold"}), dbc.Input(id="adresse", type="text")])
    ], className="mb-3"),

    dbc.Row([
        dbc.Col([dbc.Label("Alter", style={"fontWeight": "bold"}), dbc.Input(id="alter", type="number")]),
        dbc.Col([dbc.Label("Kaufpreis der Liegenschaft (CHF)", style={"fontWeight": "bold"}), dbc.Input(id="kaufpreis", type="number", value=500000)]),
        dbc.Col([dbc.Label("Eigenkapital (CHF)", style={"fontWeight": "bold"}), dbc.Input(id="eigenkapital", type="number", value=100000)])
    ], className="mb-3"),

    dbc.Row([
        dbc.Col([dbc.Label("Cash", style={"fontWeight": "bold"}), dbc.Input(id="cash", type="number", value=0)]),
        dbc.Col([dbc.Label("2. Säule", style={"fontWeight": "bold"}), dbc.Input(id="saule2", type="number", value=0)]),
        dbc.Col([dbc.Label("3. Säule", style={"fontWeight": "bold"}), dbc.Input(id="saule3", type="number", value=0)])
    ], className="mb-3"),

    dbc.Row([
        dbc.Col([dbc.Label("Jährliches Bruttoeinkommen (CHF)", style={"fontWeight": "bold"}), dbc.Input(id="einkommen", type="number", value=80000)]),
        dbc.Col([dbc.Label("Amortisation (Jahre)", style={"fontWeight": "bold"}), dbc.Input(id="amortisation", type="number", value=20)])
    ], className="mb-3"),

    dbc.Row([
        dbc.Col([dbc.Label("Hypothekentyp", style={"fontWeight": "bold"}), dcc.Dropdown(id="hypothektyp", options=[
            {"label": "SARON", "value": "saron"},
            {"label": "5 Jahre Festhypothek", "value": "fest5"},
            {"label": "10 Jahre Festhypothek", "value": "fest10"}
        ], value="saron")]),
    ]),

    html.Br(),
    html.Button("Berechnung als PDF herunterladen", id="download_pdf", className="btn btn-primary"),
    html.Br(),
    html.Div(id="ergebnis")
], style={"padding": "30px", "fontFamily": "Arial Narrow"})

@app.callback(
    Output("ergebnis", "children"),
    Input("kaufpreis", "value"),
    Input("eigenkapital", "value"),
    Input("cash", "value"),
    Input("saule2", "value"),
    Input("saule3", "value"),
    Input("einkommen", "value"),
    Input("amortisation", "value"),
    Input("hypothektyp", "value")
)
def update_ergebnis(kaufpreis, eigenkapital, cash, saule2, saule3, einkommen, amortisation, hypothektyp):
    total_eigenkapital = eigenkapital + cash + saule2 + saule3
    hypothek = kaufpreis - total_eigenkapital

    zinssatz_1 = 5.0
    zinssatz_2 = 6.0

    hypothek_1 = hypothek * 0.66
    hypothek_2 = hypothek * 0.14

    amortisation_rate = hypothek_2 / amortisation

    gesamtkosten = hypothek_1 * (zinssatz_1 / 100) + hypothek_2 * (zinssatz_2 / 100) + amortisation_rate

    pdf_content = f"""
    Hypothekenrechner
    Name: {name}
    Adresse des Objekts: {adresse}
    Alter: {alter}

    Kaufpreis: CHF {kaufpreis:,.2f}
    Eigenkapital: CHF {total_eigenkapital:,.2f}
    Hypothek: CHF {hypothek:,.2f}

    Jährliche Kosten: CHF {gesamtkosten:,.2f}
    Monatliche Kosten: CHF {(gesamtkosten / 12):,.2f}
    Amortisation: CHF {amortisation_rate:,.2f} pro Jahr
    """

    return html.Div([
        html.H4(f"Hypothekenbetrag: CHF {hypothek:,.2f}", style={"fontWeight": "bold"}),
        html.P(f"Monatliche Kosten: CHF {(gesamtkosten / 12):,.2f}", style={"fontWeight": "bold"}),
        html.P(f"Jährliche Kosten: CHF {gesamtkosten:,.2f}", style={"fontWeight": "bold"}),
        html.P(f"Amortisation: CHF {amortisation_rate:,.2f} pro Jahr", style={"fontWeight": "bold"})
    ])
