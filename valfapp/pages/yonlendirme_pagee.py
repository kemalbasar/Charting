from dash import dcc, html
import dash_bootstrap_components as dbc

from valfapp.layouts import nav_bar

layout = html.Div([
    nav_bar,
    dbc.Row([
        dbc.Col([
            dbc.ListGroup([
                dbc.ListGroupItem(html.H2("Cnc:"),style={"background-color":"white", "color":"#214b9c"}),
                dbc.ListGroupItem(html.H2("Montaj:"),style={"background-color":"white", "color":"#214b9c"}),
                dbc.ListGroupItem(html.H2("Cncto:"),style={"background-color":"white", "color":"#214b9c"}),
                dbc.ListGroupItem(html.H2("Pres-1:"),style={"background-color":"white", "color":"#214b9c"}),
                dbc.ListGroupItem(html.H2("Pres-2:"),style={"background-color":"white", "color":"#214b9c"})
            ])
        ], md=2, className="mt-5", style={"height": "500px"}),
        dbc.Col([
            html.H2("Günlük"),
            dbc.ListGroup([
                dbc.ListGroupItem(html.A(href="/adrcncreal", children=dbc.Button("CNC-GÜNLÜK", n_clicks=0, color="primary", className='prd-button')),style={"background-color":"white"}),
                dbc.ListGroupItem(html.A(href="/adrmontajreal", children=dbc.Button("MONTAJ-GÜNLÜK", n_clicks=0, color="primary", className='prd-button')),style={"background-color":"white"}),
                dbc.ListGroupItem(html.A(href="/adrcnctornareal", children=dbc.Button("CNC-TO-GÜNLÜK", n_clicks=0, color="primary", className='prd-button')),style={"background-color":"white"}),
                dbc.ListGroupItem(html.A(href="/adrpres1real", children=dbc.Button("PRES-1-GÜNLÜK", n_clicks=0, color="primary", className='prd-button')),style={"background-color":"white"}),
                dbc.ListGroupItem(html.A(href="/adrpres2real", children=dbc.Button("PRES-2-GÜNLÜK", n_clicks=0, color="primary", className='prd-button')),style={"background-color":"white"}),
            ])
        ], md=3, className="text-center"),
        dbc.Col([
            html.H2("Haftalık"),
            dbc.ListGroup([ 
                dbc.ListGroupItem(html.A(href="/adrcncweekreal", children=dbc.Button("CNC-HAFTALIK", n_clicks=0, color="primary", className='prd-button')),style={"background-color":"white"}),
                dbc.ListGroupItem(html.A(href="/adrmontajweekreal", children=dbc.Button("MONTAJ-HAFTALIK", n_clicks=0, color="primary", className='prd-button')),style={"background-color":"white"}),
                dbc.ListGroupItem(html.A(href="/adrcnctornaweekreal", children=dbc.Button("CNC-TO-HAFTALIK", n_clicks=0, color="primary", className='prd-button')),style={"background-color":"white"}),
                dbc.ListGroupItem(html.A(href="/adrpres1weekreal", children=dbc.Button("PRES-1-HAFTALIK", n_clicks=0, color="primary", className='prd-button')),style={"background-color":"white"}),
                dbc.ListGroupItem(html.A(href="/adrpres2weekreal", children=dbc.Button("PRES-2-HAFTALIK", n_clicks=0, color="primary", className='prd-button')),style={"background-color":"white"}),
            ])
        ], md=3, className="text-center"),
        dbc.Col([
            html.H2("Aylık"),
            dbc.ListGroup([
                dbc.ListGroupItem(html.A(href="/adrcncmonthreal", children=dbc.Button("CNC-AYLIK", n_clicks=0, color="primary", className='prd-button')),style={"background-color":"white"}),
                dbc.ListGroupItem(html.A(href="/adrmontajmonthreal", children=dbc.Button("MONTAJ-AYLIK", n_clicks=0, color="primary", className='prd-button')),style={"background-color":"white"}),
                dbc.ListGroupItem(html.A(href="/adrcnctornamonthreal", children=dbc.Button("CNC-TO-AYLIK", n_clicks=0, color="primary", className='prd-button')),style={"background-color":"white"}),
                dbc.ListGroupItem(html.A(href="/adrpres1monthreal", children=dbc.Button("PRES-1-AYLIK", n_clicks=0, color="primary", className='prd-button')),style={"background-color":"white"}),
                dbc.ListGroupItem(html.A(href="/adrpres2monthreal", children=dbc.Button("PRES-2-AYLIK", n_clicks=0, color="primary", className='prd-button')),style={"background-color":"white"}),
            ])
        ], md=3, className="text-center"),
    ], style={"margin-left": "100px"})
])

