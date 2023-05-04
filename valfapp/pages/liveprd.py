import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from valfapp.app import app

from valfapp.pages import livecnc, livepres

# Define the Dash app

# Define the layout for the main page
layout = html.Div([
    html.H1('Maliyet Merkezleri'),
    dcc.Link('CNC', href='/liveprd/livecnc'),
    html.Br(),
    dcc.Link('PRES', href='/liveprd/livepres')
])



# Define the callbacks for routing
@app.callback(Output('page-content2', 'children'),
              Input('url', 'pathname'))
def display_page(pathname, liveprd=None):
    if pathname == '/liveprd/livecnc':
        return livecnc.layout
    elif pathname == '/liveprd/livepres':
        return livepres.layout
    else:
        return 404