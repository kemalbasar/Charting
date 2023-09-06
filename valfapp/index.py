### Import Packages ###
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
### Import Dash Instance and Pages ###
from valfapp.app import app
from pages import value, prod_eff, workcenters,liveprd,dragtester
from valfapp.layouts import layout_27_loginpage, layout_12_loginpage
from valfapp.pages import livecnc, livepres
from flask import request,g

### Page container ###
# login_status_store = dcc.Store(id='login-status-store', data={'logged_in': False})

page_container = dbc.Container([ html.Div(
    children=[
        dcc.Location(id='url', refresh=False),
        dcc.Store(id='login-status-store', data={'logged_in': False}, storage_type='local'),
        dcc.Store(id='device-info-store'),
        html.Div(id='page-content') ]),
                           html.Div(id='touch-support-output', style={'display': 'none'})
    ])



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

index_layout = layout_12_loginpage

# Update the before_request method
@app.server.before_request
def before_request():
    user_agent = request.user_agent
    g.device_type = "Mobile" if user_agent.platform in ["android", "iphone", "ipad"] else "Desktop"
    touch_support = request.form.get('touch-support-output', 'no-touch')
    if touch_support == 'touch':
        g.device_type = "Mobile"  # or "Touch" to be more accurate
    else:
        g.device_type = "Desktop"

# Callback to update the device info store
@app.callback(
    Output('device-info-store', 'data'),
    Input('login-status-store', 'data')
)
def update_device_info(login_status):
    if login_status and login_status.get('logged_in'):
        device_type = getattr(g, 'device_type', 'Desktop') # Default to 'Desktop' if not set
        # print({'device_type': device_type})
        print(g)
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
        elif pathname == '/value':
            return value.layout
        elif pathname == '/wcreport':
            return workcenters.layout
        elif pathname == '/liveprd/livecnc':
            return livecnc.layout
        elif pathname == '/liveprd/livepres':
            return livepres.layout
        elif pathname == '/dragtester':
            return dragtester.layout
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
        value.layout,
        workcenters.layout,
        livepres.layout,
        livecnc.layout,
        dragtester.layout
        # ittools.layout
    ]
)

app.layout.interval = -1



#method takes input as dataframe and return buble graph


# refresh_store = dcc.Store(id='refresh-store', data=refresh_count)
