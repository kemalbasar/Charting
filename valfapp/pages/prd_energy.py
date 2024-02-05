# Import required libraries and modules
from datetime import datetime, date, timedelta
import dash_bootstrap_components as dbc
import dash_table
import pandas as pd
import plotly.express as px
from decimal import Decimal
import plotly.graph_objs as go
from _plotly_utils.colors.qualitative import Alphabet
from dash import dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate
from config import valftoreeg, project_directory
from run.agent import ag
from valfapp.app import app
from valfapp.configuration import layout_color
from valfapp.layouts import nav_bar


layout = [
    # Your commented-out buttons
    # dbc.Button("Day", id="btn-day_en", n_clicks=0, color="primary", className='day-button'),
    # dbc.Button("Week", id="btn-week1_en", n_clicks=0, color="primary", className='week-button'),
    # dbc.Button("Month", id="btn-month1_en", n_clicks=0, color="primary", className='month-button'),
    # dbc.Button("Year", id="btn-year1_en", n_clicks=0, color="primary", className='year-button'),

    # Store and Download components
    dcc.Store(id='generated_data2'), dcc.Download(id="download-energy2"), dcc.Download(id="download-energy3"),

    # Navigation Bar
    nav_bar,

    # Energy Search and Filter Components

    dbc.Row(
        [
            dbc.Col(
                html.Div(
                    [
                        dcc.Dropdown(
                            id='machine-type-dropdown2',
                            options=[
                                {'label': k, 'value': k}
                                for k in valftoreeg.keys()
                            ],
                            value=list(valftoreeg.keys())[0],
                            style={
                                'color': 'white',
                                'width': 220,
                            },
                        )], style={"margin-top": 18}), width=1),
            dbc.Col(
                html.Div(
                    [dcc.Dropdown(
                        id='machine-dropdown2',
                        style={
                            'color': 'white',
                            'width': 220,
                        },
                        value='Analizörler'
                    )], style={"margin-top": 18}), width=1),
            dbc.Col(
                html.Div(
                    [dcc.Dropdown(
                        id='date-dropdown2',
                        options=[
                            {'label': i, 'value': i}
                            for i in ['Day', 'Month']
                        ],
                        style={
                            'color': 'white',
                            'font': {'color': '#2149b4'},
                            'width': 220,
                        },
                        value='month',
                    ),
                    ],
                    style={"margin-top": 18},
                ),
                className="", width=1
            ),
            dbc.Col(
                html.Div(
                    [
                        dcc.DatePickerRange(
                            id='date-picker2',
                            className="dash-date-picker-multi",
                            start_date=(date.today() - timedelta(weeks=1)).isoformat(),
                            end_date=(date.today()).isoformat(),
                            display_format='YYYY-MM-DD',
                            style={'color': '#212121'},
                            persistence=True,
                            persistence_type='session',
                        ),
                        html.Button(
                            'Search',
                            id='search2',
                            className="dash-empty-button",
                            n_clicks=0,
                        ),
                        html.Button(
                            'Download',
                            id='download2',
                            className="dash-empty-button",
                            n_clicks=0,
                        ),
                        html.Button(
                            'DownloadF',
                            id='download3',
                            className="dash-empty-button",
                            n_clicks=0,
                        ),
                    ],
                ), style={"margin-left": 100, "margin-top": 15}
            ),
        ], style={"margin-top": 40, 'border': '3px dashed blue', "margin-left": 44}, className="g-0"
    ),
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dash_table.DataTable(
                    id="data_table2",
                    data=[],
                    columns=[],
                    filter_action='native',
                    style_cell={
                        "textAlign": "center",
                        "padding": "10px",
                        "color": "black",
                        'max-width': 100
                    },
                    style_table={
                        'borderCollapse': 'collapse',
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(248, 248, 248)'
                        }
                    ],
                    style_header={
                        'backgroundColor': 'rgb(230, 230, 230)',
                        'fontWeight': 'bold'
                    },
                    sort_action='native'
                ),

            ], style={"margin-top": 75}, className="")
        ], width=12, style={"margin-left": "100px"}),])
]


# Define the callback to update the second dropdown
@app.callback(
    Output('machine-dropdown2', 'options'),
    Input('machine-type-dropdown2', 'value')
)
def set_machine_options(selected_machine_type):
    if selected_machine_type in ["Bütün", "HAVALANDIRMA - FAN"]:
        return [{'label': v, 'value': k} for k, v in valftoreeg[selected_machine_type].items()]
    else:
        print("herehere")
        list_of_mpoints = [{'label': v, 'value': k} for k, v in valftoreeg[selected_machine_type].items()]
        list_of_mpoints.append({"label": "Hepsi", "value": "Hepsi"})
        print(list_of_mpoints)
        return list_of_mpoints




@app.callback(
    Output("data_table2", "data"),
    Output("data_table2", "columns"),
    [State('date-picker2', 'start_date'),
     State('date-picker2', 'end_date'),
     State('machine-type-dropdown2', 'value'),
     State('machine-dropdown2', 'value'),
     State('date-dropdown2', 'value'),
     Input('search2', 'n_clicks')]
)
def cache_to_result(s_date, f_date, costcenter, m_point, date_interval, button):
    if button <= 0:
        raise PreventUpdate
    df = ag.run_query(f"SELECT * FROM VLFPRDENERGYVİEW")
    df["TOTWEIGHT"] = df["TOTWEIGHT"].fillna(0)
    df["KWHPERTON"] = df.apply(lambda x: (x["TOTKWH"] / x["TOTWEIGHT"]) if x["TOTWEIGHT"] != 0 else 1.111, axis=1)
    df['KWHPERTON'] = df['KWHPERTON'].apply(lambda x: Decimal(x).quantize(Decimal('0.000')))

    pivot_table = df.pivot_table(index="MATERIAL", columns='COSTCENTER', values='KWHPERTON', aggfunc='first')
    pivot_table.reset_index(inplace=True)
    columns = [{"name": i, "id": i} for i in pivot_table.columns]
    print("********************************")
    return pivot_table.to_dict("records"), columns



@app.callback(
    Output("download-energy2", "data"),
    Input("download2", "n_clicks"),
    prevent_initial_call=True
)
def generate_excel(n_clicks,):
    print("here")
    generated_data = ag.run_query(r"SELECT * FROM VLFPRDENERGYUNSTRUCTERED")
    if n_clicks < 1:
        raise PreventUpdate

    return dcc.send_data_frame(generated_data.to_excel, "energydata.xlsx", index=False)\

@app.callback(
    Output("download-energy3", "data"),
    Input("download3", "n_clicks"),
)
def generate_excel2(n_clicks,):
    print("here")

    generated_data = ag.run_query(r"SELECT * FROM VLFPRDENERGYVİEW")
    if n_clicks < 1:
        raise PreventUpdate

    return dcc.send_data_frame(generated_data.to_excel, "energydata.xlsx", index=False)
