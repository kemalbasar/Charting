from dash import dcc, html, Input, Output, State
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import time
from run.agent import agiot as ag
from valfapp.app import app
from config import kb, project_directory
from dash.dependencies import Input, Output

num_cameras = 6
current_year = datetime.now().year
months = [{'label': datetime(current_year, i, 1).strftime('%B'), 'value': i} for i in range(1, 13)]
years = [{'label': str(year), 'value': year} for year in range(current_year - 1, current_year + 1)]

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
                                            style={'border': '1px solid black', 'color': 'black', 'font-weight': 'bold'})
                                ]),
                                html.Tr(id=f'controlled-persecond-row-{i}', children=[
                                    html.Td("Saniye Denetlenen Miktar",
                                            style={'border': '1px solid black', 'color': 'black', 'font-weight': 'bold'}),
                                    html.Td(id=f'saniyede_denetlenen-{i}',
                                            style={'border': '1px solid black', 'font-weight': 'bold', 'color': 'black'})
                                ]),
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
selected_month = last_month.month

rows = []
for i in range(0, len(camera_layouts), 3):
    row = dbc.Row(camera_layouts[i:i + 3], style={'margin-bottom': '15px'})
    rows.append(row)

layout = [
    dbc.Row([html.H1('Aylık Makine Verileri', style={'text-align': 'center', "fontFamily": 'Arial Black',
                                                     'backgroundColor': 'rgba(33, 73, 180, 1)', 'color': 'white', 'padding-bottom': '5px'})]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='month-dropdown',
                options=months,
                value=last_month.month,
                style={'margin-bottom': '15px'},
                className='month-dropdown-container'),
        ], width=3),
        dbc.Col([
            dcc.Dropdown(
                id='year-dropdown',
                options=years,
                value=current_year,
                style={'margin-bottom': '15px'},
                className='year-dropdown-container'),
        ], width=1),
    ]),
    dcc.Store(id='selected-month-store'),
    dcc.Store(id='selected-year-store'),
    *rows
]

@app.callback(
    Output('selected-month-store', 'data'),
    Input('month-dropdown', 'value')
)
def store_selected_month(selected_month):
    return selected_month


@app.callback(
    Output('selected-year-store', 'data'),
    Input('year-dropdown', 'value')
)
def store_selected_year(selected_year):
    return selected_year


def generate_table_callback(camera_index):
    def update_table(selected_month, selected_year):
        query_path = project_directory + r"\Charting\queries\vlf_ayıklamakmr_monthlydata.sql"
        text_to_find = ["XYZ", "{month1}", "{year1}"]
        text_to_put = [f"KMR-0{camera_index}", f"{selected_month}", f"{selected_year}"]
        df = ag.editandrun_query(query_path, text_to_find, text_to_put)

        if df.empty:
            return "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"

        matnum = df['MATNUM'].iloc[0]
        totalquan = df['TOTALQUAN'].iloc[0]
        ok = df['OK'].iloc[0]
        notok = df['NOTOK'].iloc[0]
        notokgolsel = df['NOTOKGORSEL'].iloc[0]
        notokolcusel = df['NOTOKOLCUSEL'].iloc[0]
        saniyede_denetlenen = df['SANIYE_DENETLENEN'].iloc[0]

        return matnum, totalquan, ok, notok, notokgolsel, notokolcusel, saniyede_denetlenen

    return update_table


def generate_graph1_callback(camera_index):
    def update_graph1(selected_month, selected_year):
        kmr = f"KMR-0{camera_index}"
        query = f'SELECT MONTH, SANIYE_DENETLENEN FROM VLFAYIKLAMAMONTHLY WHERE MACHINE = \'{kmr}\' AND YEAR = {selected_year}'
        df1 = ag.run_query(query)
        lengtquery = f'SELECT COUNT(MONTH) as Lenght FROM VLFAYIKLAMAMONTHLY WHERE MACHINE = \'{kmr}\' AND YEAR = {selected_year}'
        length = ag.run_query(lengtquery)

        if df1.empty:
            return go.Figure()

        snydenet = []
        month = []
        monthdef = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        length = length['Lenght'].iloc[0]

        for j in range(length):
            snydenet.append(df1['SANIYE_DENETLENEN'].iloc[j])
            monthloc = df1['MONTH'].iloc[j]
            month.append(monthdef[monthloc - 1])

        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=month,
            y=snydenet,
            mode='lines+markers',
            name='Veri'))

        fig1.update_layout(
            title='Denetlenen Miktar',
            xaxis_title='',
            yaxis_title='',
            autosize=True,
            margin=dict(l=10, r=0, t=30, b=20),
            xaxis=dict(domain=[0, 1]),
            yaxis=dict(domain=[0, 1])
        )
        return fig1

    return update_graph1


def generate_graph2_callback(camera_index):
    def update_graph2(selected_month, selected_year):
        kmr = f"KMR-0{camera_index}"
        query = f'SELECT MONTH, TOTALQUAN FROM VLFAYIKLAMAMONTHLY WHERE MACHINE = \'{kmr}\' AND YEAR = {selected_year}'
        df1 = ag.run_query(query)
        lengtquery = f'SELECT COUNT(MONTH) as Lenght FROM VLFAYIKLAMAMONTHLY WHERE MACHINE = \'{kmr}\' AND YEAR = {selected_year}'
        length = ag.run_query(lengtquery)

        if df1.empty:
            return go.Figure()

        mktr = []
        month = []
        monthdef = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        length = length['Lenght'].iloc[0]

        for j in range(length):
            mktr.append(df1['TOTALQUAN'].iloc[j])
            monthloc = df1['MONTH'].iloc[j]
            month.append(monthdef[monthloc - 1])

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=month,
            y=mktr,
            mode='lines+markers',
            name='Veri'))

        fig2.update_layout(
            title='Toplam Miktar',
            xaxis_title='',
            yaxis_title='',
            autosize=True,
            margin=dict(l=10, r=0, t=30, b=20),
            xaxis=dict(domain=[0, 1]),
            yaxis=dict(domain=[0, 1])
        )
        return fig2

    return update_graph2


for i in range(1, num_cameras + 1):
    app.callback(
        [Output(f'matnum-{i}', 'children'),
         Output(f'totalquan-{i}', 'children'),
         Output(f'ok-{i}', 'children'),
         Output(f'notok-{i}', 'children'),
         Output(f'notok-gorsel-{i}', 'children'),
         Output(f'notok-olcusel-{i}', 'children'),
         Output(f'saniyede_denetlenen-{i}', 'children')],
        [Input('selected-month-store', 'data'),
         Input('selected-year-store', 'data')]
    )(generate_table_callback(i))

    app.callback(
        Output(f'line-graph1-{i}', 'figure'),
        [Input('selected-month-store', 'data'),
         Input('selected-year-store', 'data')]
    )(generate_graph1_callback(i))

    app.callback(
        Output(f'line-graph2-{i}', 'figure'),
        [Input('selected-month-store', 'data'),
         Input('selected-year-store', 'data')]
    )(generate_graph2_callback(i))


@app.callback(
    Output('output-div', 'children'),
    [Input('month-dropdown', 'value'),
     Input('year-dropdown', 'value')]
)
def update_output(selected_month, selected_year):
    if selected_month and selected_year:
        selected_month_name = datetime(current_year, selected_month, 1).strftime('%B')
        return f"Seçilen Ay ve Yıl: {selected_month_name} {selected_year}"
    return "Henüz bir ay ve yıl seçilmedi."
