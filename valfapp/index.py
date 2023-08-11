### Import Packages ###
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
### Import Dash Instance and Pages ###
from valfapp.app import app
from pages import pg1, prod_eff, workcenters,liveprd
from valfapp.pages import livecnc, livepres
from flask import request,g

### Page container ###
# login_status_store = dcc.Store(id='login-status-store', data={'logged_in': False})

page_container = html.Div(
    children=[
        dcc.Location(id='url', refresh=False),
        dcc.Store(id='login-status-store', data={'logged_in': False}, storage_type='local'),
        dcc.Store(id='device-info-store'), # Store without initial data
        html.Div(id='page-content')
    ]
)




### Login Page Layout ###
login_layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Form([
                dbc.Label("Username:"),
                dbc.Input(type="text", id="username", placeholder="Enter username"),
            ]),
            dbc.Form([
                dbc.Label("Password:"),
                dbc.Input(type="password", id="password", placeholder="Enter password"),
            ]),
            dbc.Button("Login", id="login-button", color="primary"),
        ], width={"size": 6, "offset": 3}),
    ], className="justify-content-center"),
], fluid=True)



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
                        html.Img(src='/assets/tutarlama.link.png', style={"width": "600px", "height": "400px", "object-fit": "fit"}),
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
            width=4,  # Adjust the width of the column, you can use values from 1 to 12
            style={"padding": 14,'margin-left':50}
        ),
        dbc.Col(
            dcc.Link(
                children=[
                    html.Div([
                        html.Img(src='/assets/report.link.png', style={"width": "600px", "height": "400px", "object-fit": "fit"}),
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
            style={"padding-top": 13,'margin-left':43}

        ),
    ],style={'margin-left': 270,'margin-top': 37,'margin-bottom': '-45px'}),
    dbc.Row([
        dbc.Col(
            dcc.Link(
                children=[
                    html.Div([
                        html.Img(src='/assets/wc.link.png', style={"width": "600px", "height": "400px", "object-fit": "fit"}),
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
            width=4,  # Adjust the width of the column, you can use values from 1 to 12
            style={"padding-top": 30}
        ),
        dbc.Col(
            dcc.Link(
                children=[
                    html.Div([
                        html.Img(src='/assets/live.link.png', style={"width": "600px", "height": "400px", "object-fit": "fit"}),
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
            style={"padding": 28,'margin-left':42,'margin-top':2}
        ),
    ],style={'margin-left': 322}),
        dcc.Link(
                children='ittools',
                href='/ittools',
            )
], fluid=True)

# Update the before_request method
@app.server.before_request
def before_request():
    user_agent = request.user_agent
    g.device_type = "Mobile" if user_agent.platform in ["android", "iphone", "ipad"] else "Desktop"

# Callback to update the device info store
@app.callback(
    Output('device-info-store', 'data'),
    Input('login-status-store', 'data')
)
def update_device_info(login_status):
    if login_status and login_status.get('logged_in'):
        device_type = getattr(g, 'device_type', 'Desktop') # Default to 'Desktop' if not set
        print({'device_type': device_type})
        return {'device_type': device_type}

@app.callback(
    Output('some-output', 'children'),
    Input('device-info-store', 'data')
)
def customize_layout(device_info):
    device_type = device_info.get('device_type', 'Desktop') if device_info else 'Desktop'
    # Use the device_type to customize your layout

@app.callback(
    Output("login-status-store", "data"),
    Input("login-button", "n_clicks"),
    State("username", "value"),
    State("password", "value"),
    prevent_initial_call=True
)
def login(n_clicks, username, password):
    # Here you can add your logic to check username and password
    # For now, let's just allow any credentials
    if username and password:
        return {'logged_in': True}
    return {'logged_in': False}

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
    Input('login-status-store', 'data')
    ]
)
def display_page(pathname,login_status_data):
    if login_status_data and login_status_data['logged_in']:
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
    else:
        return login_layout




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
