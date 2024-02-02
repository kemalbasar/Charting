from datetime import datetime, timedelta
import math
import dash
import tkinter as tk
from tkinter import ttk

import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc,Input, Output, State
from run.agent import ag
import plotly.express as px
from valfapp.app import app




df = ag.run_query(r"SELECT * FROM VLFPLATECAP")


def pivotting_table():
    today = datetime.today()
    one_week_ago = today - timedelta(days=7)
    year_ago, week_num_ago, week_day_ago = one_week_ago.isocalendar()
    formatted_date_one_week_ago = f"{year_ago}-{week_num_ago}"

    df_sade = df[formatted_weeks()]
    pivot_columns = df_sade.columns.difference(['MATERIAL','COSTCENTER','WORKCENTER','SURE_HESAPLAMA_KODU','MACHINE','LABOUR','SETUP','BASEQUAN'])

    # Pivot the data
    pivoted_df = df.melt(id_vars=['MATERIAL','COSTCENTER','WORKCENTER','SURE_HESAPLAMA_KODU','MACHINE','LABOUR','SETUP','BASEQUAN'], value_vars=pivot_columns, var_name='current_week', value_name='value')

    pivoted_df["BASEQUAN"] = pivoted_df["BASEQUAN"].astype(int)
    pivoted_df["MACHINE"] = pivoted_df["MACHINE"].astype(float)
    pivoted_df["LABOUR"] = pivoted_df["LABOUR"].astype(float)
    pivoted_df["SETUP"] = pivoted_df["SETUP"].astype(float)
    pivoted_df["value"] = pivoted_df["value"].astype(float)
    pivoted_df['value_min'] = pivoted_df.apply(lambda row: calculate_maxtime(row), axis=1)
    pivoted_df['current_week'] = pivoted_df['current_week'].apply(
        lambda x: formatted_date_one_week_ago if x == 'IHT0' else x[4:].replace('_', '-'))
    pivoted_df['current_week'] = pivoted_df['current_week'].apply(
        lambda x: '-'.join([x.split('-')[0], x.split('-')[1].zfill(2)]) if len(x.split('-')) > 1 else x)

    return pivoted_df


def formatted_weeks():
    # Current date
    current_date = datetime.now()

    # Calculate the start of the current week (assuming weeks start on Monday)
    current_week_start = current_date - timedelta(days=current_date.weekday())

    # Generate the current week and the next 17 weeks
    weeks = [current_week_start + timedelta(weeks=i) for i in range(18)]  # Generating the weeks

    # Formatting weeks as 'Year_WeekNumber' using ISO week date
    # Adjusting to remove leading zeros and ensuring no week "00"
    formatted_weeks = [f"{week.strftime('%G')}_{int(week.strftime('%V'))}" for week in weeks]

    # Removing the first week if it is week 00 and prefixing with "IHT_"
    formatted_weeks = ["IHT_" + week for week in formatted_weeks if not week.endswith("_0")]

    formatted_weeks.insert(0, 'IHT0')
    formatted_weeks.insert(0, 'MATERIAL')
    formatted_weeks.insert(0, 'COSTCENTER')
    formatted_weeks.insert(0, 'WORKCENTER')

    formatted_weeks.insert(0, 'SURE_HESAPLAMA_KODU')
    formatted_weeks.insert(0, 'MACHINE')
    formatted_weeks.insert(0, 'LABOUR')
    formatted_weeks.insert(0, 'SETUP')
    formatted_weeks.insert(0, 'BASEQUAN')

    return formatted_weeks

def calculate_maxtime(row):
    code = row['SURE_HESAPLAMA_KODU']
    machine = row['MACHINE']
    labour = row['LABOUR']
    setup = row['SETUP']
    total_need = row['value']
    base_quan = row['BASEQUAN']

    if total_need > 0:

        if code == 'A':
            return machine + labour + setup
        elif code == 'B':
            return (machine * total_need) + (labour * total_need) + setup
        elif code == 'C':
            return (machine * total_need) + labour + setup
        elif code == 'D':
            return machine + (labour * total_need) + setup
        elif code == 'E':
            return math.ceil(total_need / base_quan) * machine + labour + setup
        elif code == 'F':
            return machine + math.ceil(total_need / base_quan) * labour + setup
        elif code == 'G':
            return math.ceil(total_need / base_quan) * (machine + labour) + setup
        elif code == 'H':
            return math.ceil(total_need / base_quan) * machine + (labour * total_need) + setup
        elif code == 'I':
            return (machine * total_need) + (labour * (total_need / base_quan)) + setup
        elif code == 'J':
            return 0

    else:
        return 0

# Apply the function to each row in the DataFrame


root = tk.Tk()
root.title("ComboBox Örneği")

layout = dbc.Container([
    dcc.Store(id='stored_data',data=pivotting_table().to_json(date_format='iso', orient='split')),
    dbc.Row([
        dbc.Col([dcc.Dropdown(
            id='costcenter-dropdown',
            options=[{'label': i, 'value': i} for i in
                     ["CNC", "CNCTORNA", "FASON", "ISIL", "MONTAJ", "PAKET", "PLKYZYIS", "PRESHANE", "TASLAMA",
                      "YIKAMA"]],
            value='CNC'
        )
        ]),
        dbc.Col([dcc.Dropdown(
            id='workcenter-dropdown',
            options=[],
            value=None
        )
            ])
        ]),
    dbc.Row([
        dbc.Col([
dcc.Graph(id='fig')
    ]),
        dbc.Col([
dcc.Graph(id='figx')
    ])
        ])

])


@app.callback(
    Output('fig', 'figure'),
     Input('costcenter-dropdown', 'value'),
     State('stored_data', 'data')
)
def update_graph(selected_costcenter,df_json):
    if df_json is None:
        return px.bar()
    if df_json is None:
        return [], None
    df = pd.read_json(df_json, orient='split')
    costcenter_df = df[df['COSTCENTER'] == selected_costcenter]
    sum_b = costcenter_df.groupby(['COSTCENTER','current_week']).sum({'value_min'}).reset_index()
    fig = px.bar(sum_b, x='current_week', y='value_min')
    fig.update_xaxes(type='category')
    return fig

@app.callback(
    Output('figx', 'figure'),
     Input('workcenter-dropdown', 'value'),
     State('stored_data', 'data')
)
def update_graph(selected_workcenter,df_json):
    if df_json is None:
        return px.bar()
    if df_json is None:
        return [], None
    df = pd.read_json(df_json, orient='split')
    filtered_df = df[df['WORKCENTER'] == selected_workcenter]
    sum_df = filtered_df.groupby(['WORKCENTER', 'current_week']).sum({'value_min'}).reset_index()
    figx = px.bar(sum_df, x='current_week', y='value_min')
    figx.update_xaxes(type='category')
    return figx


@app.callback(
    [Output('workcenter-dropdown', 'options'),
     Output('workcenter-dropdown', 'value')],
    [Input('costcenter-dropdown', 'value'),
     State('stored_data', 'data')]
)
def workcenter_data_generate(selected_costcenter,df_json):

    if df_json is None:
        return [], None
    df = pd.read_json(df_json, orient='split')

#   [{'label': v, 'value': k} for k, v in valftoreeg[selected_machine_type].items()]
    filtered_df = df[df['COSTCENTER'] == selected_costcenter]
    unique_workcenters = filtered_df["WORKCENTER"].unique().tolist()
    sorted_workcenters = sorted(unique_workcenters)
    options_list = [{'label': wc, 'value': wc} for wc in sorted_workcenters]
    first_option = options_list[0] if options_list else None
    return options_list, first_option["value"]

