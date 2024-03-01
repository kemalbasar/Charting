from datetime import datetime, timedelta
import math
import dash
import tkinter as tk
import numpy as np
from tkinter import ttk
from dash import html
from dash_table.Format import Format, Scheme
from dash.dash_table import DataTable
import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc,Input, Output, State
from run.agent import ag
import plotly.express as px
from valfapp.app import app




df = ag.run_query(r"SELECT * FROM VLFPLATECAP")

print(df)

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

df_prepared = pivotting_table()

# Sonra, 'current_week' ve diğer tüm sütunlar için gruplandırma yaparak 'value_min' toplamını hesaplayın
df_grouped = df_prepared.groupby(['MATERIAL', 'COSTCENTER', 'WORKCENTER', 'SURE_HESAPLAMA_KODU', 'MACHINE', 'LABOUR', 'SETUP', 'BASEQUAN', 'current_week']).agg({'value_min':'sum'}).reset_index()

# Son olarak, pivot işlemini gerçekleştirin
pivot_result = df_grouped.pivot(index=['MATERIAL', 'COSTCENTER', 'WORKCENTER', 'SURE_HESAPLAMA_KODU', 'MACHINE', 'LABOUR', 'SETUP', 'BASEQUAN'], columns='current_week', values='value_min').reset_index()

sum_df_pivot_costcenter = pivot_result.groupby(['COSTCENTER'], as_index=False).sum()
print(pivot_result)



def create_weeks_dict():
    start_date = datetime.now() - timedelta(weeks=1)

    # Önümüzdeki 18 hafta için yıl ve hafta numarasını içeren bir sözlük oluştur, hafta numarası iki basamaklı olacak şekilde
    weeks_dict = {}
    for i in range(19):  # Bu hafta dahil olmak üzere toplamda 19 hafta
        week_start = start_date + timedelta(weeks=i)
        year, week_num, _ = week_start.isocalendar()
        weeks_dict[f"{year}-{str(week_num).zfill(2)}"] = f"{year}-{str(week_num).zfill(2)}"

    return weeks_dict

weeks_dict = create_weeks_dict()
weeks_dict_cap = [{"name": key, "id": key} for key in weeks_dict.keys()]
weeks_dict_cap.insert(0, {"name": "STAT", "id": "STAT"})

formatted_columns_capcostcenter = []
for column in weeks_dict_cap:
    if column["id"] == "STAT":
        formatted_columns_capcostcenter.append(column)
    else:
        formatted_columns_capcostcenter.append({
            **column,
            "type": "numeric",
            "format": Format(precision=1, scheme=Scheme.fixed)
        })

columns_costcenter = [{"name": key, "id": key} for key in weeks_dict.keys()]
columns_costcenter.insert(0, {"name": "COSTCENTER", "id": "COSTCENTER"})

formatted_columns = []
for column in columns_costcenter:
    if column["id"] == "COSTCENTER":  # COSTCENTER sütunu metinsel olabilir, formatlama uygulanmaz
        formatted_columns.append(column)
    else:
        formatted_columns.append({
            **column,
            "type": "numeric",
            "format": Format(precision=1, scheme=Scheme.fixed)
        })



columns_workcenter = [{"name": key, "id": key} for key in weeks_dict.keys()]
columns_workcenter.insert(0, {"name": "WORKCENTER", "id": "WORKCENTER"})

formatted_columns_workcenter = []
for column in columns_workcenter:
    if column["id"] == "WORKCENTER":
        formatted_columns_workcenter.append(column)
    else:
        formatted_columns_workcenter.append({
            **column,
            "type": "numeric",
            "format": Format(precision=1, scheme=Scheme.fixed)
        })

columns_material = [{"name": key, "id": key} for key in weeks_dict.keys()]
columns_material.insert(0, {"name": "MATERIAL", "id": "MATERIAL"})

formatted_columns_material = []
for column in columns_material:
    if column["id"] == "MATERIAL":
        formatted_columns_material.append(column)
    else:
        formatted_columns_material.append({
            **column,
            "type": "numeric",
            "format": Format(precision=1, scheme=Scheme.fixed)
        })



root = tk.Tk()
root.title("ComboBox Örneği")

layout = dbc.Container([
    dcc.Store(id='stored_data',data=pivotting_table().to_json(date_format='iso', orient='split')),
    dcc.Store(id='stored_data_pivot',data=pivot_result.to_json(date_format='iso', orient='split')),
    dbc.Row([
        dbc.Col([dcc.Dropdown(
            id='costcenter-dropdown',
            options=[{'label': i, 'value': i} for i in
                     ["CNC", "CNCTORNA", "FASON", "ISIL", "MONTAJ", "PAKET", "PLKYZYIS", "PRESHANE", "TASLAMA",
                      "YIKAMA"]],
            value='CNC'
        )
        ])

    ]),
    dbc.Row([
        dbc.Col([
          dcc.Graph(id='fig')
        ]),
        dbc.Col([
            DataTable(id=f"costcenter_table", data=sum_df_pivot_costcenter.to_dict('records'),
                     columns=formatted_columns
                            ,style_cell={
                                    'minWidth': 'auto',  # Hücrenin minimum genişliği
                                    'width': 'auto',  # Hücrenin genişliği
                                    'maxWidth': 'auto',  # Hücrenin maksimum genişliği
                                    'color': 'black',  # Font color for the cells
                                    'backgroundColor': 'white',  # Slightly transparent background
                                    #'minWidth': '80px', 'width': '80px', 'maxWidth': '100px',  # Cell width specifications
                                    'textAlign': 'left',  # Center text alignment
                                    'border': '1px solid black'  # Border for the cells
                            },
                                style_table = {
                                    'height': '450px',  # Fixed height for the virtualized table
                                    'width': '950px',  # Fixed width for the table
                                    'overflowY': 'auto',  # Enable vertical scroll
                                    'borderCollapse': 'collapse',  # Collapse borders
                                    'border': '1px solid black'  # Border around the table
                            },
                                style_header = {
                                    'fontWeight': 'bold',  # Make header text bold
                                    'backgroundColor': 'rgba(0, 0, 0, 0.1)',  # Slightly darker background for the header
                                    'borderBottom': '1px solid black',  # Bottom border for the header cells
                                    'color': 'black'  # Font color for the header
                            },
                                style_data_conditional = [
                                    {
                                        'if': {'column_id': column_id, 'filter_query': '{{{}}} = 0'.format(column_id)},
                                        'color': 'white'
                                    } for column_id in [col['id'] for col in formatted_columns]
                                # Here you can add any conditional styles you might have
                                # For example, styling for the active cell or conditional formatting based on cell values
                            ],
            )
        ])
    ]),

    dbc.Row([
        DataTable(id=f"capasity_table_costcenter", data=pivot_result.to_dict('records'),
                  columns=formatted_columns_capcostcenter
                  , style_cell={
                'minWidth': 'auto',  # Hücrenin minimum genişliği
                'width': 'auto',  # Hücrenin genişliği
                'maxWidth': 'auto',  # Hücrenin maksimum genişliği
                # 'whiteSpace': 'normal',  # Uzun metinlerin birden fazla satıra yayılmasını sağlar

                'color': 'black',  # Font color for the cells
                'backgroundColor': 'white',  # Slightly transparent background
                # 'minWidth': '80px', 'width': '80px', 'maxWidth': '100px',  # Cell width specifications
                'textAlign': 'left',  # Center text alignment
                'border': '1px solid black'  # Border for the cells
            },
                  style_table={
                      # 'overflowX': 'auto'
                      'height': '150px',  # Fixed height for the virtualized table
                      # 'width': '800px',  # Fixed width for the table
                      'overflowY': 'auto',  # Enable vertical scroll
                      'borderCollapse': 'collapse',  # Collapse borders
                      'border': '1px solid black'  # Border around the table
                  },
                  style_header={
                      'fontWeight': 'bold',  # Make header text bold
                      'backgroundColor': 'rgba(0, 0, 0, 0.1)',  # Slightly darker background for the header
                      'borderBottom': '1px solid black',  # Bottom border for the header cells
                      'color': 'black'  # Font color for the header
                  },
                  style_data_conditional=[
                      {
                          'if': {'column_id': column_id, 'filter_query': '{{{}}} = 0'.format(column_id)},
                          'color': 'white'
                      } for column_id in [col['id'] for col in formatted_columns_capcostcenter]
                      # Here you can add any conditional styles you might have
                      # For example, styling for the active cell or conditional formatting based on cell values
                  ],
                  )

    ]),

     dbc.Row([
        dbc.Col([dcc.Dropdown(
            id='workcenter-dropdown',
            options=[],
            value=None
             )
        ])

     ]),
     dbc.Row([
        dbc.Col([
           dcc.Graph(id='figx')
        ],style={'width': '600px'}),
         dbc.Col([
             DataTable(id=f"workcenter_table", data=pivot_result.to_dict('records'),
                  columns=formatted_columns_workcenter
                            ,style_cell={
                                    'minWidth': 'auto',  # Hücrenin minimum genişliği
                                    'width': 'auto',  # Hücrenin genişliği
                                    'maxWidth': 'auto',  # Hücrenin maksimum genişliği
                                    'color': 'black',  # Font color for the cells
                                    'backgroundColor': 'white',  # Slightly transparent background
                                    #'minWidth': '80px', 'width': '80px', 'maxWidth': '100px',  # Cell width specifications
                                    'textAlign': 'left',  # Center text alignment
                                    'border': '1px solid black'  # Border for the cells
                            },
                                style_table = {
                                    'height': '450px',  # Fixed height for the virtualized table
                                    'width': '950px',  # Fixed width for the table
                                    'overflowY': 'auto',  # Enable vertical scroll
                                    'borderCollapse': 'collapse',  # Collapse borders
                                    'border': '1px solid black'  # Border around the table
                            },
                                style_header = {
                                    'fontWeight': 'bold',  # Make header text bold
                                    'backgroundColor': 'rgba(0, 0, 0, 0.1)',  # Slightly darker background for the header
                                    'borderBottom': '1px solid black',  # Bottom border for the header cells
                                    'color': 'black'  # Font color for the header
                            },
                                style_data_conditional = [
                                    {
                                        'if': {'column_id': column_id, 'filter_query': '{{{}}} = 0'.format(column_id)},
                                        'color': 'white'
                                    } for column_id in [col['id'] for col in formatted_columns_workcenter]
                                # Here you can add any conditional styles you might have
                                # For example, styling for the active cell or conditional formatting based on cell values
                            ],
                  )
         ])
     ]),

dbc.Row([
        DataTable(id=f"capasity_table_workcenter", data=pivot_result.to_dict('records'),
                  columns=formatted_columns_capcostcenter
                  , style_cell={
                'minWidth': 'auto',  # Hücrenin minimum genişliği
                'width': 'auto',  # Hücrenin genişliği
                'maxWidth': 'auto',  # Hücrenin maksimum genişliği
                # 'whiteSpace': 'normal',  # Uzun metinlerin birden fazla satıra yayılmasını sağlar

                'color': 'black',  # Font color for the cells
                'backgroundColor': 'white',  # Slightly transparent background
                # 'minWidth': '80px', 'width': '80px', 'maxWidth': '100px',  # Cell width specifications
                'textAlign': 'left',  # Center text alignment
                'border': '1px solid black'  # Border for the cells
            },
                  style_table={
                      # 'overflowX': 'auto'
                      'height': '150px',  # Fixed height for the virtualized table
                      # 'width': '800px',  # Fixed width for the table
                      'overflowY': 'auto',  # Enable vertical scroll
                      'borderCollapse': 'collapse',  # Collapse borders
                      'border': '1px solid black'  # Border around the table
                  },
                  style_header={
                      'fontWeight': 'bold',  # Make header text bold
                      'backgroundColor': 'rgba(0, 0, 0, 0.1)',  # Slightly darker background for the header
                      'borderBottom': '1px solid black',  # Bottom border for the header cells
                      'color': 'black'  # Font color for the header
                  },
                  style_data_conditional=[
                      {
                          'if': {'column_id': column_id, 'filter_query': '{{{}}} = 0'.format(column_id)},
                          'color': 'white'
                      } for column_id in [col['id'] for col in formatted_columns_capcostcenter]
                      # Here you can add any conditional styles you might have
                      # For example, styling for the active cell or conditional formatting based on cell values
                  ],
                  )

    ]),

    dbc.Row([
        DataTable(id=f"material_table", data=pivot_result.to_dict('records'),
                  columns=formatted_columns_material
                            ,style_cell={
                                    'minWidth': 'auto',  # Hücrenin minimum genişliği
                                    'width': 'auto',  # Hücrenin genişliği
                                    'maxWidth': 'auto',  # Hücrenin maksimum genişliği
                                    #'whiteSpace': 'normal',  # Uzun metinlerin birden fazla satıra yayılmasını sağlar

                                    'color': 'black',  # Font color for the cells
                                    'backgroundColor': 'white',  # Slightly transparent background
                                    #'minWidth': '80px', 'width': '80px', 'maxWidth': '100px',  # Cell width specifications
                                    'textAlign': 'left',  # Center text alignment
                                    'border': '1px solid black'  # Border for the cells
                            },
                                style_table = {
                                   # 'overflowX': 'auto'
                                    'height': '800px',  # Fixed height for the virtualized table
                                    #'width': '800px',  # Fixed width for the table
                                    'overflowY': 'auto',  # Enable vertical scroll
                                    'borderCollapse': 'collapse',  # Collapse borders
                                    'border': '1px solid black'  # Border around the table
                            },
                                style_header = {
                                    'fontWeight': 'bold',  # Make header text bold
                                    'backgroundColor': 'rgba(0, 0, 0, 0.1)',  # Slightly darker background for the header
                                    'borderBottom': '1px solid black',  # Bottom border for the header cells
                                    'color': 'black'  # Font color for the header
                            },
                                style_data_conditional = [
                                   {
                                      'if': {'column_id': column_id, 'filter_query': '{{{}}} = 0'.format(column_id)},
                                           'color': 'white'
                                    } for column_id in [col['id'] for col in formatted_columns_material]
                                # Here you can add any conditional styles you might have
                                # For example, styling for the active cell or conditional formatting based on cell values
                            ],
        )
    ])
],fluid=True)


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

    [Output('capasity_table_costcenter', 'data'),Output('workcenter_table', 'data')],
     Input('costcenter-dropdown', 'value'),
     State('stored_data_pivot', 'data')
)
def update_costcenter_table(selected_costcenter,df_json_pivot):
    if df_json_pivot is None:
        return []
    df_pivot = pd.read_json(df_json_pivot, orient='split')
    filtered_df = df_pivot[df_pivot['COSTCENTER'] == selected_costcenter]
    sum_df = filtered_df.groupby(['COSTCENTER'], as_index=False).sum()

    sum_df_wc = filtered_df.groupby(['WORKCENTER'], as_index=False).sum()

    return sum_df.to_dict('records'),sum_df_wc.to_dict('records')
@app.callback(
    [Output('figx', 'figure'),Output('material_table', 'data'),
       Output('capasity_table_workcenter', 'data')],
     Input('workcenter-dropdown', 'value'),
     [State('stored_data', 'data'),State('stored_data_pivot', 'data')]
)
def update_graph(selected_workcenter,df_json,df_json_pivot):
    if df_json is None:
        return px.bar()
    if df_json is None:
        return [], None
    if df_json_pivot is None:
        return []
    df = pd.read_json(df_json, orient='split')
    df_pivot = pd.read_json(df_json_pivot, orient='split')
    filtered_df_pivot = df_pivot[df_pivot['WORKCENTER'] == selected_workcenter]
    sum_df_pivot = filtered_df_pivot.groupby(['WORKCENTER'], as_index=False).sum()

    filtered_df = df[df['WORKCENTER'] == selected_workcenter]
    sum_df = filtered_df.groupby(['WORKCENTER', 'current_week']).sum({'value_min'}).reset_index()
    figx = px.bar(sum_df, x='current_week', y='value_min')
    figx.update_xaxes(type='category')
    return figx,filtered_df_pivot.to_dict('records'),sum_df_pivot.to_dict('records')


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

