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


def create_weeks_dict():
    start_date = datetime.now() - timedelta(weeks=1)

    # Önümüzdeki 18 hafta için yıl ve hafta numarasını içeren bir sözlük oluştur, hafta numarası iki basamaklı olacak şekilde
    weeks_dict = {}
    for i in range(19):  # Bu hafta dahil olmak üzere toplamda 19 hafta
        week_start = start_date + timedelta(weeks=i)
        year, week_num, _ = week_start.isocalendar()
        weeks_dict[f"{year}-{str(week_num).zfill(2)}"] = f"{year}-{str(week_num).zfill(2)}"

    return weeks_dict



layout = dbc.Container([
    dcc.Store(id='stored_data',data= pd.DataFrame().to_json(date_format='iso', orient='split')),
    dcc.Store(id='stored_data_pivot',data=pd.DataFrame().to_json(date_format='iso', orient='split')),
    dbc.Row([ dbc.Col(html.Div(dcc.Dropdown(
            id='section-dropdown',
            options=[{'label': i, 'value': i} for i in
                     ["Hepsi", "Plaka", "Checkvalf", "Pres"]],
            value='Hepsi'
          )
      ), width={"size": 3, "offset": 5})
    ]),

    dbc.Row([
        dbc.Col(html.Div([dcc.Dropdown(
            id='costcenter-dropdown',
            options=[],
            value=None
          )
        ]), width={"size": 3, "offset": 0}),
        dbc.Col(html.Div([
            html.Button('Costcenter Tablosunu İndir', id='btn-download-costcenter'),
            dcc.Download(id='download-costcenter')
         ]), style={'textAlign': 'right'}
        ),


    ]),

    dbc.Row([
        dbc.Col([
          dcc.Graph(id='fig')
        ]),
        dbc.Col([
            DataTable(id=f"costcenter_table",
	                            style_cell={
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
                            }
            )
        ])
    ]),

    dbc.Row([
        dbc.Col(html.Div([
            html.Button('Costcenter Kapasite Tablosunu İndir', id='btn-download-costcenter_kapasite'),
            dcc.Download(id='download-costcenter_kapasite')
        ]), width={"size": 3, "offset": 0}),  # Bu, butonu sağa hizalar
    ]),

    dbc.Row([
        DataTable(id=f"capasity_table_costcenter",
                columns=[{
                    'id': 'doluluk_orani',  # Bu, doluluk oranınızın sütun adıdır
                    'name': 'Doluluk Oranı',
                    'type': 'numeric',
                    'format': Format(precision=2, scheme=Scheme.percentage)  # Yüzde olarak formatlama
                }],
                style_cell={
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
                      'height': 'auto',  # Fixed height for the virtualized table
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
                }
        )

    ]),

    dbc.Row([
        dbc.Col(html.Div([dcc.Dropdown(
            id='workcenter-dropdown',
            options=[],
            value=None
        )
        ]), width={"size": 3, "offset": 0}),
        dbc.Col(html.Div([
            html.Button('Workcenter Tablosunu İndir', id='btn-download-workcenter'),
            dcc.Download(id='download-workcenter')
        ]), style={'textAlign': 'right'}
        ),

    ]),
     dbc.Row([
        dbc.Col([
           dcc.Graph(id='figx')
        ],style={'width': '600px'}),
         dbc.Col([
             DataTable(id=f"workcenter_table",
                                style_cell={
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
                            }
                  )
         ])
     ]),

    dbc.Row([
        dbc.Col(html.Div([
            html.Button('Workcenter Kapasite Tablosunu İndir', id='btn-download-workcenter_kapasite'),
            dcc.Download(id='download-workcenter_kapasite')
        ]), width={"size": 3, "offset": 0}),  # Bu, butonu sağa hizalar
    ]),

dbc.Row([
        DataTable(id=f"capasity_table_workcenter",
                style_cell={
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
                      'height': 'auto',  # Fixed height for the virtualized table
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
                  }

                  )

    ]),

    dbc.Row([
        dbc.Col(html.Div([
            html.Button('Malzeme Tablosunu İndir', id='btn-download-malzeme'),
            dcc.Download(id='download-malzeme')
        ]), width={"size": 3, "offset": 5}),  # Bu, butonu sağa hizalar
    ]),

    dbc.Row([
        DataTable(id=f"material_table",
                            style_cell ={
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
                            style_table ={
                                   # 'overflowX': 'auto'
                                    'height': '800px',  # Fixed height for the virtualized table
                                    #'width': '800px',  # Fixed width for the table
                                    'overflowY': 'auto',  # Enable vertical scroll
                                    'borderCollapse': 'collapse',  # Collapse borders
                                    'border': '1px solid black'  # Border around the table
                            },
                            style_header ={
                                    'fontWeight': 'bold',  # Make header text bold
                                    'backgroundColor': 'rgba(0, 0, 0, 0.1)',  # Slightly darker background for the header
                                    'borderBottom': '1px solid black',  # Bottom border for the header cells
                                    'color': 'black'  # Font color for the header
                            }
        )
    ])
], fluid=True)


def formatted_weeks_first():
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
    formatted_weeks.insert(0, 'ANAMAMUL')
    formatted_weeks.insert(0, 'COSTCENTER')
    formatted_weeks.insert(0, 'WORKCENTER')
    formatted_weeks.insert(0, 'CAPGRP')

    formatted_weeks.insert(0, 'SURE_HESAPLAMA_KODU')
    formatted_weeks.insert(0, 'MACHINE')
    formatted_weeks.insert(0, 'LABOUR')
    formatted_weeks.insert(0, 'SETUP')
    formatted_weeks.insert(0, 'BASEQUAN')

    return formatted_weeks


@app.callback(
   [Output('stored_data', 'data'),
    Output('stored_data_pivot', 'data'),
    Output("costcenter_table","data"),
    Output("costcenter_table","columns"),
    Output("costcenter_table","style_data_conditional"),
    Output("capasity_table_costcenter","columns"),
    Output("capasity_table_costcenter","style_data_conditional"),
    Output("workcenter_table", "columns"),
    Output("workcenter_table", "style_data_conditional"),
    Output("capasity_table_workcenter", "columns"),
    Output("capasity_table_workcenter", "style_data_conditional"),
    Output("material_table", "columns"),
    Output("material_table", "style_data_conditional"),
    Output("costcenter-dropdown", "options"),
    Output("costcenter-dropdown", "value")],
   Input('section-dropdown', 'value')
)
def update_graph(selected_section):
    weeks_first = formatted_weeks_first()

    # gerekli section değişikliği
    if selected_section == "Hepsi":
        df1 = ag.run_query(r"SELECT B.CAPGRP,A.* FROM VLFPLATECAP A LEFT JOIN IASCAPWRKCTR B ON A.MATERIAL = B.MATERIAL AND A.WORKCENTER = B.WORKCENTER WHERE A.COSTCENTER != ''")
        df1 = df1[weeks_first]

        df2 = ag.run_query(r"SELECT B.CAPGRP,A.* FROM VLFCHECKVALFCAP A LEFT JOIN IASCAPWRKCTR B ON A.MATERIAL = B.MATERIAL AND A.WORKCENTER = B.WORKCENTER WHERE A.WORKCENTER != 'SA'")
        df2 = df2[weeks_first]

        df3 = ag.run_query(r"SELECT B.CAPGRP,A.* FROM VLFPRESCAP A LEFT JOIN IASCAPWRKCTR B ON A.ANAMAMUL = B.MATERIAL AND A.WORKCENTER = B.WORKCENTER WHERE A.COSTCENTER != ''")
        df3 = df3[weeks_first]
        df3['MATERIAL'] = df3['ANAMAMUL']

        df = pd.concat([df1, df2, df3], ignore_index=True)

    elif selected_section == "Plaka":
        df = ag.run_query(r"SELECT B.CAPGRP,A.* FROM VLFPLATECAP A LEFT JOIN IASCAPWRKCTR B ON A.MATERIAL = B.MATERIAL AND A.WORKCENTER = B.WORKCENTER WHERE A.COSTCENTER != ''")
    elif selected_section == "Checkvalf":
        df = ag.run_query(r"SELECT B.CAPGRP,A.* FROM VLFCHECKVALFCAP A LEFT JOIN IASCAPWRKCTR B ON A.MATERIAL = B.MATERIAL AND A.WORKCENTER = B.WORKCENTER WHERE A.WORKCENTER != 'SA'")
    elif selected_section == "Pres":
        df = ag.run_query(r"SELECT B.CAPGRP,A.* FROM VLFPRESCAP A LEFT JOIN IASCAPWRKCTR B ON A.ANAMAMUL = B.MATERIAL AND A.WORKCENTER = B.WORKCENTER WHERE A.COSTCENTER != ''")
    else:
        df1 = ag.run_query(r"SELECT B.CAPGRP,A.* FROM VLFPLATECAP A LEFT JOIN IASCAPWRKCTR B ON A.MATERIAL = B.MATERIAL AND A.WORKCENTER = B.WORKCENTER WHERE A.COSTCENTER != ''")
        df1 = df1[weeks_first]

        df2 = ag.run_query(r"SELECT B.CAPGRP,A.* FROM VLFCHECKVALFCAP A LEFT JOIN IASCAPWRKCTR B ON A.MATERIAL = B.MATERIAL AND A.WORKCENTER = B.WORKCENTER WHERE A.WORKCENTER != 'SA'")
        df2 = df2[weeks_first]

        df3 = ag.run_query(r"SELECT B.CAPGRP,A.* FROM VLFPRESCAP A LEFT JOIN IASCAPWRKCTR B ON A.ANAMAMUL = B.MATERIAL AND A.WORKCENTER = B.WORKCENTER WHERE A.COSTCENTER != ''")
        df3 = df3[weeks_first]
        df3['MATERIAL'] = df3['ANAMAMUL']

        df = pd.concat([df1, df2, df3], ignore_index=True)
    df['COSTCENTER'] = df['COSTCENTER'].replace({'CNCTORN2': 'CNCTORNA', 'CNCTORN3': 'CNCTORNA'})
    df['COSTCENTER'] = df['COSTCENTER'].replace('ELISI2', 'ELISI')
    df['COSTCENTER'] = df['COSTCENTER'].replace({'ISOFINI2': 'ISOFINIS', 'ISOFINI3': 'ISOFINIS', 'ISOFINI4': 'ISOFINIS'})
    df['COSTCENTER'] = df['COSTCENTER'].replace('KALITEF2', 'KALITEF')
    df['COSTCENTER'] = df['COSTCENTER'].replace({'KURUTMA2': 'KURUTMA', 'KURUTMA3': 'KURUTMA', 'KURUTMA4': 'KURUTMA'})
    df.loc[df['CAPGRP'] == 'FINAL TASLAMA', 'COSTCENTER'] = 'FINAL TASLAMA'
    df.loc[df['CAPGRP'] == 'KABA TASLAMA', 'COSTCENTER'] = 'KABA TASLAMA'

    print('here')
    print(df)
    def pivotting_table():
        today = datetime.today()
        one_week_ago = today - timedelta(days=7)
        year_ago, week_num_ago, week_day_ago = one_week_ago.isocalendar()
        formatted_date_one_week_ago = f"{year_ago}-{week_num_ago}"

        df_sade = df[formatted_weeks()]

        pivot_columns = df_sade.columns.difference(
            ['ANAMAMUL','MATERIAL', 'COSTCENTER', 'WORKCENTER', 'SURE_HESAPLAMA_KODU', 'MACHINE', 'LABOUR', 'SETUP', 'BASEQUAN'])

        # Pivot the data
        pivoted_df = df.melt(
            id_vars=['ANAMAMUL','MATERIAL', 'COSTCENTER', 'WORKCENTER', 'SURE_HESAPLAMA_KODU', 'MACHINE', 'LABOUR', 'SETUP',
                     'BASEQUAN'], value_vars=pivot_columns, var_name='current_week', value_name='value')

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
        formatted_weeks.insert(0, 'ANAMAMUL')
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
    df_grouped = df_prepared.groupby(
        ['MATERIAL', 'COSTCENTER', 'WORKCENTER', 'SURE_HESAPLAMA_KODU', 'MACHINE', 'LABOUR', 'SETUP', 'BASEQUAN',
         'current_week']).agg({'value_min': 'sum', 'ANAMAMUL': 'max'}).reset_index()

    # Son olarak, pivot işlemini gerçekleştirin
    pivot_result = df_grouped.pivot(
        index=['ANAMAMUL','MATERIAL', 'COSTCENTER', 'WORKCENTER', 'SURE_HESAPLAMA_KODU', 'MACHINE', 'LABOUR', 'SETUP', 'BASEQUAN'],
        columns='current_week', values='value_min').reset_index()



    sum_df_pivot_costcenter = pivot_result.groupby(['COSTCENTER'], as_index=False).sum()

    unique_costcenters = pivot_result["COSTCENTER"].unique().tolist()
    sorted_costcenters = sorted(unique_costcenters)

    options_list = [{'label': wc, 'value': wc} for wc in sorted_costcenters]
    first_option = options_list[0] if options_list else None



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
                "format": Format(precision=0, scheme=Scheme.fixed)
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
                "format": Format(precision=0, scheme=Scheme.fixed)
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
                "format": Format(precision=0, scheme=Scheme.fixed)
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
                "format": Format(precision=0, scheme=Scheme.fixed)
            })
    df_prepared = df_prepared.to_json(date_format='iso', orient='split')
    pivot_result = pivot_result.to_json(date_format='iso', orient='split')

    return [df_prepared, pivot_result, sum_df_pivot_costcenter.to_dict('records'),formatted_columns,
         [{'if': {'column_id': column_id, 'filter_query': '{{{}}} = 0'.format(column_id)},'color': 'white'} for
         column_id in [col['id'] for col in formatted_columns]],
         formatted_columns_capcostcenter,
         [{'if': {'column_id': column_id, 'filter_query': '{{{}}} = 0'.format(column_id)},'color': 'white'} for
         column_id in [col['id'] for col in formatted_columns_capcostcenter]],
         formatted_columns_workcenter,
         [{'if': {'column_id': column_id, 'filter_query': '{{{}}} = 0'.format(column_id)}, 'color': 'white'} for
        column_id in [col['id'] for col in formatted_columns_workcenter]],
             formatted_columns_capcostcenter,
            [{'if': {'column_id': column_id, 'filter_query': '{{{}}} = 0'.format(column_id)}, 'color': 'white'} for
             column_id in [col['id'] for col in formatted_columns_capcostcenter]],
             formatted_columns_material,
            [{'if': {'column_id': column_id, 'filter_query': '{{{}}} = 0'.format(column_id)}, 'color': 'white'} for
             column_id in [col['id'] for col in formatted_columns_material]],
            options_list, first_option["value"]
            ]


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
    weeks_dict = create_weeks_dict()
    filtered_df = df_pivot[df_pivot['COSTCENTER'] == selected_costcenter]
    sum_df = filtered_df.groupby(['COSTCENTER'], as_index=False).sum()
    sum_df['STAT'] = 'Kapasite İhtiyacı'
    weeks = list(weeks_dict.values())
    filtered_sum_df = sum_df[['STAT'] + weeks]

    sum_df_wc = filtered_df.groupby(['WORKCENTER'], as_index=False).sum()
    work_center_sayisi = sum_df_wc.shape[0]

    total_capacity = 5100 * work_center_sayisi
    first_week = list(weeks_dict.values())[0]

    data_for_new_row = {'STAT': 'Toplam Kapasite'}
    data_for_new_row.update({week: 0 if week == first_week else total_capacity for week in weeks_dict.values()})
    # Yeni satırı DataFrame'e ekle
    new_row = pd.DataFrame([data_for_new_row])

    cap_df = pd.concat([filtered_sum_df, new_row], ignore_index=True)


    result_row = {'STAT': 'Kapasite Farkı'}
    result_row.update(cap_df[list(weeks_dict.values())].iloc[1] - cap_df[list(weeks_dict.values())].iloc[0])

    # Append the result as a new row in the DataFrame
    cap_df = cap_df.append(result_row, ignore_index=True)

    numeric_cols = cap_df.columns.difference(['STAT'])

    # 'result_row' satırının kümülatif toplamını hesaplayın
    cumulative_sum = cap_df.loc[cap_df['STAT'] == 'Kapasite Farkı', numeric_cols].cumsum(axis=1)

    # Kümülatif toplam sonuçlarını yeni bir satıra ekleyin
    new_cumulative_row = {'STAT': 'Kümülatif Toplam'}
    new_cumulative_row.update(cumulative_sum.iloc[0])

    # Yeni kümülatif toplam satırını cap_df DataFrame'ine ekleyin
    cap_df = cap_df.append(new_cumulative_row, ignore_index=True)


    # 'Kapasite İhtiyacı' ve 'Toplam Kapasite' satırlarını seçin
    uretim_ihtiyaci = cap_df[cap_df['STAT'] == 'Kapasite İhtiyacı'].iloc[0]
    toplam_kapasite = cap_df[cap_df['STAT'] == 'Toplam Kapasite'].iloc[0]


    # Doluluk oranını hesaplamak için bir boş liste oluşturun
    doluluk_orani = []

    # Her bir numeric kolon için doluluk oranını hesaplayın
    for col in weeks_dict:
        # İlk kolon için özel durum: Eğer 'Toplam Kapasite' 0 ise, doluluk oranı da 0 olmalıdır
        if toplam_kapasite[col] == 0:
            doluluk_orani.append(0)
        else:
            # Doluluk oranını hesaplayın ve listeye ekleyin
            oran = (uretim_ihtiyaci[col] / toplam_kapasite[col]) * 100
            doluluk_orani.append(oran)

    # Doluluk oranlarını içeren yeni bir satır oluşturun
    doluluk_orani_satiri = pd.DataFrame([doluluk_orani], columns=weeks_dict)
    doluluk_orani_satiri['STAT'] = 'Doluluk Oranı'

    # Yeni satırı DataFrame'e ekleyin
    cap_df_prepared = pd.concat([cap_df, doluluk_orani_satiri], ignore_index=True)

    sum_df_wc = filtered_df.groupby(['WORKCENTER'], as_index=False).sum()

    return cap_df_prepared.to_dict('records'),sum_df_wc.to_dict('records')
@app.callback(
    [Output('figx', 'figure'),Output('material_table', 'data'),
     Output('capasity_table_workcenter', 'data')],
     Input('workcenter-dropdown', 'value'),
     [State('stored_data', 'data'),
      State('stored_data_pivot', 'data'),
      State('section-dropdown', 'value'),
      State('costcenter-dropdown', 'value')]
)
def update_graph(selected_workcenter, df_json, df_json_pivot, selected_section, selected_costcenter):
    if df_json is None:
        return px.bar()
    if df_json is None:
        return [], None
    if df_json_pivot is None:
        return []
    df = pd.read_json(df_json, orient='split')
    weeks_dict = create_weeks_dict()
    df_pivot = pd.read_json(df_json_pivot, orient='split')

    if selected_workcenter == "Hepsi":
        filtered_df_pivot_cap = df_pivot[df_pivot['COSTCENTER'] == selected_costcenter]
        unique_workcenters = filtered_df_pivot_cap["WORKCENTER"].unique().tolist()
        sorted_workcenters = sorted(unique_workcenters)
        first_element = sorted_workcenters[0] if sorted_workcenters else None
        filtered_df_pivot_cap = filtered_df_pivot_cap[df_pivot['WORKCENTER'] == first_element]

        filtered_df_pivot = df_pivot[df_pivot['COSTCENTER'] == selected_costcenter]

    else:
        filtered_df_pivot_cap = df_pivot[df_pivot['COSTCENTER'] == selected_costcenter]
        filtered_df_pivot = df_pivot[df_pivot['COSTCENTER'] == selected_costcenter]
        filtered_df_pivot_cap = filtered_df_pivot_cap[filtered_df_pivot_cap['WORKCENTER'] == selected_workcenter]
        filtered_df_pivot = filtered_df_pivot[filtered_df_pivot['WORKCENTER'] == selected_workcenter]

    if selected_section == 'Pres':
        week_columns = list(weeks_dict.values())
        columns_to_select = ['ANAMAMUL'] + week_columns

        filtered_df_pivot = filtered_df_pivot[columns_to_select]
        filtered_df_pivot = filtered_df_pivot.rename(columns={'ANAMAMUL': 'MATERIAL'})


    sum_df_pivot = filtered_df_pivot_cap.groupby(['WORKCENTER'], as_index=False).sum()
    sum_df_pivot['STAT'] = 'Kapasite İhtiyacı'
    weeks = list(weeks_dict.values())
    filtered_sum_df = sum_df_pivot[['STAT'] + weeks]

    if selected_workcenter == "Hepsi":
        filtered_df = df[df['COSTCENTER'] == selected_costcenter]
        unique_workcenters_df = filtered_df["WORKCENTER"].unique().tolist()
        sorted_workcenters_df = sorted(unique_workcenters_df)
        first_element_df = sorted_workcenters_df[0] if sorted_workcenters_df else None
        filtered_df = filtered_df[filtered_df['WORKCENTER'] == first_element_df]
    else:
        filtered_df = df[df['COSTCENTER'] == selected_costcenter]
        filtered_df = filtered_df[filtered_df['WORKCENTER'] == selected_workcenter]

    sum_df = filtered_df.groupby(['WORKCENTER', 'current_week']).sum({'value_min'}).reset_index()
    figx = px.bar(sum_df, x='current_week', y='value_min')
    figx.update_xaxes(type='category')



    total_capacity = 5100
    first_week = list(weeks_dict.values())[0]
    data_for_new_row = {'STAT': 'Toplam Kapasite'}
    data_for_new_row.update({week: 0 if week == first_week else total_capacity for week in weeks_dict.values()})
    # Yeni satırı DataFrame'e ekle
    new_row = pd.DataFrame([data_for_new_row])

    cap_df = pd.concat([filtered_sum_df, new_row], ignore_index=True)

    result_row = {'STAT': 'Kapasite Farkı'}
    result_row.update(cap_df[list(weeks_dict.values())].iloc[1] - cap_df[list(weeks_dict.values())].iloc[0])

    cap_df = pd.concat([cap_df, pd.DataFrame([result_row])], ignore_index=True)

    numeric_cols = cap_df.columns.difference(['STAT'])

    # 'result_row' satırının kümülatif toplamını hesaplayın
    cumulative_sum = cap_df.loc[cap_df['STAT'] == 'Kapasite Farkı', numeric_cols].cumsum(axis=1)

    # Kümülatif toplam sonuçlarını yeni bir satıra ekleyin
    new_cumulative_row = {'STAT': 'Kümülatif Toplam'}
    new_cumulative_row.update(cumulative_sum.iloc[0])

    # Yeni kümülatif toplam satırını cap_df DataFrame'ine ekleyin
    cap_df = cap_df.append(new_cumulative_row, ignore_index=True)

    # 'Kapasite İhtiyacı' ve 'Toplam Kapasite' satırlarını seçin
    uretim_ihtiyaci = cap_df[cap_df['STAT'] == 'Kapasite İhtiyacı'].iloc[0]
    toplam_kapasite = cap_df[cap_df['STAT'] == 'Toplam Kapasite'].iloc[0]

    # Doluluk oranını hesaplamak için bir boş liste oluşturun
    doluluk_orani = []

    # Her bir numeric kolon için doluluk oranını hesaplayın
    for col in weeks_dict:
        # İlk kolon için özel durum: Eğer 'Toplam Kapasite' 0 ise, doluluk oranı da 0 olmalıdır
        if toplam_kapasite[col] == 0:
            doluluk_orani.append(0)
        else:
            # Doluluk oranını hesaplayın ve listeye ekleyin
            oran = (uretim_ihtiyaci[col] / toplam_kapasite[col]) * 100
            doluluk_orani.append(oran)

    # Doluluk oranlarını içeren yeni bir satır oluşturun
    doluluk_orani_satiri = pd.DataFrame([doluluk_orani], columns=weeks_dict)
    doluluk_orani_satiri['STAT'] = 'Doluluk Oranı'

    # Yeni satırı DataFrame'e ekleyin
    cap_df_prepared = pd.concat([cap_df, doluluk_orani_satiri], ignore_index=True)

    return figx,filtered_df_pivot.to_dict('records'), cap_df_prepared.to_dict('records')



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
    sorted_workcenters.append("Hepsi")
    options_list = [{'label': wc, 'value': wc} for wc in sorted_workcenters]
    first_option = options_list[0] if options_list else None
    return options_list, first_option["value"]


@app.callback(
    Output('download-costcenter', 'data'),
    Input('btn-download-costcenter', 'n_clicks'),
    State('stored_data_pivot', 'data'),
    prevent_initial_call=True
)
def download_costcenter_data(n_clicks, df_json_pivot):
    if df_json_pivot is None:
        return []
    df_pivot = pd.read_json(df_json_pivot, orient='split')
    df_pivot_costcenter = df_pivot.groupby(['COSTCENTER'], as_index=False).sum()
    df_pivot_costcenter = df_pivot_costcenter.round(1)
    # DataFrame'inizi oluşturun veya var olan bir DataFrame'i kullanın

    return dcc.send_data_frame(df_pivot_costcenter.to_excel, "costcenter_data.xlsx", sheet_name="Costcenter")

@app.callback(
    Output('download-costcenter_kapasite', 'data'),
    Input('btn-download-costcenter_kapasite', 'n_clicks'),
    State('stored_data_pivot', 'data'),
    State('costcenter-dropdown', 'value'),
    prevent_initial_call=True
)
def download_costcenter_kapasite_data(n_clicks, df_json_pivot,selected_costcenter):
    if df_json_pivot is None:
        return []
    df_pivot = pd.read_json(df_json_pivot, orient='split')
    weeks_dict = create_weeks_dict()
    filtered_df = df_pivot[df_pivot['COSTCENTER'] == selected_costcenter]
    sum_df = filtered_df.groupby(['COSTCENTER'], as_index=False).sum()
    sum_df = sum_df.round(0)
    # DataFrame'inizi oluşturun veya var olan bir DataFrame'i kullanın
    sum_df['STAT'] = 'Kapasite İhtiyacı'

    weeks = list(weeks_dict.values())
    filtered_sum_df = sum_df[['STAT'] + weeks]

    sum_df_wc = filtered_df.groupby(['WORKCENTER'], as_index=False).sum()
    work_center_sayisi = sum_df_wc.shape[0]

    total_capacity = 5100 * work_center_sayisi
    first_week = list(weeks_dict.values())[0]

    data_for_new_row = {'STAT': 'Toplam Kapasite'}
    data_for_new_row.update({week: 0 if week == first_week else total_capacity for week in weeks_dict.values()})
    # Yeni satırı DataFrame'e ekle
    new_row = pd.DataFrame([data_for_new_row])

    cap_df = pd.concat([filtered_sum_df, new_row], ignore_index=True)

    result_row = {'STAT': 'Kapasite Farkı'}
    result_row.update(cap_df[list(weeks_dict.values())].iloc[1] - cap_df[list(weeks_dict.values())].iloc[0])

    # Append the result as a new row in the DataFrame
    cap_df = cap_df.append(result_row, ignore_index=True)

    numeric_cols = cap_df.columns.difference(['STAT'])

    # 'result_row' satırının kümülatif toplamını hesaplayın
    cumulative_sum = cap_df.loc[cap_df['STAT'] == 'Kapasite Farkı', numeric_cols].cumsum(axis=1)

    # Kümülatif toplam sonuçlarını yeni bir satıra ekleyin
    new_cumulative_row = {'STAT': 'Kümülatif Toplam'}
    new_cumulative_row.update(cumulative_sum.iloc[0])

    # Yeni kümülatif toplam satırını cap_df DataFrame'ine ekleyin
    cap_df = cap_df.append(new_cumulative_row, ignore_index=True)

    # 'Kapasite İhtiyacı' ve 'Toplam Kapasite' satırlarını seçin
    uretim_ihtiyaci = cap_df[cap_df['STAT'] == 'Kapasite İhtiyacı'].iloc[0]
    toplam_kapasite = cap_df[cap_df['STAT'] == 'Toplam Kapasite'].iloc[0]

    # Doluluk oranını hesaplamak için bir boş liste oluşturun
    doluluk_orani = []

    # Her bir numeric kolon için doluluk oranını hesaplayın
    for col in weeks_dict:
        # İlk kolon için özel durum: Eğer 'Toplam Kapasite' 0 ise, doluluk oranı da 0 olmalıdır
        if toplam_kapasite[col] == 0:
            doluluk_orani.append(0)
        else:
            # Doluluk oranını hesaplayın ve listeye ekleyin
            oran = (uretim_ihtiyaci[col] / toplam_kapasite[col]) * 100
            doluluk_orani.append(oran)

    # Doluluk oranlarını içeren yeni bir satır oluşturun
    doluluk_orani_satiri = pd.DataFrame([doluluk_orani], columns=weeks_dict)
    doluluk_orani_satiri['STAT'] = 'Doluluk Oranı'

    # Yeni satırı DataFrame'e ekleyin
    cap_df_prepared = pd.concat([cap_df, doluluk_orani_satiri], ignore_index=True)
    cap_df_prepared = cap_df_prepared.round(0)

    return dcc.send_data_frame(cap_df_prepared.to_excel, "costcenter_kapasite.xlsx", sheet_name="Costcenter Kapasite")

@app.callback(
    Output('download-workcenter', 'data'),
    Input('btn-download-workcenter', 'n_clicks'),
    State('stored_data_pivot', 'data'),
    State('costcenter-dropdown', 'value'),
    prevent_initial_call=True
)
def download_workcenter_data(n_clicks, df_json_pivot,selected_costcenter):
    if df_json_pivot is None:
        return []
    df_pivot = pd.read_json(df_json_pivot, orient='split')
    filtered_df = df_pivot[df_pivot['COSTCENTER'] == selected_costcenter]
    sum_df_wc = filtered_df.groupby(['WORKCENTER'], as_index=False).sum()
    sum_df_wc = sum_df_wc.round(1)

    return dcc.send_data_frame(sum_df_wc.to_excel, "workcenter_data.xlsx", sheet_name="Workcenter")


@app.callback(
    Output('download-workcenter_kapasite', 'data'),
    Input('btn-download-workcenter_kapasite', 'n_clicks'),
    State('stored_data_pivot', 'data'),
    State('workcenter-dropdown', 'value'),
State('costcenter-dropdown', 'value'),
    prevent_initial_call=True
)
def download_workcenter_kapasite_data(n_clicks, df_json_pivot,selected_workcenter,selected_costcenter):
    if df_json_pivot is None:
        return []
    df_pivot = pd.read_json(df_json_pivot, orient='split')
    weeks_dict = create_weeks_dict()
    if selected_workcenter == "Hepsi":
        filtered_df_pivot = df_pivot[df_pivot['COSTCENTER'] == selected_costcenter]
        unique_workcenters = filtered_df_pivot["WORKCENTER"].unique().tolist()
        sorted_workcenters = sorted(unique_workcenters)
        first_element = sorted_workcenters[0] if sorted_workcenters else None
        filtered_df_pivot = df_pivot[df_pivot['WORKCENTER'] == first_element]
    else:
        filtered_df_pivot = df_pivot[df_pivot['COSTCENTER'] == selected_costcenter]
        filtered_df_pivot = filtered_df_pivot[filtered_df_pivot['WORKCENTER'] == selected_workcenter]

    sum_df_pivot = filtered_df_pivot.groupby(['WORKCENTER'], as_index=False).sum()
    sum_df_pivot = sum_df_pivot.round(0)
    sum_df_pivot['STAT'] = 'Kapasite İhtiyacı'
    # DataFrame'inizi oluşturun veya var olan bir DataFrame'i kullanın

    weeks = list(weeks_dict.values())
    filtered_sum_df = sum_df_pivot[['STAT'] + weeks]


    total_capacity = 5100
    first_week = list(weeks_dict.values())[0]
    data_for_new_row = {'STAT': 'Toplam Kapasite'}
    data_for_new_row.update({week: 0 if week == first_week else total_capacity for week in weeks_dict.values()})
    # Yeni satırı DataFrame'e ekle
    new_row = pd.DataFrame([data_for_new_row])

    cap_df = pd.concat([filtered_sum_df, new_row], ignore_index=True)

    result_row = {'STAT': 'Kapasite Farkı'}
    result_row.update(cap_df[list(weeks_dict.values())].iloc[1] - cap_df[list(weeks_dict.values())].iloc[0])

    cap_df = pd.concat([cap_df, pd.DataFrame([result_row])], ignore_index=True)

    numeric_cols = cap_df.columns.difference(['STAT'])

    # 'result_row' satırının kümülatif toplamını hesaplayın
    cumulative_sum = cap_df.loc[cap_df['STAT'] == 'Kapasite Farkı', numeric_cols].cumsum(axis=1)

    # Kümülatif toplam sonuçlarını yeni bir satıra ekleyin
    new_cumulative_row = {'STAT': 'Kümülatif Toplam'}
    new_cumulative_row.update(cumulative_sum.iloc[0])

    # Yeni kümülatif toplam satırını cap_df DataFrame'ine ekleyin
    cap_df = cap_df.append(new_cumulative_row, ignore_index=True)

    # 'Kapasite İhtiyacı' ve 'Toplam Kapasite' satırlarını seçin
    uretim_ihtiyaci = cap_df[cap_df['STAT'] == 'Kapasite İhtiyacı'].iloc[0]
    toplam_kapasite = cap_df[cap_df['STAT'] == 'Toplam Kapasite'].iloc[0]

    # Doluluk oranını hesaplamak için bir boş liste oluşturun
    doluluk_orani = []

    # Her bir numeric kolon için doluluk oranını hesaplayın
    for col in weeks_dict:
        # İlk kolon için özel durum: Eğer 'Toplam Kapasite' 0 ise, doluluk oranı da 0 olmalıdır
        if toplam_kapasite[col] == 0:
            doluluk_orani.append(0)
        else:
            # Doluluk oranını hesaplayın ve listeye ekleyin
            oran = (uretim_ihtiyaci[col] / toplam_kapasite[col]) * 100
            doluluk_orani.append(oran)

    # Doluluk oranlarını içeren yeni bir satır oluşturun
    doluluk_orani_satiri = pd.DataFrame([doluluk_orani], columns=weeks_dict)
    doluluk_orani_satiri['STAT'] = 'Doluluk Oranı'

    # Yeni satırı DataFrame'e ekleyin
    cap_df_prepared = pd.concat([cap_df, doluluk_orani_satiri], ignore_index=True)
    cap_df_prepared = cap_df_prepared.round(0)

    return dcc.send_data_frame(cap_df_prepared.to_excel, "workcenter_kapasite.xlsx", sheet_name="Workcenter Kapasite")

@app.callback(
    Output('download-malzeme', 'data'),
    Input('btn-download-malzeme', 'n_clicks'),
    State('stored_data_pivot', 'data'),
    State('workcenter-dropdown', 'value'),
    State('costcenter-dropdown', 'value'),
    prevent_initial_call=True
)
def download_malzeme_data(n_clicks, df_json_pivot,selected_workcenter,selected_costcenter):
    if df_json_pivot is None:
        return []
    df_pivot = pd.read_json(df_json_pivot, orient='split')
    if selected_workcenter == "Hepsi":
        filtered_df_pivot = df_pivot[df_pivot['COSTCENTER'] == selected_costcenter]
    else:
        filtered_df_pivot = df_pivot[df_pivot['COSTCENTER'] == selected_costcenter]
        filtered_df_pivot = filtered_df_pivot[filtered_df_pivot['WORKCENTER'] == selected_workcenter]

    filtered_df_pivot = filtered_df_pivot.round(1)
    # DataFrame'inizi oluşturun veya var olan bir DataFrame'i kullanın

    return dcc.send_data_frame(filtered_df_pivot.to_excel, "malzeme_data.xlsx", sheet_name="Malzeme")


