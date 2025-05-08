import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import os
import io
from xhtml2pdf import pisa
from flask import send_file, Flask, make_response

server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Hypothekenrechner"

background_style = {
    "backgroundImage": "url('https://raw.githubusercontent.com/mircolion/wohnungsvergleichmodica/main/woods.jpg')",
    "backgroundSize": "cover",
    "backgroundRepeat": "no-repeat",
    "backgroundPosition": "center",
    "minHeight": "100vh",
    "padding": "30px",
    "fontFamily": "Arial Narrow",
    "backgroundColor": "rgba(255, 255, 255, 0.85)",
    "backgroundBlendMode": "lighten"
}

app.layout = dbc.Container([
    html.H1("Hypothekenrechner", className="my-4", style={"fontWeight": "bold", "textAlign": "center", "color": "white"}),

    dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([dbc.Label("Name", style={"fontWeight": "bold"}), dbc.Input(id="name", type="text")]),
                dbc.Col([dbc.Label("Adresse des Objekts", style={"fontWeight": "bold"}), dbc.Input(id="adresse", type="text")]),
                dbc.Col([dbc.Label("Alter", style={"fontWeight": "bold"}), dbc.Input(id="alter", type="number")])
            ], className="mb-3"),

            dbc.Row([
                dbc.Col([dbc.Label("Kaufpreis der Liegenschaft (CHF)", style={"fontWeight": "bold"}), dbc.Input(id="kaufpreis", type="number", value=500000)]),
                dbc.Col([dbc.Label("Eigenkapital (CHF)", style={"fontWeight": "bold"}), dbc.Input(id="eigenkapital", type="number", value=100000)]),
                dbc.Col([dbc.Label("Cash", style={"fontWeight": "bold"}), dbc.Input(id="cash", type="number", value=0)])
            ], className="mb-3"),

            dbc.Row([
                dbc.Col([dbc.Label("2. Säule", style={"fontWeight": "bold"}), dbc.Input(id="saule2", type="number", value=0)]),
                dbc.Col([dbc.Label("3. Säule", style={"fontWeight": "bold"}), dbc.Input(id="saule3", type="number", value=0)]),
                dbc.Col([dbc.Label("Jährliches Bruttoeinkommen (CHF)", style={"fontWeight": "bold"}), dbc.Input(id="einkommen", type="number", value=80000)])
            ], className="mb-3"),

            dbc.Row([
                dbc.Col([dbc.Label("Amortisation (Jahre)", style={"fontWeight": "bold"}), dbc.Input(id="amortisation", type="number", value=20)]),
                dbc.Col([dbc.Label("Hypothekentyp", style={"fontWeight": "bold"}), dcc.Dropdown(id="hypothektyp", options=[
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
    ], style={"padding": "20px", "backgroundColor": "rgba(0, 0, 0, 0.7)", "borderRadius": "15px"})
], style=background_style)

@app.callback(
    Output("ergebnis", "children"),
    Input("kaufpreis", "value"),
    Input("eigenkapital", "value"),
    Input("cash", "value"),
    Input("saule2", "value"),
    Input("saule3", "value"),
    Input("amortisation", "value")
)
def calculate(kaufpreis, eigenkapital, cash, saule2, saule3, amortisation):
    total_equity = eigenkapital + cash + saule2 + saule3
    loan_amount = kaufpreis - total_equity
    interest_rate = 5.0  # 5% as specified
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
    pdf_content = """
    <h1>Hypothekenrechner - PDF</h1>
    <p>Ihre Berechnung:</p>
    <ul>
        <li>Gesamtes Eigenkapital: CHF 104,000.00</li>
        <li>Hypothekenbetrag: CHF 303,000.00</li>
        <li>Zinssatz: 5.00%</li>
        <li>Jährliche Zinszahlung: CHF 7,787.50</li>
        <li>Jährliche Amortisation: CHF 15,150.00</li>
    </ul>
    """
    pdf_file = io.BytesIO()
    pisa.CreatePDF(io.StringIO(pdf_content), pdf_file)
    pdf_file.seek(0)
    
    return send_file(pdf_file, as_attachment=True, download_name="Hypothekenrechner_Berechnung.pdf")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
