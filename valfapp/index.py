### Import Packages ###
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
### Import Dash Instance and Pages ###
from valfapp.app import app
from pages import pg1, prod_eff, valuation_dashboard

### Page container ###

page_container = html.Div(
    children=[
        # represents the URL bar, doesn't render anything
        dcc.Location(
            id='url',
            refresh=False,
        ),
        # content will be rendered in this element
        html.Div(id='page-content')
    ]
)
### Index Page Layout ###
index_layout = dbc.Container([
    dbc.Row([html.H1("Valfsan Dashboards",
                     style={"text-align": "center", 'color': 'LightSteelBlue', 'font-weight': 'bold', 'margin-top': 20,
                            'padding': 50,
                            "width": 1500, "height": 100})]),
    dbc.Row([html.H2("Reports",
                     style={"text-align": "left", 'color': 'rgb(218, 255, 160)', 'font-weight': 'bold', 'margin-top': 5,
                            "margin-left": 40,
                            "width": 300, "height": 40, "border-bottom": "1px rgb(218, 255, 160) inset"})]),
    dbc.Row([
        html.Div(
            children=[
                dcc.Link(
                    children='1.Valuation ( Not Ready )',
                    href='/pg1',
                    style={"color": "DimGrey", "font-weight": "bold"}

                ),
                html.Br(),
                dcc.Link(
                    children='2.Manufacturing Dashboard',
                    href='/prod_eff',
                    style={"color": "DimGrey", "font-weight": "bold"}

                ),
                html.Br(),
                dcc.Link(
                    children='3.Costing',
                    href='/valuation_dashboard',
                    style={"color": "DimGrey", "font-weight": "bold"}

                ),
            ]
            , style={"padding": 30, "width": 300, "height": 500, "margin-left": 40,
                     'background-color': "rgb(218, 255, 160)", "opacity": 0.5}
        ),
    ])

], fluid=True)

### Set app layout to page container ###
app.layout = page_container
### Assemble all layouts ###
app.validation_layout = html.Div(
    children=[
        page_container,
        index_layout,
        pg1.layout,
        prod_eff.layout,
        valuation_dashboard.layout
    ]
)


### Update Page Container ###
@app.callback(
    Output(
        component_id='page-content',
        component_property='children',
    ),
    [Input(
        component_id='url',
        component_property='pathname',
    )]
)
def display_page(pathname):
    if pathname == '/':
        return index_layout
    elif pathname == '/pg1':
        return pg1.layout
    elif pathname == '/prod_eff':
        return prod_eff.layout
    elif pathname == '/valuation_dashboard':
        return valuation_dashboard.layout
    else:
        return '404'
