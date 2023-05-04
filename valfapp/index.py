### Import Packages ###
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
### Import Dash Instance and Pages ###
from valfapp.app import app
from pages import pg1, prod_eff, workcenters,liveprd
from valfapp.pages import livecnc, livepres

### Page container ###

page_container = html.Div(
    children=[
        dcc.Interval(id='interval', interval=500 * 1000,
                     n_intervals=0),
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
    # dcc.Interval(
    #     id='interval-component',
    #     interval=1000000, # 5000 milliseconds = 5 seconds
    #     n_intervals=0
    # ),
    dbc.Row([html.H1("Valfsan Analytics",
                     style={"text-align": "center", 'color': 'LightSteelBlue', 'font-weight': 'bold',
                            'padding': 50,
                            "width": 1000, "height": 100})],
            className="justify-content-center"),
    dbc.Row([
        dbc.Col(
            dcc.Link(
                children=[
                    html.Div([
                        html.Img(src='/assets/tutarlama.link.png', style={"width": "700px", "height": "480px", "object-fit": "fit"}),
                        html.H1("Tutarlama ( Geliştirme Aşamasında )", style={
                            "position": "absolute",
                            "bottom": 8,
                            "right": 8,
                            'color': 'white',
                            'font-weight': 'bold',
                        })
                    ], style={"position": "relative", "display": "inline-block"})
                ],
                href='/pg1',
            ),
            width=5,  # Adjust the width of the column, you can use values from 1 to 12
            style={"padding": 15}
        ),
        dbc.Col(
            dcc.Link(
                children=[
                    html.Div([
                        html.Img(src='/assets/report.link.png', style={"width": "700px", "height": "480px", "object-fit": "fit"}),
                        html.H1("M.Merkezi OEE Raporu", style={
                            "position": "absolute",
                            "bottom": 8,
                            "right": 8,
                            'color': 'white',
                            'font-weight': 'bold',
                        })
                    ], style={"position": "relative", "display": "inline-block"})
                ],
                href='/prod_eff',
            ),
            width=5,  # Adjust the width of the column, you can use values from 1 to 12
            style={"padding": 15}

        ),
    ],style={'margin-left': 220,'margin-top': 40,'margin-bottom': '-45px'}),
    dbc.Row([
        dbc.Col(
            dcc.Link(
                children=[
                    html.Div([
                        html.Img(src='/assets/wc.link.png', style={"width": "700px", "height": "480px", "object-fit": "fit"}),
                        html.H1("İş Merkezi Raporu", style={
                            "position": "absolute",
                            "bottom": 0,
                            "right": 10,
                            'color': 'white',
                            'font-weight': 'bold',
                        })
                    ], style={"position": "relative", "display": "inline-block"})
                ],
                href='/wcreport',
            ),
            width=5,  # Adjust the width of the column, you can use values from 1 to 12
            style={"padding": 15}
        ),
        dbc.Col(
            dcc.Link(
                children=[
                    html.Div([
                        html.Img(src='/assets/live.link.png', style={"width": "700px", "height": "480px", "object-fit": "fit"}),
                        html.H1("Üretim Canlı Takip", style={
                            "position": "absolute",
                            "bottom": 0,
                            "right": 8,
                            'color': 'white',
                            'font-weight': 'bold',
                        })
                    ], style={"position": "absolute", "display": "inline-block"})
                ],
                href='/liveprd',
            )
            ,
            width=5,  # Adjust the width of the column, you can use values from 1 to 12
            style={"padding": 15}
        ),
    ],style={'margin-left': 220}),
        dcc.Link(
                children='ittools',
                href='/ittools',
            )
], fluid=True)


### Update Page Container ###
@app.callback(
    Output(
        component_id='page-content',
        component_property='children',
    ),
    [Input(
        component_id='url',
        component_property='pathname',
    ),
     Input('interval', 'n_intervals')
    ]
)
def display_page(pathname,n):

    # print(n)
    if pathname == '/':
        return index_layout
    elif pathname == '/liveprd':
        return liveprd.layout
    elif pathname == '/prod_eff':
        return prod_eff.layout
    elif pathname == '/pg1':
        return pg1.layout
    elif pathname == '/wcreport':
        return workcenters.layout
    elif pathname == '/liveprd/livecnc':
        return livecnc.layout
    elif pathname == '/liveprd/livepres':
        return livepres.layout
    # elif pathname == '/ittools':
    #     return ittools.layout
    else:
        return '404'


### Set app layout to page container ###
app.layout = page_container
### Assemble all layouts ###
app.validation_layout = html.Div(
    children=[
        page_container,
        index_layout,
        liveprd.layout,
        prod_eff.layout,
        pg1.layout,
        workcenters.layout,
        livepres.layout,
        livecnc.layout,
        # ittools.layout
    ]
)

app.layout.interval = -1



#method takes input as dataframe and return buble graph


# refresh_store = dcc.Store(id='refresh-store', data=refresh_count)
