import numpy as np
import pandas as pd
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
from mysql.connector import connection

from run.agent import agiot as ag
from valfapp.app import app
from datetime import date, timedelta, datetime
from config import kb
from dash_table import DataTable
from valfapp.functions.functions_prd import indicator_for_tvs
import statistics
from dash.dependencies import Input, Output


layout = [
    dbc.Row([html.H1("Günlük Üretim Raporu",
                     style={'text-align': 'center', "fontFamily": 'Arial Black', 'fontSize': 30,
                            'backgroundColor': '#f0f0f0'})])
    ,

    dbc.Row(html.Div(children=[
        dcc.DatePickerRange(id='date-picker-range',
                             start_date=date.today() + timedelta(days=-kb),
                             end_date = date.today(),
                             persistence=True,
                             persistence_type='memory'
                             ),
    ], style={'display': 'flex', 'flexDirection': 'row'})
    ),

    dbc.Row([
        dbc.Col([
            html.H3("Rapor",style={"align":"center"}),
            DataTable(
                id='uretim_data',
                columns=[],

                style_table={
                    'height' : '800',
                    'overflowY': 'auto',
                    'border': 'thin lightgrey solid',
                    'fontFamily': 'Arial, sans-serif',
                    'minWidth': '70%',  # Adjust this value to set the minimum width
                    'width': '80%',  # Adjust this value to set the width
                    'textAlign': 'center',
                },
                style_header={
                    'backgroundColor': 'rgba(0, 0, 0, 0)',  # Semi-transparent background
                    'fontWeight': 'bold',  # Bold font
                    'color': '#2F4F4F',  # Cool text color
                    'fontFamily': 'Arial, sans-serif',  # Font family
                    'fontSize': '14px',
                    'border': '1px solid  brown',
                    'borderRadius': '2px'
                    # Font size
                },

            ),
        ],width=8),

        dbc.Col([html.Div(id='indicator-figures-container', className='row'), ], width=4),

    ]),

    dbc.Row([dbc.Col([dcc.Graph(id="gantt_chart",style={"margin-top":70}),], width=9),
    ]),
]

@app.callback(
    Output('uretim_data', 'columns'),
    Output("uretim_data", 'data'),
    Output('indicator-figures-container', 'children'),
    Input("date-picker-range", 'start_date'),
    Input("date-picker-range", 'end_date')
)
def update_summary_table(start_date, end_date):
    result_data = []
    fig_container = []
    counter = 0

    query_path = r"C:\Users\fozturk\Documents\GitHub\Charting\queries\vlf_ayıklamakmr_uretim.sql"
    text_to_find = ['XYZ', 'XXXX-XX-XX', 'YYYY-YY-YY']

    query_path2 = r"C:\Users\fozturk\Documents\GitHub\Charting\queries\vlf_ayıklamakmr_times.sql"
    text_to_find2 = ['XYZ', 'XXXX-XX-XX', 'YYYY-YY-YY']

    for x in range(1, 7):
        text_to_put = [f'KMR-0{x}', start_date, end_date]
        data = ag.editandrun_query(query_path, text_to_find, text_to_put)

        text_to_put2 = [f'KMR-0{x}', start_date, end_date]
        data2 = ag.editandrun_query(query_path2, text_to_find2, text_to_put2)

        data2["MATERIAL"] = data["MATERIAL"].apply(lambda x: x.split('\x00', 1)[0])

        merged_data = pd.merge(data, data2, left_on=['PRDORDER', 'AYKDATE', 'SHIFTURETIM'],
                               right_on=['CONFIRMATION', 'MACHINEDATE', 'SHIFTAYK'], how='inner')

        merged_data["MIN_WORKSTART"] = pd.to_datetime(merged_data["MIN_WORKSTART"]).dt.strftime('%Y-%m-%d %H:%M:%S')
        merged_data["MAX_WORKEND"] = pd.to_datetime(merged_data["MAX_WORKEND"]).dt.strftime('%Y-%m-%d %H:%M:%S')

        result_data.append(merged_data)



    final_result = pd.concat(result_data, ignore_index=True)

    table_data = final_result.groupby(['MACHINE', 'SHIFTAYK', 'NAME', 'MATERIAL_x', 'PRDORDER']).agg(
        {'QUANTITY': 'first', 'NOTOK': 'first',
         'MIN_WORKSTART': 'min', 'MAX_WORKEND': 'max', 'CALISIYOR': 'sum',
         'DURUS': 'first', 'SANIYE_DENETLENEN': 'first', 'PPM': 'first'})

    table_data['SANIYE_DENETLENEN'] = (table_data['QUANTITY'] + table_data['NOTOK']) / (table_data['CALISIYOR']) / 60
    table_data = table_data.sort_values(by=['MACHINE', 'MIN_WORKSTART'])


    table_data = table_data.reset_index()

    table_data['MIN_WORKSTART'] = pd.to_datetime(table_data['MIN_WORKSTART']).dt.strftime('%Y-%m-%d %H:%M:%S')


    machine_data = table_data.groupby(['MACHINE']).agg(
        {'QUANTITY': 'sum', 'NOTOK': 'sum', 'MIN_WORKSTART': 'min', 'MAX_WORKEND': 'max', 'CALISIYOR': 'sum',
        'PPM': 'first'})

    domain_y1 = 0;
    domain_y2 = 0;

    for machine_index, indicator_data in machine_data.iterrows():


        domain_y1 = 0.05 + domain_y1
        domain_y2 = 0.15 + domain_y2

        fig2 = go.Figure()
        fig2.add_trace(go.Indicator(
            value=((indicator_data['QUANTITY'] + indicator_data['NOTOK']) / (indicator_data['CALISIYOR']) / 60),
            title = {'text': "Saniye Başına Denetlenen"},
            delta={'reference': 6},
            gauge={'axis': {'visible': False}},
            domain={'x': [0.05, 0.50], 'y': [-0.3, 0.25]}) )

        fig2.add_trace(go.Indicator(
            value=indicator_data['PPM'],
            title={'text': "PPM"},
            gauge={
                'shape': "bullet",
                'axis': {'visible': False}},
            domain={'x': [0.05, 0.40], 'y': [domain_y1, domain_y2]})
        )

        fig2.update_layout(
            grid={'rows': 2, 'columns': 2, 'pattern': "independent"},
            template={'data': {'indicator': [{
                'mode': "number+delta+gauge",
                'delta': {'reference': 5000}}]
            }}, height=200,
            width=400,
           ##margin=dict(l=55, r=75, t=55, b=15)  # Adjust margin values to decrease distance

        )

        ##fig_container.append(dcc.Graph(figure=fig2, id=f'indicator-graph-{machine_index}'))

        fig_container.append(html.Div([dcc.Graph(figure=fig2)], className='two columns'))

        counter += 1

        # If two figures are added to the row, start a new row
        if counter == 3:
            counter = 0
            fig_container.append(html.Div([], className='row'))

    columns = [{"name": i, "id": i} for i in table_data.columns]

    return columns, table_data.to_dict("records"), fig_container
@app.callback(

    Output("gantt_chart", "figure"),
    Input("uretim_data", 'data'),
    Input("date-picker-range", 'start_date'),
    Input("date-picker-range", 'end_date'),
    )

def draw_dist_plot(data,start_date,end_date):

    data3 = ag.editandrun_query(r"C:\Users\fozturk\Documents\GitHub\Charting\queries\vlf_ayıklamakmr_timesforgantt.sql",

                               texttofind = ['XXXX-XX-XX','YYYY-YY-YY'],texttoput = [start_date,end_date])

    data3["MIN_WORKSTART"] = pd.to_datetime(data3["MIN_WORKSTART"]).dt.strftime('%Y-%m-%d %H:%M:%S')

    data3["MAX_WORKEND"] = pd.to_datetime(data3["MAX_WORKEND"]).dt.strftime('%Y-%m-%d %H:%M:%S')

    fig = go.Figure()

    fig = px.timeline(data_frame=data3[["MIN_WORKSTART", "MAX_WORKEND", "MACHINEAYK","TYPE"]],
                   x_start="MIN_WORKSTART",
                   x_end="MAX_WORKEND",
                   y='MACHINEAYK', color="TYPE",
                   color_discrete_map={"CALISIYOR": "forestgreen" , "BEKLEME DURUSU" : "red" , "MALZEME DURUSU" : "brown"})

    return fig

