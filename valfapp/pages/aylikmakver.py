import numpy as np
import pandas as pd
from dash import dcc, html, Input, Output, State
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import time
from run.agent import agiot as ag
from valfapp.app import app
from datetime import date, timedelta, datetime
from config import kb, project_directory
from dash_table import DataTable
from valfapp.functions.functions_prd import indicator_for_tvs
import statistics
from dash.dependencies import Input, Output

length_camera= f'SELECT COUNT(DISTINCT MACHINE) as Lenght FROM VLFAYIKLAMAMONTHLY'
lengthc = ag.run_query(length_camera)
num_cameras = lengthc["Lenght"].iloc[0]
current_year = datetime.now().year
months = [{'label': datetime(current_year, i, 1).strftime('%B'), 'value': i}for i in range(1, 13)]


camera_layouts = []

for i in range(1, num_cameras + 1):
    camera_layout = (
        dbc.Col([
            dbc.Row([
                html.Div(
                    children=[
                        html.H4(f"Kamera - 0{i}", style={'text-align': 'center',
                                                         'background-color': 'white',
                                                         'color': 'black', 'font-weight': 'bold',
                                                         'width': '100%'}),
                        html.Table(
                            style={'width': '100%', 'border-collapse': 'collapse', 'color': 'black',
                                   'background-color': 'white'},
                            children=[
                                html.Tr(id=f'controlled-row-{i}', children=[
                                    html.Td("Malzeme Sayısı",
                                            style={'border': '1px solid black', 'color': 'black', 'font-weight': 'bold'}),
                                    html.Td(id=f'matnum-{i}',
                                            style={'border': '1px solid black', 'font-weight': 'bold', 'color': 'black'})
                                ]),
                                html.Tr(id=f'total-quantity-row-{i}', children=[
                                    html.Td("Toplam Miktar",
                                            style={'border': '1px solid black', 'color': 'black', 'font-weight': 'bold'}),
                                    html.Td(id=f'totalquan-{i}',
                                            style={'border': '1px solid black', 'font-weight': 'bold', 'color': 'black'})
                                ]),
                                html.Tr(id=f'total-ok-row-{i}', children=[
                                    html.Td("Toplam OK",
                                            style={'border': '1px solid black', 'color': 'black', 'font-weight': 'bold'}),
                                    html.Td(id=f'ok-{i}',
                                            style={'border': '1px solid black', 'font-weight': 'bold', 'color': 'black'})
                                ]),
                                html.Tr(id=f'total-notok-row-{i}', children=[
                                    html.Td("Toplam NOTOK",
                                            style={'border': '1px solid black', 'color': 'black', 'font-weight': 'bold'}),
                                    html.Td(id=f'notok-{i}',
                                            style={'border': '1px solid black', 'font-weight': 'bold', 'color': 'black'})
                                ]),


                                html.Tr(id=f'notok-gorsel-row-{i}', children=[
                                    html.Td("NOTOK GORSEL",
                                            style={'border': '1px solid black', 'color': 'black', 'font-weight': 'bold',
                                                   'padding-left': '20px'}),
                                    html.Td(id=f'notok-gorsel-{i}',
                                            style={'border': '1px solid black', 'color': 'black', 'font-weight': 'bold'})
                                ]),
                                html.Tr(id=f'notok-olcusel-row-{i}', children=[
                                    html.Td("NOTOK OLCUSEL",
                                            style={'border': '1px solid black', 'color': 'black', 'font-weight': 'bold',
                                                   'padding-left': '20px'}),
                                    html.Td(id=f'notok-olcusel-{i}',
                                            style={'border': '1px solid black', 'color': 'black', 'font-weight': 'bold' })
                                ]),



                                html.Tr(id=f'controlled-persecond-row-{i}', children=[
                                    html.Td("Saniye Denetlenen Miktar",
                                            style={'border': '1px solid black', 'color': 'black', 'font-weight': 'bold'}),
                                    html.Td(id=f'saniyede_denetlenen-{i}',
                                            style={'border': '1px solid black', 'font-weight': 'bold', 'color': 'black'})
                                ]),
                                dcc.Interval(
                                    id=f'interval-component-{i}',
                                    interval=10000,
                                    n_intervals=0
                                )
                            ]
                        )
                    ], style={'background-color': 'white', 'width': '100%'}
                )
            ], style={'margin': '0px'}),
            dbc.Row([
                dbc.Col([
                    html.Div(
                        dcc.Graph(id=f'line-graph1-{i}', style={'height': '300px', 'width': '100%', 'padding-top': '30px',
                                                                'background-color': 'white'})
                    )
                ], style={'margin-left': '0px'})
            ]),
            dbc.Row([
                dbc.Col([
                    html.Div(
                        dcc.Graph(id=f'line-graph2-{i}',
                                  style={'height': '300px', 'width': '100%', 'background-color': 'white'})
                    )
                ], style={'margin-left': '0px'})
            ])
        ], width=4)
    )
    camera_layouts.append(camera_layout)

today = datetime.now()
last_month = today - relativedelta(months=1)
selectedmonth=last_month
print(selectedmonth.month)
print('jjjjjjjjjjjj')

rows = []
for i in range(0, len(camera_layouts), 3):
    row = dbc.Row(camera_layouts[i:i + 3], style={'margin-bottom': '15px'})
    rows.append(row)

layout = [
    dbc.Row([html.H1('Aylık Makine Verileri', style={'text-align': 'center', "fontFamily": 'Arial Black',
                                                     'backgroundColor': 'rgba(33, 73, 180, 1)', 'color': 'white','padding-bottom':'5px'})]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='month-dropdown',
                options=months,
                value=last_month.month,
                style={'margin-bottom':'15px'},
                className='mounth-dropdown-container'),
        ], width=3)
    ]),
    dcc.Store(id='selected-month-store'),
    *rows
]


@app.callback(
    Output('selected-month-store', 'data'),
    Input('month-dropdown', 'value')
)
def store_selected_month(selected_month):
    return selected_month


for i in range(1, num_cameras + 1):
    @app.callback(
        [Output(f'matnum-{i}', 'children'),
         Output(f'totalquan-{i}', 'children'),
         Output(f'ok-{i}', 'children'),
         Output(f'notok-{i}', 'children'),
         Output(f'notok-gorsel-{i}', 'children'),
         Output(f'notok-olcusel-{i}', 'children'),
         Output(f'saniyede_denetlenen-{i}', 'children')],
        [Input(f'interval-component-{i}', 'n_intervals'),
         Input('selected-month-store', 'data')]  # Use the selected month from the store
    )
    def update_table(n, selected_month, i=i):
        query_path = (project_directory + r"\Charting\queries\vlf_ayıklamakmr_monthlydata.sql")
        text_to_find = ["XYZ", "{month1}"]
        text_to_put = [f"KMR-0{i}", f"{selected_month}"]
        df = ag.editandrun_query(query_path, text_to_find, text_to_put)

        if df.empty:
            return "N/A", "N/A", "N/A", "N/A", "N/A"

        print(df)
        print('qqqqqqqqqqqq')
        matnum = df['MATNUM'].iloc[0]
        totalquan = df['TOTALQUAN'].iloc[0]
        ok = df['OK'].iloc[0]
        notok = df['NOTOK'].iloc[0]
        notokgolsel=df['NOTOKGORSEL'].iloc[0]
        notokolcusel = df['NOTOKOLCUSEL'].iloc[0]
        saniyede_denetlenen = df['SANIYE_DENETLENEN'].iloc[0]


        return matnum, totalquan, ok, notok,notokgolsel,notokolcusel, saniyede_denetlenen



    @app.callback(
        Output(f'line-graph1-{i}', 'figure'),
        [Input(f'interval-component-{i}', 'n_intervals')]
    )
    def update_graph1(n, i=i):
        kmr = f"KMR-0{i}"
        query = f'SELECT MONTH, SANIYE_DENETLENEN FROM VLFAYIKLAMAMONTHLY WHERE MACHINE = \'{kmr}\''
        df1 = ag.run_query(query)
        lengtquery =  f'SELECT COUNT(MONTH) as Lenght  FROM VLFAYIKLAMAMONTHLY WHERE MACHINE = \'{kmr}\''
        length = ag.run_query(lengtquery)
        print(df1)
        print('yyyyyy')
        snydenet = []
        month = []
        monthdef = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        if df1.empty:
            return go.Figure()

        length = length['Lenght'].iloc[0]

        for j in range(length):
            snydenet.append(df1['SANIYE_DENETLENEN'].iloc[j])
            monthloc = df1['MONTH'].iloc[j]
            month.append(monthdef[monthloc - 1])
        y_values = snydenet
        x_values = month

        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            mode='lines+markers',
            name='Veri'))

        fig1.update_layout(
            title=f'Denetlenen Miktar',
            xaxis_title='',
            yaxis_title='',
            autosize=True,
            margin=dict(l=10, r=0, t=30, b=20),
            xaxis=dict(domain=[0, 1]),
            yaxis=dict(domain=[0, 1])
        )
        return fig1

    @app.callback(
        Output(f'line-graph2-{i}', 'figure'),
        [Input(f'interval-component-{i}', 'n_intervals')]
    )
    def update_graph2(n, i=i):
        kmr=f"KMR-0{i}"
        query = f'SELECT MONTH, TOTALQUAN FROM VLFAYIKLAMAMONTHLY WHERE MACHINE = \'{kmr}\''
        df1 = ag.run_query(query)
        lengtquery =  f'SELECT COUNT(MONTH) as Lenght  FROM VLFAYIKLAMAMONTHLY WHERE MACHINE = \'{kmr}\''
        length = ag.run_query(lengtquery)
        print(df1)
        print('yyyyyy')

        mktr = []
        month = []
        monthdef = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        if df1.empty:
            return go.Figure()

        length = length['Lenght'].iloc[0]

        for j in range(length):
            mktr.append(df1['TOTALQUAN'].iloc[j])
            monthloc = df1['MONTH'].iloc[j]
            month.append(monthdef[monthloc - 1])

        y_values = mktr
        x_values = month

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            mode='lines+markers',
            name='Veri'))

        fig2.update_layout(
            title=f'Toplam Miktar',
            xaxis_title='',
            yaxis_title='',
            autosize=True,
            margin=dict(l=10, r=0, t=30, b=20),
            xaxis=dict(domain=[0, 1]),
            yaxis=dict(domain=[0, 1])
        )
        return fig2


@app.callback(
    Output('output-div', 'children'),
    Input('month-dropdown', 'value')
)
def update_output(selected_month):
    if selected_month:
        selected_month_name = datetime(current_year, selected_month, 1).strftime('%B')
        return f"Seçilen Ay: {selected_month_name}"
    return "Henüz bir ay seçilmedi."