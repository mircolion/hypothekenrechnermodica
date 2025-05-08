import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import os
import io
from xhtml2pdf import pisa
from flask import send_file, Flask

server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Hypothekenrechner"

app.layout = dbc.Container([
    html.H1("Hypothekenrechner", className="my-4", style={"fontWeight": "bold", "textAlign": "center", "color": "white"}),

    dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([dbc.Label("Name", style={"fontWeight": "bold", "color": "white"}), dbc.Input(id="name", type="text", placeholder="Max Mustermann")]),
                dbc.Col([dbc.Label("Adresse des Objekts", style={"fontWeight": "bold", "color": "white"}), dbc.Input(id="adresse", type="text", placeholder="Musterstrasse 1, 8000 Zürich")]),
                dbc.Col([dbc.Label("Alter", style={"fontWeight": "bold", "color": "white"}), dbc.Input(id="alter", type="number", placeholder="30")]),
            ], className="mb-3"),

            html.Hr(),

            dbc.Row([
                dbc.Col([dbc.Label("Kaufpreis der Liegenschaft (CHF)", style={"fontWeight": "bold", "color": "white"}), dbc.Input(id="kaufpreis", type="number", value=500000)]),
                dbc.Col([dbc.Label("Eigenkapital (CHF)", style={"fontWeight": "bold", "color": "white"}), dbc.Input(id="eigenkapital", type="number", value=100000)]),
                dbc.Col([dbc.Label("Cash", style={"fontWeight": "bold", "color": "white"}), dbc.Input(id="cash", type="number", value=0)])
            ], className="mb-3"),

            dbc.Row([
                dbc.Col([dbc.Label("2. Säule", style={"fontWeight": "bold", "color": "white"}), dbc.Input(id="saule2", type="number", value=0)]),
                dbc.Col([dbc.Label("3. Säule", style={"fontWeight": "bold", "color": "white"}), dbc.Input(id="saule3", type="number", value=0)]),
                dbc.Col([dbc.Label("Jährliches Bruttoeinkommen (CHF)", style={"fontWeight": "bold", "color": "white"}), dbc.Input(id="einkommen", type="number", value=80000)])
            ], className="mb-3"),

            dbc.Row([
                dbc.Col([dbc.Label("Amortisation (Jahre)", style={"fontWeight": "bold", "color": "white"}), dbc.Input(id="amortisation", type="number", value=20)]),
                dbc.Col([dbc.Label("Hypothekentyp", style={"fontWeight": "bold", "color": "white"}), dcc.Dropdown(id="hypothektyp", options=[
                    {"label": "SARON", "value": "saron"},
                    {"label": "5 Jahre Festhypothek", "value": "fest5"},
                    {"label": "10 Jahre Festhypothek", "value": "fest10"}
                ], value="saron")])
            ]),

            html.Hr(),

            html.Button("Berechnung als PDF herunterladen", id="download_pdf", className="btn btn-primary"),
            html.Br(),
            html.Div(id="ergebnis")
        ])
    ], style={"padding": "20px", "backgroundColor": "#2C3E50", "boxShadow": "0 0 15px rgba(0,0,0,0.2)", "borderRadius": "15px"})
], style={"padding": "30px", "fontFamily": "Arial Narrow", "maxWidth": "800px", "margin": "auto", "backgroundColor": "#34495E"})

@app.callback(
    Output("ergebnis", "children"),
    Input("kaufpreis", "value"),
    Input("eigenkapital", "value"),
    Input("cash", "value"),
    Input("saule2", "value"),
    Input("saule3", "value"),
    Input("einkommen", "value"),
    Input("amortisation", "value"),
    Input("hypothektyp", "value"),
)
def calculate(kaufpreis, eigenkapital, cash, saule2, saule3, einkommen, amortisation, hypothektyp):
    total_equity = eigenkapital + cash + saule2 + saule3
    loan_amount = kaufpreis - total_equity

    interest_rate = {"saron": 1.25, "fest5": 1.8, "fest10": 2.2}[hypothektyp]
    yearly_interest = loan_amount * (interest_rate / 100)
    amortization_payment = loan_amount / amortisation

    return html.Div([
        html.H4(f"Gesamtes Eigenkapital: CHF {total_equity:,.2f}", style={"color": "white"}),
        html.H4(f"Hypothekenbetrag: CHF {loan_amount:,.2f}", style={"color": "white"}),
        html.P(f"Zinssatz: {interest_rate:.2f}%", style={"color": "white"}),
        html.P(f"Jährliche Zinszahlung: CHF {yearly_interest:,.2f}", style={"color": "white"}),
        html.P(f"Jährliche Amortisation: CHF {amortization_payment:,.2f}", style={"color": "white"})
    ])

@app.server.route("/download_pdf")
def download_pdf():
    pdf_content = f"""
    <h1>Hypothekenrechner</h1>
    <p>Hypothekenberechnung für Ihr Objekt</p>
    <ul>
        <li>Name: {name}</li>
        <li>Adresse: {adresse}</li>
        <li>Alter: {alter}</li>
        <li>Gesamtes Eigenkapital: CHF {total_equity:,.2f}</li>
        <li>Hypothekenbetrag: CHF {loan_amount:,.2f}</li>
        <li>Zinssatz: {interest_rate:.2f}%</li>
        <li>Jährliche Zinszahlung: CHF {yearly_interest:,.2f}</li>
        <li>Jährliche Amortisation: CHF {amortization_payment:,.2f}</li>
    </ul>
    """
    pdf = io.BytesIO()
    pisa.CreatePDF(io.StringIO(pdf_content), pdf)
    pdf.seek(0)
    
    return send_file(pdf, as_attachment=True, download_name="Hypothekenrechner_Berechnung.pdf")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
