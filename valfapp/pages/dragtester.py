import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ClientsideFunction


layout = html.Div(id="main", children=[
    html.Div(id="drag_container0", className="container", children=[

    html.Div(id="drag_container", className="container", children=[
        dbc.Card([
            dbc.CardHeader("Card 1"),
            dbc.CardBody(
                "Some content"
            ),
        ]),
        dbc.Card([
            dbc.CardHeader("Card 2"),
            dbc.CardBody(
                "Some other content"
            ),
        ]),
        dbc.Card([
            dbc.CardHeader("Card 3"),
            dbc.CardBody(
                "Some more content"
            ),
        ]),
    ], style={'padding': 10}) ,
        html.Div(id="drag_container2", className="container", children=[
        dbc.Card([
            dbc.CardHeader("Card a"),
            dbc.CardBody(
                "Some content"
            ),
        ]),
        dbc.Card([
            dbc.CardHeader("Card b"),
            dbc.CardBody(
                "Some other content"
            ),
        ]),
        dbc.Card([
            dbc.CardHeader("Card c"),
            dbc.CardBody(
                "Some more content"
            ),
        ]),
    ], style={'padding': 10} )
 ] )
])