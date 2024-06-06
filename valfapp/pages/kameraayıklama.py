import numpy as np
import pandas as pd
from dash import dcc, html, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
from run.agent import agiot as ag
from valfapp.app import app
from datetime import date, timedelta, datetime
from config import kb
from dash_table import DataTable
import time

from valfapp.layouts import nav_bar

layout = [
    nav_bar,
    dcc.Store(id='ayıklama_data',
              data=[]),
    dcc.Store(id='selected_material', data=None),  # Add this line
    dcc.Store(id='selected_confirmation', data=None),  # Add this line

    dbc.Row([html.H1("Ayıklama Robotu Kalite Sonuçları",
                     style={'text-align': 'center', "fontFamily": 'Arial Black', 'fontSize': 30,'color': 'rgba(255, 171, 76, 0.8)', 'background-color':'white'  })]),

    dbc.Row(html.Div(children=[
        dcc.DatePickerRange(id='date-picker-range',
                             start_date=date.today() + timedelta(days=-kb),
                             end_date = date.today() + timedelta(days=-kb),
                             persistence=True,
                             persistence_type='memory'
                             ),


    ], style={'display': 'flex', 'flexDirection': 'row', "margin-left": 74})
    ),

    dbc.Row([

        dbc.Col([
            html.H3("Hata Oranlarına Göre Azalan Parça Listesi",
                    style={"align": "center", 'color': 'rgba(255, 141, 11, 0.8)', 'padding': '10px'}),
            DataTable(
                id='one_line_summary',
                columns=[
                    {'name': 'MACHINE', 'id': 'MACHINE'},
                    {'name': 'MATERIAL', 'id': 'MATERIAL'},
                    {'name': 'CONFIRMATION', 'id': 'CONFIRMATION'},
                    {'name': 'OK', 'id': 'OK'},
                    {'name': 'TOTALNOTOK', 'id': 'TOTALNOTOK'},
                    {'name': 'NOTOKOLCUSEL', 'id': 'NOTOKOLCUSEL'},
                    {'name': 'NOTOKGORSEL', 'id': 'NOTOKGORSEL'},
                ],
                style_table={
                    'height': '300px',
                    'overflowY': 'auto',
                    'border': 'thin lightgrey solid',
                    'fontFamily': 'Arial, sans-serif',
                    'minWidth': '70%',
                    'width': '100%',
                    'textAlign': 'center',
                    'color': 'rgba(255, 141, 11, 0.8)',
                },
                style_header={
                    'backgroundColor': 'rgba(0, 0, 0, 0)',
                    'fontWeight': 'bold',
                    'color': 'rgba(255, 141, 11, 0.8)',
                    'fontFamily': 'Arial, sans-serif',
                    'fontSize': '16px',
                    'border': '1px dotted brown',
                    'borderRadius': '2px'
                },
                row_selectable='single',
                selected_rows=[],
            ),
        ], width=7, style={'paddingRight': '5px'}),

        dbc.Col([
            html.H3("Üretim Detayları", style={"align": "center", 'color': 'rgba(255, 141, 11, 0.8)',  'padding': '10px'}),
            DataTable(
                id='production',
                columns=[
                    {'name': 'WORKCENTER', 'id': 'WORKCENTER'},
                    {'name': 'NAME', 'id': 'NAME'},
                    {'name': 'CONFDATE', 'id': 'CONFDATE'},
                    {'name': 'OUTPUT', 'id': 'OUTPUT'},
                    {'name': 'WORKINGTIME', 'id': 'WORKINGTIME'},
                    {'name': 'TOOLNUM', 'id': 'TOOLNUM'},
                ],
                style_table={
                    'height': '300px',
                    'overflowY': 'auto',
                    'border': 'thin lightgrey solid',
                    'fontFamily': 'Arial, sans-serif',
                    'minWidth': '100%',
                    'width': '100%',
                    'textAlign': 'center',
                    'color': 'rgba(255, 141, 11, 0.8)',
                },
                style_header={
                    'backgroundColor': 'rgba(0, 0, 0, 0)',
                    'fontWeight': 'bold',
                    'color': 'rgba(255, 141, 11, 0.8)',
                    'fontFamily': 'Arial, sans-serif',
                    'fontSize': '16px',
                    'border': '1px dotted brown',
                    'borderRadius': '2px'
                }
            ),
        ], width=5, style={'paddingLeft': '5px'}),

    ], style={"margin-left": 75}),

    dbc.Row([
                html.Div([
                    html.H1("ÖLÇÜM BİLGİLERİ",
                            style={'textAlign': 'center', 'padding': '23px', 'borderRadius': '5px',
                                   'fontSize': '35px', 'margin-top': 75, 'color': 'rgba(255, 141, 11, 0.8)','background-color':'white','margin-right':100}),
                    dbc.Row([
                        html.H1("İç Çap:", style={'color': 'rgba(255, 141, 11, 0.8)'}),
                        dbc.Col(html.Div([
                            DataTable(
                                id='all_intervals_ic',
                                style_table={
                                    'height': '437px',
                                    'overflowY': 'auto',
                                    'border': 'thin lightgrey solid',
                                    'fontFamily': 'Arial, sans-serif',
                                    'minWidth': '100%',  # Adjusted to full width of the div
                                    'width': '100%',
                                    'textAlign': 'center',
                                },
                                style_header={
                                    'backgroundColor': 'rgb(230, 230, 230)',
                                    'fontWeight': 'bold',
                                    'color': 'rgba(255, 141, 11, 0.8)',
                                    'fontFamily': 'Arial, sans-serif',
                                    'fontSize': '16px',
                                    'border': '1px dotted brown',
                                    'borderRadius': '2px'
                                },
                                style_data_conditional=[
                                    {'if': {'row_index': 'odd'},
                                     'backgroundColor': 'rgb(248, 248, 248)'}
                                ],
                                style_cell={
                                    "textAlign": "center",
                                    "padding": "10px",
                                    "color": "black",
                                    'maxWidth': 70
                                }
                            )
                        ], style={"margin-top": 50}),width=3),
                        dbc.Col(dcc.Graph(id="dist_plot1", style={"margin-top": 50}))
                    ],className="mt-5", justify="around"),

                    dbc.Row([
                        html.H1("Dış Çap:", style={'color': 'rgba(255, 141, 11, 0.8)'}),
                        dbc.Col(html.Div([
                            DataTable(
                                id='all_intervals_dis',
                                style_table={
                                    'height': '430px',
                                    'overflowY': 'auto',
                                    'border': 'thin lightgrey solid',
                                    'fontFamily': 'Arial, sans-serif',
                                    'minWidth': '100%',  # Adjusted to full width of the div
                                    'width': '100%',
                                    'textAlign': 'center',
                                },
                                style_header={
                                    'backgroundColor': 'rgb(230, 230, 230)',
                                    'fontWeight': 'bold',
                                    'color': 'rgba(255, 141, 11, 0.8)',
                                    'fontFamily': 'Arial, sans-serif',
                                    'fontSize': '16px',
                                    'border': '1px dotted brown',
                                    'borderRadius': '20px'
                                },
                                style_data_conditional=[
                                    {'if': {'row_index': 'odd'},
                                     'backgroundColor': 'rgb(248, 248, 248)'}
                                ],
                                style_cell={
                                    "textAlign": "center",
                                    "padding": "10px",
                                    "color": "black",
                                    'maxWidth': 115
                                }
                            )
                        ], style={"margin-top": 50}),width=3),
                        dbc.Col(dcc.Graph(id="dist_plot2", style={"margin-top": 50}))
                    ],className="mt-5", justify="around"),

                    dbc.Row([
                        html.H1("Eş Merkezlilik:", style={'color': 'rgba(255, 141, 11, 0.8)'}),
                        dbc.Col(html.Div([
                            DataTable(
                                id='all_intervals_es',
                                style_table={
                                    'height': '430px',
                                    'overflowY': 'auto',
                                    'border': 'thin lightgrey solid',
                                    'fontFamily': 'Arial, sans-serif',
                                    'minWidth': '100%',  # Adjusted to full width of the div
                                    'width': '100%',
                                    'textAlign': 'center',
                                },
                                style_header={
                                    'backgroundColor': 'rgb(230, 230, 230)',
                                    'fontWeight': 'bold',
                                    'color': 'rgba(255, 141, 11, 0.8)',
                                    'fontFamily': 'Arial, sans-serif',
                                    'fontSize': '16px',
                                    'border': '1px dotted brown',
                                    'borderRadius': '2px'
                                },
                                style_data_conditional=[
                                    {'if': {'row_index': 'odd'},
                                     'backgroundColor': 'rgb(248, 248, 248)'}
                                ],
                                style_cell={
                                    "textAlign": "center",
                                    "padding": "10px",
                                    "color": "black",
                                    'maxWidth': 115
                                }
                            )
                        ], style={"margin-top": 50}),width=3),
                        dbc.Col(dcc.Graph(id="dist_plot3", style={"margin-top": 50}))
                    ],className="mt-5", justify="around")
                ], style={"margin-left": 75}),

    dcc.Interval(id="data_refresh", interval=1000000)

])]


@app.callback(
    Output("material_ayk", 'options'),
    Output("ayıklama_data", 'data'),
    Input("machine_ayk", 'value'),
    State("date-picker-range", 'start_date'),
    State("date-picker-range", 'end_date'),
    prevent_initial_call=True
)
def material_data(n, start_date,end_date):
    data = ag.run_query(f"SELECT * FROM VLFAYIKLAMA WHERE CURDATETIME >= '{start_date}' AND CURDATETIME < '{end_date}'")

    if type(data) is not pd.DataFrame:
        return no_update, no_update
    else:
        if len(data) == 0:
            return no_update, no_update

    data['MINIMUM'] = data['MINIMUM'].astype(float)
    data['MAXIMUM'] = data['MAXIMUM'].astype(float)
    data['QUANTITY'] = data['QUANTITY'].astype(int)
    data["midpoints"] = (data['MINIMUM'] + data['MAXIMUM']) / 2
    data["MATERIAL"] = data["MATERIAL"].apply(lambda x: x.split('\x00', 1)[0])
    data["CURDATETIME"] = pd.to_datetime(data["CURDATETIME"]).dt.strftime('%Y-%m-%d %H:%M:%S')
    data["CURDATETIME"] = pd.to_datetime(data["CURDATETIME"]).dt.date
    data["MACHINE"] = data["MACHINE"].astype(str)
    material_list = list(data["MATERIAL"].unique())

    return material_list, data.to_json(date_format='iso', orient='split')


@app.callback(
    Output("one_line_summary", 'data'),
    Output('one_line_summary', 'columns'),
    Output('selected_material', 'data'),  # Add this line
    Output('selected_confirmation', 'data'),  # Add this line
    Input("date-picker-range", 'start_date'),
    Input("date-picker-range", 'end_date'),
    Input('one_line_summary', 'selected_rows'),  # Add this line
    State('one_line_summary', 'data'),  # Add this line
    prevent_initial_call=True
)
def update_table_data(start_date, end_date, selected_rows, table_data):
    material_list = []

    for x in range(1, 7):
        machine = f"KMR-0{x}"
        time.sleep(1)

        data2 = ag.run_query(
            f"SELECT '{machine}' as MACHINE,MATERIAL,CONFIRMATION,MAX(OK) AS OK , (MAX(NOTOKGORSEL) +  MAX(NOTOKOLCUSEL)) AS TOTALNOTOK,MAX(NOTOKOLCUSEL) AS NOTOKOLCUSEL ,"
            f" MAX(NOTOKGORSEL) AS NOTOKGORSEL FROM  [dbo].[{machine}] "
            f" WHERE CAST(CURDATETIME AS DATE)  >= '{start_date}' AND CAST(CURDATETIME AS DATE)  < '{end_date}' "
            f" GROUP BY MATERIAL,CONFIRMATION"
            f" ORDER BY (MAX(NOTOKGORSEL) +  MAX(NOTOKOLCUSEL)) DESC")
        data2["MATERIAL"] = data2["MATERIAL"].apply(lambda x: x.split('\x00', 1)[0] if x else None)
        data2["CONFIRMATION"] = data2["CONFIRMATION"].astype(str)
        data2["MACHINE"] = data2["MACHINE"].astype(str)
        data2['OK'] = data2['OK'].astype(int)
        data2['TOTALNOTOK'] = data2['TOTALNOTOK'].astype(int)
        data2['NOTOKGORSEL'] = data2['NOTOKGORSEL'].astype(int)
        data2['NOTOKOLCUSEL'] = data2['NOTOKOLCUSEL'].astype(int)

        material_list.append(data2)

    final_result = pd.concat(material_list, ignore_index=True)
    final_result = final_result.sort_values(by=['TOTALNOTOK'], ascending=False)

    data = final_result.to_dict('records')
    columns = [{"name": i, "id": i} for i in final_result.columns]

    if selected_rows is not None and len(selected_rows) > 0:

        selected_material = table_data[selected_rows[0]]['MATERIAL']
        selected_confirmation = table_data[selected_rows[0]]['CONFIRMATION']

    else:
        selected_material = None
        selected_confirmation = None

    return data, columns, selected_material, selected_confirmation



##### bubble chart
@app.callback(
    Output('all_intervals_ic', 'columns'),
    Output('all_intervals_dis', 'columns'),
    Output("all_intervals_es", "columns"),
    Output("all_intervals_ic", 'data'),
    Output("all_intervals_dis", 'data'),
    Output("all_intervals_es", 'data'),
    Output("dist_plot1", "figure"),
    Output("dist_plot2", "figure"),
    Output("dist_plot3", "figure"),
    Input("selected_material", 'data'),  # Modify this line
    State("date-picker-range", 'start_date'),
    State("date-picker-range", 'end_date'),
    prevent_initial_call=True

)
def draw_dist_plot(material, start_date, end_date):
    # Function to scale the size of markers
    def scale_size(quantity, min_size=4, max_size=12):
        scaled_size = max(min_size, min(max_size, quantity))
        return scaled_size


    data = ag.run_query(f"SELECT * FROM VLFAYIKLAMA WHERE MATERIAL = '{material}' AND CURDATETIME >= '{start_date}' AND CURDATETIME < '{end_date}'")
    data["MATERIAL"] = data["MATERIAL"].astype(str)
    data["MATERIAL"] = data["MATERIAL"].apply(lambda x: x.split('\x00', 1)[0] if x else None)

    data = data.loc[data["MATERIAL"] == material]


    df_nom = ag.run_query(
        f"SELECT MATERIAL,[MTYPE],[MTYPENOM],[MTYPETOL] FROM [VLFKMRAYKTOL] WHERE MATERIAL = '{material}'")

    df_nom['MTYPENOM'] = df_nom['MTYPENOM'].astype(float)

    df_ic = df_nom.loc[df_nom["MTYPE"] == 'ICCAP']
    df_es = df_nom.loc[df_nom["MTYPE"] == 'ESMERKEZLILIK']
    df_dis = df_nom.loc[df_nom["MTYPE"] == 'DISCAP']

    data_ic = data.loc[data["MTYPE"] == 'ICCAP']
    data_es = data.loc[data["MTYPE"] == 'ESMERKEZLILIK']
    data_dis = data.loc[data["MTYPE"] == 'DISCAP']


    fig = go.Figure()
    fig1 = go.Figure()
    fig2 = go.Figure()


    list_of_data = []


    for figure, data_interval in [[fig, data_ic],
                                                [fig1, data_es],
                                                [fig2, data_dis]]:

        # data_interval = data_interval.merge(data_summary, on=["MATERIAL"], how='left')
        # # data_es = data_es.merge(df_es,on=["MATERIAL"], how='left')
        # # data_dis = data_dis.merge(df_dis,on=["MATERIAL"], how='left')
        #
        # data_interval['OKNOTOK'] = np.where(
        #     (data_interval['MAXIMUM'] > data_interval['MTYPENOM'] * 1.01) | (
        #                 data_interval['MINIMUM'] < data_interval['MTYPENOM'] * 0.99),
        #     'RED',
        #     'KABUL'
        # )
        data_interval.sort_values(by="MINIMUM", inplace=True)
        data_interval["MINIMUM"] = data_interval["MINIMUM"].astype(float).round(decimals=4)
        data_interval["MAXIMUM"] = data_interval["MAXIMUM"].astype(float).round(decimals=4)



        data_interval["midpoints"] = (data_interval["MINIMUM"] + data_interval["MAXIMUM"]) / 2

        # Loop through the data and add traces
        dtick_value = (data_interval["midpoints"].max() - data_interval["midpoints"].min()) / 20


        for i, row in data_interval.iterrows():
            if row["QUANTITY"] > 0:
                # marker_symbol = "circle" if row["OKNOTOK"] == "KABUL" else "circle-x"
                # row["QUANTITY"] = row["QUANTITY"] * 100 if row["OKNOTOK"] == 'RED' else row["QUANTITY"]
                # marker_size = scale_size(row["QUANTITY"])
                figure.add_trace(go.Bar(
                    x=[row["midpoints"]],
                    y=[row["QUANTITY"]],
                    marker=dict(
                        color='DarkOrange',
                        opacity=0.7,
                    )
                ))

        # Update layout and annotations as before
        figure.update_layout(
            showlegend=False,
            plot_bgcolor='FloralWhite',
            paper_bgcolor='FloralWhite',
            xaxis=dict(
                title='Midpoints',
                title_font=dict(size=20, family='Arial'),
                showgrid=True,  # Enable the x-axis grid
                gridcolor='rgba(255, 140, 0, 0.7)',  # Customize the grid color
                gridwidth=1,  # Customize the grid line width
                dtick=dtick_value,  # Adjust this value to control x-axis tick frequency
            ),
            yaxis=dict(
                title='KABUL-RED',
                title_font=dict(size=20, family='Arial'),
                type='log',
                showgrid=True,  # Enable the y-axis grid
                gridcolor='rgba(255, 140, 0, 0.7)',  # Customize the grid color
                gridwidth=1,  # Customize the grid line width
                # For logarithmic scale, you might leave dtick to auto-adjust or set it to a specific value
            ),
            # title=dict(text='İç Çap', y=0.95, font=dict(size=25, family='Arial')),
            legend=dict(x=0, y=1.1, traceorder="normal", orientation="h"),
            height=400,
            annotations=[
                dict(
                    text=f"Gözlem Sayısı : {data_interval['QUANTITY'].sum()}",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0,
                    y=1.15,
                    font=dict(size=16, family='Arial'),
                ),
                dict(
                    text="Tolerans Değeri : ?",  # Update with actual value if needed
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=1,
                    y=1.15,
                    font=dict(size=16, family='Arial'),
                )
            ]
        )

        data_interval = data_interval[["MINIMUM", "MAXIMUM", "QUANTITY"]]
        data_interval["OKNOTOK"] = 'NAN'
        list_of_data.append(data_interval)
    return [{"name": i, "id": i} for i in list_of_data[0].columns], [{"name": i, "id": i} for i in
                                                                     list_of_data[1].columns], \
        [{"name": i, "id": i} for i in list_of_data[2].columns], list_of_data[0].to_dict("records"), list_of_data[
        1].to_dict("records"), \
        list_of_data[2].to_dict("records"), fig, fig1, fig2


@app.callback(
    Output('production', 'data'),
    Output('production', 'columns'),
    Input('selected_confirmation', 'data'),
    prevent_initial_call=True
)
def update_production_data(confirmation):
    if not confirmation:
        return no_update, no_update

    print(f"DENEME2")
    print(confirmation)


    data4 = ag.run_query(
        f"SELECT C.WORKCENTER, (H.NAME + ' ' + H.SURNAME) AS NAME, CAST(C.CONFIRMDATE AS DATE) AS CONFDATE, C.OUTPUT," 
        f"(C.WORKINGTIME * 60) AS WORKINGTIME, I.TOOLNUM FROM [VALFSAN604].[dbo].IASPRDCONF C "
        f"LEFT JOIN [VALFSAN604].[dbo].IASHCMPERS H ON C.CLIENT = H.CLIENT AND C.PERSONELNUM = H.PERSID "
        f"LEFT JOIN [VALFSAN604].[dbo].IASPRDRST I ON C.CLIENT = I.CLIENT AND C.COMPANY = I.COMPANY AND C.PRDORDER = I.PRDORDER AND C.POTYPE = I.POTYPE "
        f"WHERE C.OUTPUT > 0 AND I.SEC = 1 AND C.COSTCENTER != 'SKURUTMA' AND C.PRDORDER = '{confirmation }'  ORDER BY C.CONFIRMATION, C.CONFIRMPOS")

    print(f"DENEME3")
    print(data4)

    data4["WORKCENTER"] = data4["WORKCENTER"].astype(str)
    data4["NAME"] = data4["NAME"].astype(str)
    data4['CONFDATE'] = pd.to_datetime(data4['CONFDATE']).dt.strftime('%Y-%m-%d')
    data4['OUTPUT'] = data4['OUTPUT'].astype(int)
    data4['WORKINGTIME'] = data4['WORKINGTIME'].astype(float)
    data4['TOOLNUM'] = data4['TOOLNUM'].astype(str)


    print(f"DENEME4")
    print(data4)

    columns = [{"name": i, "id": i} for i in data4.columns]
    return data4.to_dict('records'), columns