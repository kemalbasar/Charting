### Import Packages ###
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
### Import Dash Instance and Pages ###
from valfapp.app import app
from pages import value, prod_eff, workcenters,liveprd,dragtester
from valfapp.layouts import layout_12_loginpage_v2
from valfapp.pages import livecnc, livepres, energy, cnctotv, taslamatv, montajtv, yuzeyislemtv, kameraayıklama, \
    tvmonitor, uretimrapor, kapasite, prd_energy, cnc1tv, cnc2tv, camayikuretim, adr_CNC, adr_CNCTORNA, \
    adr_PRES1, adr_PRES2, adr_MONTAJ, gvt_page, adr_CNC_week, adr_PRES1_week, adr_PRES2_week, adr_CNCTORNA_week, \
    adr_MONTAJ_week, adr_CNC_month, adr_CNCTORNA_month, adr_MONTAJ_month, adr_PRES1_month, adr_PRES2_month, \
    adr_CNCreal, adr_CNCTORNAreal, \
    adr_PRES1real, adr_PRES2real, adr_MONTAJreal, adr_CNC_weekreal, adr_PRES1_weekreal, adr_PRES2_weekreal, adr_CNCTORNA_weekreal, \
    adr_MONTAJ_weekreal, adr_CNC_monthreal, adr_CNCTORNA_monthreal, adr_MONTAJ_monthreal, adr_PRES1_monthreal, adr_PRES2_monthreal,yonlendirme_pagee
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
    ], fluid=True)



### Login Page Layout ###

### Index Page Layout ###

index_layout = layout_12_loginpage_v2

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




#### Yeni bir sayfa açtığımız zaman buraya eklem
####yapıyoruz
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
    if pathname == '/':
        return index_layout
    elif pathname == '/liveprd':
        return liveprd.layout
    elif pathname == '/prodeff':
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
    elif pathname == '/energy':
        return energy.layout
    elif pathname == '/prdenergy':
        return prd_energy.layout
    elif pathname == '/cnctotv':
        return cnctotv.layout
    elif pathname == '/cnc1tv':
        return cnc1tv.layout
    elif pathname == '/cnc2tv':
        return cnc2tv.layout
    elif pathname == '/taslamatv':
        return taslamatv.layout
    elif pathname == '/montajtv':
        return montajtv.layout
    elif pathname == '/yislemtv':
        return yuzeyislemtv.layout
    elif pathname == '/tvmonitor':
        return tvmonitor.layout
    elif pathname == '/uretimrapor':
        return uretimrapor.layout
    elif pathname == '/kapasite':
        return kapasite.layout
    elif pathname == '/kameraayiklama':
        return kameraayıklama.layout
    elif pathname == '/gvt_page':
        return gvt_page.layout
    elif pathname == '/camayikuretim':
        return camayikuretim.layout
    elif pathname == '/yonlendirmepagee':
        return yonlendirme_pagee.layout
    elif pathname == '/adrcnc':
        return adr_CNC.layout
    elif pathname == '/adrcnctorna':
        return adr_CNCTORNA.layout
    elif pathname == '/adrpres1':
        return adr_PRES1.layout
    elif pathname == '/adrpres2':
        return adr_PRES2.layout
    elif pathname == '/adrmontaj':
        return adr_MONTAJ.layout
    elif pathname == '/adrcncweek':
        return adr_CNC_week.layout
    elif pathname == '/adrcnctornaweek':
        return adr_CNCTORNA_week.layout
    elif pathname == '/adrmontajweek':
        return adr_MONTAJ_week.layout
    elif pathname == '/adrpres1week':
        return adr_PRES1_week.layout
    elif pathname == '/adrpres2week':
        return adr_PRES2_week.layout
    elif pathname == '/adrcnctornamonth':
        return adr_CNCTORNA_month.layout
    elif pathname == '/adrmontajmonth':
        return adr_MONTAJ_month.layout
    elif pathname == '/adrpres1month':
        return adr_PRES1_month.layout
    elif pathname == '/adrpres2month':
        return adr_PRES2_month.layout
    elif pathname == '/adrcncmonth':
        return adr_CNC_month.layout
    
    elif pathname == '/adrcncreal':
        return adr_CNCreal.layout
    elif pathname == '/adrcnctornareal':
        return adr_CNCTORNAreal.layout
    elif pathname == '/adrpres1real':
        return adr_PRES1real.layout
    elif pathname == '/adrpres2real':
        return adr_PRES2real.layout
    elif pathname == '/adrmontajreal':
        return adr_MONTAJreal.layout
    elif pathname == '/adrcncweekreal':
        return adr_CNC_weekreal.layout
    elif pathname == '/adrcnctornaweekreal':
        return adr_CNCTORNA_weekreal.layout
    elif pathname == '/adrmontajweekreal':
        return adr_MONTAJ_weekreal.layout
    elif pathname == '/adrpres1weekreal':
        return adr_PRES1_weekreal.layout
    elif pathname == '/adrpres2weekreal':
        return adr_PRES2_weekreal.layout
    elif pathname == '/adrcnctornamonthreal':
        return adr_CNCTORNA_monthreal.layout
    elif pathname == '/adrmontajmonthreal':
        return adr_MONTAJ_monthreal.layout
    elif pathname == '/adrpres1monthreal':
        return adr_PRES1_monthreal.layout
    elif pathname == '/adrpres2monthreal':
        return adr_PRES2_monthreal.layout
    elif pathname == '/adrcncmonthreal':
        return adr_CNC_monthreal.layout
    else:
        print(f"adsadasd{pathname}")
        return '404'




### Set app layout to page container ###
app.layout = page_container
### Assemble all layouts ###
app.validation_layout = html.Div(
    children=(
        page_container,
        index_layout,
        liveprd.layout,
        prod_eff.layout,
        value.layout,
        workcenters.layout,
        livepres.layout,
        livecnc.layout,
        dragtester.layout,
        energy.layout,
        prd_energy.layout,
        cnctotv.layout,
        cnc1tv.layout,
        cnc2tv.layout,
        taslamatv.layout,
        montajtv.layout,
        yuzeyislemtv.layout,
        kameraayıklama.layout,
        camayikuretim.layout,
        tvmonitor.layout,
        uretimrapor.layout,
        kapasite.layout,
        gvt_page.layout,
        yonlendirme_pagee.layout,
        adr_CNC.layout,
        adr_CNCTORNA.layout,
        adr_PRES1.layout,
        adr_PRES2.layout,
        adr_MONTAJ.layout,
        adr_PRES1_week.layout,
        adr_PRES2_week.layout,
        adr_CNC_week.layout,
        adr_CNCTORNA_week.layout,
        adr_MONTAJ_week.layout,
        adr_CNC_month.layout,
        adr_CNCTORNA_month.layout,
        adr_MONTAJ_month.layout,
        adr_PRES1_month.layout,
        adr_PRES2_month.layout,
        
        adr_CNCreal.layout,
        adr_CNCTORNAreal.layout,
        adr_PRES1real.layout,
        adr_PRES2real.layout,
        adr_MONTAJreal.layout,
        adr_PRES1_weekreal.layout,
        adr_PRES2_weekreal.layout,
        adr_CNC_weekreal.layout,
        adr_CNCTORNA_weekreal.layout,
        adr_MONTAJ_weekreal.layout,
        adr_CNC_monthreal.layout,
        adr_CNCTORNA_monthreal.layout,
        adr_MONTAJ_monthreal.layout,
        adr_PRES1_monthreal.layout,
        adr_PRES2_monthreal.layout,

        # ittools.layout
    )
)


app.layout.interval = -1



#method takes input as dataframe and return buble graph


# refresh_store = dcc.Store(id='refresh-store', data=refresh_count)
