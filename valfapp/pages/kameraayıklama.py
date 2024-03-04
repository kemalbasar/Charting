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

from valfapp.layouts import nav_bar

data = ag.run_query(r"SELECT * FROM VLFAYIKLAMA")
data['MINIMUM'] = data['MINIMUM'].astype(float)
data['MAXIMUM'] = data['MAXIMUM'].astype(float)
data['QUANTITY'] = data['QUANTITY'].astype(int)
data["midpoints"] = (data['MINIMUM'] + data['MAXIMUM']) / 2
data["MATERIAL"] = data["MATERIAL"].apply(lambda x: x.split('\x00', 1)[0])
data["CURDATETIME"] = pd.to_datetime(data["CURDATETIME"]).dt.strftime('%Y-%m-%d %H:%M:%S')
data["CURDATETIME"] = pd.to_datetime(data["CURDATETIME"]).dt.date

data = data.to_json(date_format='iso', orient='split')

data2 = ag.run_query(
    r"SELECT MATERIAL,CONFIRMATION,MAX(OK) AS OK , MAX(NOTOKGORSEL) AS NOTOKGORSEL , MAX(NOTOKOLCUSEL) AS NOTOKOLCUSEL FROM  [dbo].[KMR-02]  GROUP BY MATERIAL,CONFIRMATION")
data2["MATERIAL"] = data2["MATERIAL"].apply(lambda x: x.split('\x00', 1)[0])
data2["CONFIRMATION"] = data2["CONFIRMATION"].astype(str)
data2['OK'] = data2['OK'].astype(int)
data2['NOTOKGORSEL'] = data2['NOTOKGORSEL'].astype(int)
data2['NOTOKOLCUSEL'] = data2['NOTOKOLCUSEL'].astype(int)

data2 = data2.to_json(date_format='iso', orient='split')

layout = [
    nav_bar,
    dcc.Store(id='ayıklama_data',
              data=data),
    dbc.Row([html.H1("Ayıklama Robotu Kalite Sonuçları",
                     style={'text-align': 'center', "fontFamily": 'Arial Black', 'fontSize': 30,
                            'backgroundColor': '#f0f0f0'})])
    ,

    dbc.Row(html.Div(children=[
        dcc.DatePickerSingle(id='date-picker_ayk', className="dash-date-picker",
                             date=date.today() + timedelta(days=-kb),
                             persistence=True,
                             persistence_type='memory'
                             ),

        dcc.Dropdown(id="machine_ayk",
                     className='dropdown-style',
                     options=['KMR-01', 'KMR-02', 'KMR-03', 'KMR-04', 'KMR-05', 'KMR-06'],
                     multi=False,
                     value='Makinalar',
                     ),
        dcc.Dropdown(id="material_ayk",
                     className='dropdown-style',
                     options=[3, 4, 5],
                     multi=False,
                     value='Burası',
                     ),

    ], style={'display': 'flex', 'flexDirection': 'row', "margin-left": 75})
    ),
    dbc.Row([
        dbc.Col([
            html.H3("PPM Değeri"),
            DataTable(
                id='ppmtable',
                columns=[
                    {'name': 'PPM', 'id': 'ppm'},
                ],
                style_table={
                    'height': '70px',
                    'overflowY': 'auto',
                    'border': 'thin lightgrey solid',
                    'fontFamily': 'Arial, sans-serif',
                    'minWidth': '5%',  # Adjust this value to set the minimum width
                    'width': '10%',  # Adjust this value to set the width
                    'textAlign': 'center',
                    'color': 'black'

                },
                style_header={
                    'backgroundColor': 'rgba(0, 0, 0, 0)',  # Semi-transparent background
                    'fontWeight': 'bold',  # Bold font
                    'color': '#2F4F4F',  # Cool text color
                    'fontFamily': 'Arial, sans-serif',  # Font family
                    'fontSize': '16px',
                    'border': '1px dotted brown',
                    'borderRadius': '2px'
                    # Font size
                }
            ),
        ], width=3),

        dbc.Col([
            html.H3("Özet", style={"align": "center"}),
            DataTable(
                id='one_line_summary',
                columns=[
                    {'name': 'MATERIAL', 'id': 'MATERIAL'},
                    {'name': 'CONFIRMATION', 'id': 'CONFIRMATION'},
                    {'name': 'OK', 'id': 'OK'},
                    {'name': 'NOTOKGORSEL', 'id': 'NOTOKGORSEL'},
                    {'name': 'NOTOKOLCUSEL', 'id': 'NOTOKOLCUSEL'},
                ],
                style_table={
                    'height': '100px',
                    'overflowY': 'auto',
                    'border': 'thin lightgrey solid',
                    'fontFamily': 'Arial, sans-serif',
                    'minWidth': '70%',  # Adjust this value to set the minimum width
                    'width': '80%',  # Adjust this value to set the width
                    'textAlign': 'center',
                    'color':'black'
                },
                style_header={
                    'backgroundColor': 'rgba(0, 0, 0, 0)',  # Semi-transparent background
                    'fontWeight': 'bold',  # Bold font
                    'color': '#2F4F4F',  # Cool text color
                    'fontFamily': 'Arial, sans-serif',  # Font family
                    'fontSize': '16px',
                    'border': '1px dotted brown',
                    'borderRadius': '2px'
                    # Font size
                }

            ),
        ], width=8),
    ], style={"margin-left": 75}),

    dbc.Row([
        dbc.Col([
            html.H3("Ölçüm Bilgileri"),
            html.Div(DataTable(
                id='all_intervals_ic',
                columns=[
                    {'name': 'MATERIAL', 'id': 'MATERIAL'},
                    {'name': 'CONFIRMATION', 'id': 'CONFIRMATION'},
                    {'name': 'OK', 'id': 'OK'},
                    {'name': 'NOTOKGORSEL', 'id': 'NOTOKGORSEL'},
                    {'name': 'NOTOKOLCUSEL', 'id': 'NOTOKOLCUSEL'},
                ],
                style_table={
                    'height': '300px',
                    'overflowY': 'auto',
                    'border': 'thin lightgrey solid',
                    'fontFamily': 'Arial, sans-serif',
                    'minWidth': '70%',  # Adjust this value to set the minimum width
                    'width': '80%',  # Adjust this value to set the width
                    'textAlign': 'center',
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',  # Semi-transparent background
                    'fontWeight': 'bold',  # Bold font
                    'color': '#2F4F4F',  # Cool text color
                    'fontFamily': 'Arial, sans-serif',  # Font family
                    'fontSize': '16px',
                    'border': '1px dotted brown',
                    'borderRadius': '2px'
                    # Font size
                },

                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    }
                ],
                style_cell={
                        "textAlign": "center",
                        "padding": "10px",
                        "color": "black",
                        'max-width': 115

                    }


            ), style={"margin-top": 100}),

            html.Div(DataTable(
                id='all_intervals_dis',
                columns=[
                    {'name': 'MATERIAL', 'id': 'MATERIAL'},
                    {'name': 'CONFIRMATION', 'id': 'CONFIRMATION'},
                    {'name': 'OK', 'id': 'OK'},
                    {'name': 'NOTOKGORSEL', 'id': 'NOTOKGORSEL'},
                    {'name': 'NOTOKOLCUSEL', 'id': 'NOTOKOLCUSEL'},
                ],
                style_table={
                    'height': '300px',
                    'overflowY': 'auto',
                    'border': 'thin lightgrey solid',
                    'fontFamily': 'Arial, sans-serif',
                    'minWidth': '70%',  # Adjust this value to set the minimum width
                    'width': '80%',  # Adjust this value to set the width
                    'textAlign': 'center',
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',  # Semi-transparent background
                    'fontWeight': 'bold',  # Bold font
                    'color': '#2F4F4F',  # Cool text color
                    'fontFamily': 'Arial, sans-serif',  # Font family
                    'fontSize': '16px',
                    'border': '1px dotted brown',
                    'borderRadius': '2px'
                    # Font size
                },

                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    }
                ],
                style_cell={
                    "textAlign": "center",
                    "padding": "10px",
                    "color": "black",
                    'max-width': 115

                }

            ), style={"margin-top": 95}),

            html.Div(DataTable(
                id='all_intervals_es',
                columns=[
                    {'name': 'MATERIAL', 'id': 'MATERIAL'},
                    {'name': 'CONFIRMATION', 'id': 'CONFIRMATION'},
                    {'name': 'OK', 'id': 'OK'},
                    {'name': 'NOTOKGORSEL', 'id': 'NOTOKGORSEL'},
                    {'name': 'NOTOKOLCUSEL', 'id': 'NOTOKOLCUSEL'},
                ],
                style_table={
                    'height': '300px',
                    'overflowY': 'auto',
                    'border': 'thin lightgrey solid',
                    'fontFamily': 'Arial, sans-serif',
                    'minWidth': '70%',  # Adjust this value to set the minimum width
                    'width': '80%',  # Adjust this value to set the width
                    'textAlign': 'center',
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',  # Semi-transparent background
                    'fontWeight': 'bold',  # Bold font
                    'color': '#2F4F4F',  # Cool text color
                    'fontFamily': 'Arial, sans-serif',  # Font family
                    'fontSize': '16px',
                    'border': '1px dotted brown',
                    'borderRadius': '2px'
                    # Font size
                },

                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    }
                ],
                style_cell={
                    "textAlign": "center",
                    "padding": "10px",
                    "color": "black",
                    'max-width': 115

                }

            ), style={"margin-top": 80})
        ], width=3),

        dbc.Col([dcc.Graph(id="dist_plot1", style={"margin-top": 70}),
                 dcc.Graph(id="dist_plot2", style={"margin-top": 50}),
                 dcc.Graph(id="dist_plot3", style={"margin-top": 20})], width=8)
    ], style={"margin-left": 75}),

    dcc.Interval(id="data_refresh", interval=1000000)

]


@app.callback(
    Output("ayıklama_data", 'data'),
    Input("data_refresh", 'n_interval'),
)
def store_data(n):
    data = ag.run_query(r"SELECT * FROM VLFAYIKLAMA ")
    data['MINIMUM'] = data['MINIMUM'].astype(float)
    data['MAXIMUM'] = data['MAXIMUM'].astype(float)
    data['QUANTITY'] = data['QUANTITY'].astype(int)
    data["midpoints"] = (data['MINIMUM'] + data['MAXIMUM']) / 2
    data["MATERIAL"] = data["MATERIAL"].apply(lambda x: x.split('\x00', 1)[0])
    ##data["CURDATETIME"] = data["CURDATETIME"].str.strip()
    data["CURDATETIME"] = pd.to_datetime(data["CURDATETIME"]).dt.strftime('%Y-%m-%d')
    data["MACHINE"] = data["MACHINE"]

    data = data.to_json(date_format='iso', orient='split')

    return data


@app.callback(
    Output("material_ayk", 'options'),
    State("ayıklama_data", 'data'),
    Input("machine_ayk", 'value'),
    Input("date-picker_ayk", 'date')
)
def material_data(data, value, n):
    data = pd.read_json(data, orient='split')
    data["MACHINE"] = data["MACHINE"].astype(str)
    filtered_data = data.loc[(data["CURDATETIME"] == n) & (data["MACHINE"] == value)]
    material_list = list(filtered_data["MATERIAL"].unique())
    return material_list


@app.callback(
    Output("one_line_summary", 'data'),
    Output('one_line_summary', 'columns'),
    Output("ppmtable", 'data'),
    Output('ppmtable', 'columns'),
    Input("machine_ayk", 'value'),
    State("ayıklama_data", 'data'),
    State("date-picker_ayk",'date'),
    prevent_initial_call=True

)
def update_table_data(machine, data,selected_date):
    print(f"burayım {selected_date}")
    if not machine == 'Makinalar':
        data2 = ag.run_query(
            f"SELECT MATERIAL,CONFIRMATION,MAX(OK) AS OK , MAX(NOTOKGORSEL) AS NOTOKGORSEL , MAX(NOTOKOLCUSEL) AS NOTOKOLCUSEL FROM  [dbo].[{machine}]  GROUP BY MATERIAL,CONFIRMATION")
        data2["MATERIAL"] = data2["MATERIAL"].apply(lambda x: x.split('\x00', 1)[0])
        data2["CONFIRMATION"] = data2["CONFIRMATION"].astype(str)
        data2['OK'] = data2['OK'].astype(int)
        data2['NOTOKGORSEL'] = data2['NOTOKGORSEL'].astype(int)
        data2['NOTOKOLCUSEL'] = data2['NOTOKOLCUSEL'].astype(int)

        data = pd.read_json(data, orient='split')
        data = data.loc[data["MATERIAL"] == material]
        data["MATERIAL"] = data["MATERIAL"].astype(str)
        selected_material = data["MATERIAL"].unique()
        filtered_data2 = data2[data2["MATERIAL"].isin(selected_material)]

        table_data = filtered_data2.to_dict('records')
        return table_data,[{"name": i, "id": i} for i in filtered_data2.columns]
    else:
        no_update


### line chart
'''
@app.callback(
    Output(component_id="dist_plot1", component_property="figure"),
    Output(component_id="dist_plot2", component_property="figure"),
    Output(component_id="dist_plot3", component_property="figure"),
    Input("material_ayk", "value"),
    State("ayıklama_data", "data"),
)
def draw_dist_plot(material, data):
    data = pd.read_json(data, orient='split')
    data = data.loc[data["MATERIAL"] == material]
    data["MATERIAL"] = data["MATERIAL"].astype(str)

    data_ic = data.loc[data["MTYPE"] == 'ICCAP']
    data_es = data.loc[data["MTYPE"] == 'ESMERKEZLILIK']
    data_dıs = data.loc[data["MTYPE"] == 'DISCAP']

    # Line chart for 'ICCAP'
    line_ic = go.Figure()

    line_ic.add_trace(go.Scatter(
        x=data_ic["midpoints"],
        y=data_ic["QUANTITY"],
        mode='lines+markers',
        line=dict(color='blue'),
        marker=dict(color='blue'),
        name='ICCAP',
    ))

    line_ic.update_layout(
        xaxis=dict(title='Ölçümler', title_font=dict(size=20, family='Arial')),
        yaxis=dict(title='Adet', title_font=dict(size=20, family='Arial')),
        title=dict(text='İç Çap Line Chart', y=0.95, font=dict(size=25, family='Arial')),
    )

    line_dis = go.Figure()

    line_dis.add_trace(go.Scatter(
        x=data_dıs["midpoints"],
        y=data_dıs["QUANTITY"],
        mode='lines+markers',
        line=dict(color='red'),
        marker=dict(color='red'),
        name='DISCAP',
    ))

    line_dis.update_layout(
        xaxis=dict(title='Ölçümler', title_font=dict(size=20, family='Arial')),
        yaxis=dict(title='Adet', title_font=dict(size=20, family='Arial')),
        title=dict(text='Dış Çap Line Chart', y=0.95, font=dict(size=25, family='Arial')),
    )


    line_es = go.Figure()

    line_es.add_trace(go.Scatter(
        x=data_es["midpoints"],
        y=data_es["QUANTITY"],
        mode='lines+markers',
        line=dict(color='green'),
        marker=dict(color='green'),
        name='ESMERKEZLILIK',
    ))

    line_es.update_layout(
        xaxis=dict(title='Ölçümler', title_font=dict(size=20, family='Arial')),
        yaxis=dict(title='Adet', title_font=dict(size=20, family='Arial')),
        title=dict(text='Eş Merkezlilik Line Chart', y=0.95, font=dict(size=25, family='Arial')),
    )

    return line_ic, line_dis, line_es
'''


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
    Input("material_ayk", "value"),
    State("ayıklama_data", "data"),
    prevent_initial_call=True

)
def draw_dist_plot(material, data):
    # Function to scale the size of markers
    def scale_size(quantity, min_size=4, max_size=12):
        scaled_size = max(min_size, min(max_size, quantity))
        return scaled_size

    data = pd.read_json(data, orient='split')
    data = data.loc[data["MATERIAL"] == material]
    data["MATERIAL"] = data["MATERIAL"].astype(str)
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

    for figure, data_interval, data_summary in [[fig, data_ic, df_ic],
                                                [fig1, data_es, df_es],
                                                [fig2, data_dis, df_dis]]:

        data_interval = data_interval.merge(data_summary, on=["MATERIAL"], how='left')
        # data_es = data_es.merge(df_es,on=["MATERIAL"], how='left')
        # data_dis = data_dis.merge(df_dis,on=["MATERIAL"], how='left')

        data_interval['OKNOTOK'] = np.where(
            (data_interval['MAXIMUM'] > data_interval['MTYPENOM'] * 1.01) | (
                        data_interval['MINIMUM'] < data_interval['MTYPENOM'] * 0.99),
            'RED',
            'KABUL'
        )

        data_interval.sort_values(by="MINIMUM", inplace=True)

        # Loop through the data and add traces
        dtick_value = (data_interval["midpoints"].max() - data_interval["midpoints"].min()) / 20

        for i, row in data_interval.iterrows():
            if row["QUANTITY"] > 0:
                marker_symbol = "circle" if row["OKNOTOK"] == "KABUL" else "circle-x"
                row["QUANTITY"] = row["QUANTITY"] * 100 if row["OKNOTOK"] == 'RED' else row["QUANTITY"]
                marker_size = scale_size(row["QUANTITY"])
                figure.add_trace(go.Scatter(
                    x=[row["midpoints"]],
                    y=[row["OKNOTOK"]],
                    mode='markers',
                    marker=dict(
                        size=marker_size,
                        symbol=marker_symbol,
                        sizemode='diameter',
                        sizeref=0.3,
                        opacity=0.7,
                    )
                ))

        # Update layout and annotations as before
        figure.update_layout(
            showlegend=False,
            plot_bgcolor='FloralWhite',
            xaxis=dict(autorange='reversed', title='Midpoints', title_font=dict(size=20, family='Arial'),
                       dtick=dtick_value),
            yaxis=dict(title='KABUL-RED', title_font=dict(size=20, family='Arial'), type='category'),
            title=dict(text='İç Çap', y=0.95, font=dict(size=25, family='Arial')),
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

        data_interval = data_interval[["MINIMUM", "MAXIMUM", "QUANTITY", "MTYPENOM", "MTYPETOL", "OKNOTOK"]]
        list_of_data.append(data_interval)
    return [{"name": i, "id": i} for i in list_of_data[0].columns], [{"name": i, "id": i} for i in
                                                                     list_of_data[1].columns], \
        [{"name": i, "id": i} for i in list_of_data[2].columns], list_of_data[0].to_dict("records"), list_of_data[
        1].to_dict("records"), \
        list_of_data[2].to_dict("records"), fig, fig1, fig2
