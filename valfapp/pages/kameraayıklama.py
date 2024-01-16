import pandas as pd
from dash import dcc, html, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from run.agent import agiot as ag
from valfapp.app import app
from datetime import date, timedelta, datetime
from config import kb
from dash_table import DataTable

data = ag.run_query(r"SELECT * FROM VLFAYIKLAMA")
data['MINIMUM'] = data['MINIMUM'].astype(float)
data['MAXIMUM'] = data['MAXIMUM'].astype(float)
data['QUANTITY'] = data['QUANTITY'].astype(int)
data["midpoints"] = (data['MINIMUM'] + data['MAXIMUM']) / 2
data["MATERIAL"] = data["MATERIAL"].apply(lambda x: x.split('\x00', 1)[0])
data["CURDATETIME"] = pd.to_datetime(data["CURDATETIME"]).dt.strftime('%Y-%m-%d %H:%M:%S')
data["CURDATETIME"] = pd.to_datetime(data["CURDATETIME"]).dt.date


data = data.to_json(date_format='iso', orient='split')

data2 = ag.run_query(r"SELECT MATERIAL,CONFIRMATION,MAX(OK) AS OK , MAX(NOTOKGORSEL) AS NOTOKGORSEL , MAX(NOTOKOLCUSEL) AS NOTOKOLCUSEL FROM  [dbo].[KMR-02]  GROUP BY MATERIAL,CONFIRMATION")
data2["MATERIAL"] = data2["MATERIAL"].apply(lambda x: x.split('\x00', 1)[0])
data2["CONFIRMATION"] = data2["CONFIRMATION"].astype(str)
data2['OK'] = data2['OK'].astype(int)
data2['NOTOKGORSEL'] = data2['NOTOKGORSEL'].astype(int)
data2['NOTOKOLCUSEL'] = data2['NOTOKOLCUSEL'].astype(int)

print(data2)
data2 = data2.to_json(date_format='iso', orient='split')


layout = [
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
                     options=['KMR-1','KMR-2','KMR-3','KMR-4','KMR-5','KMR-6'],
                     multi=False,
                     value='Makinalar',
                     ),
        dcc.Dropdown(id="material_ayk",
                     className='dropdown-style',
                     options=[3, 4, 5],
                     multi=False,
                     value='Burası',
                     ),

    ],style={'display': 'flex', 'flexDirection': 'row'})
    ),
    dbc.Row([
        dbc.Col(width= 0.5),
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
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold',
                    'border': 'thin lightgrey solid',
                }
            ),
        ]),
    ]),

    dbc.Row([

        dbc.Col(width=2),
        dbc.Col([
            html.H3("Ölçüm Bilgileri"),
            DataTable(
                id='datatable',
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
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold',
                    'border': 'thin lightgrey solid',
                }

            ),
        ]),
    ]),

    dbc.Col([dcc.Graph(id="dist_plot1")]),
    dbc.Col([dcc.Graph(id="dist_plot2")]),
    dbc.Col([dcc.Graph(id="dist_plot3")]),

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
    print("**********")
    print(data["CURDATETIME"].dtype)
    print(data["CURDATETIME"])
    print("**********")

    data["MACHINE"] = data["MACHINE"]

    data = data.to_json(date_format='iso', orient='split')

    return data


@app.callback(
    Output("material_ayk", 'options'),
    State("ayıklama_data", 'data'),
    Input ("machine_ayk", 'value'),
    Input ("date-picker_ayk" , 'date')
)
def material_data(data,value,n):
    print(f" VERİ KONTROLÜ")

    print(n)
    print(value)

    data = pd.read_json(data, orient='split')
    print(f" datam var {data} asdasdasdasd  tarihhhhh")

    ##a_formatted = a_date.dt.strftime('%Y-%m-%d')
    ##print(a_formatted)
    ##print(f" SONNNN")
    print(data["MACHINE"])
    ##print(len(data["MACHINE"].iloc[0]))


    data["MACHINE"] = data["MACHINE"].astype(str)

    filtered_data = data.loc[(data["CURDATETIME"] == n) & (data["MACHINE"] == value)]

    ##print(len(data["MATERIAL"].iloc[0]))

    material_list = list(filtered_data["MATERIAL"].unique())


    return  material_list

@app.callback(
    Output("datatable", 'data'),
    Input("material_ayk", "value"),
    State("ayıklama_data", 'data'),

)
def update_table_data(material,data):
    data2 = ag.run_query(r"SELECT MATERIAL,CONFIRMATION,MAX(OK) AS OK , MAX(NOTOKGORSEL) AS NOTOKGORSEL , MAX(NOTOKOLCUSEL) AS NOTOKOLCUSEL FROM  [dbo].[KMR-02]  GROUP BY MATERIAL,CONFIRMATION")
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
    return  table_data



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

    # Scatter chart for 'ICCAP'

    fig = go.Figure()
    marker_size = data_ic["QUANTITY"] * 0.1
    fig.add_trace(go.Scatter(
        x=data_ic["midpoints"],
        y=data_ic["QUANTITY"],
        mode='markers',
        marker=dict(
            size=marker_size,
            sizemode='diameter',
            sizeref=0.3,
            opacity=0.3,
        ),
        name='ICCAP',
    ))

    fig.update_layout(
        xaxis=dict(tickmode='auto', title='Midpoints', title_font=dict(size=20, family='Arial')),
        yaxis=dict(tickmode='auto', title='Quantity', title_font=dict(size=20, family='Arial')),
        title=dict(text='İç Çap', y=0.95, font=dict(size=25, family='Arial')),
        legend=dict(x=0, y=1.1, traceorder="normal", orientation="h"),
        height=500
    )

    fig.update_layout(
        annotations=[
            dict(
                text=f"Gözlem Sayısı : {data_ic['QUANTITY'].sum()}",
                showarrow=False,
                xref="paper",
                yref="paper",
                x=0,
                y=1.15,
                font=dict(size=16, family='Arial'),
            ),
            dict(
                text=f"Tolerans Değeri : ?",
                showarrow=False,    
                xref="paper",
                yref="paper",
                x=1,
                y=1.15,
                font=dict(size=16, family='Arial'),
            )
        ]
    )

    fig2 = go.Figure()
    marker_size = data_dıs["QUANTITY"] * 0.1

    fig2.add_trace(go.Scatter(
        x=data_dıs["midpoints"],
        y=data_dıs["QUANTITY"],
        mode='markers',
        marker=dict(
            size=marker_size,
            sizemode='diameter',
            sizeref=0.3,
            opacity=0.7,
        ),
        name='DISCAP',
    ))

    fig2.update_layout(
        xaxis=dict(tickmode='auto', title='Midpoints', title_font=dict(size=20, family='Arial')),
        yaxis=dict(tickmode='auto', title='Quantity', title_font=dict(size=20, family='Arial')),
        title=dict(text='Dış Çap', y=0.95, font=dict(size=25, family='Arial')),
        legend=dict(x=0, y=1.1, traceorder="normal", orientation="h"),
        height = 500
    )


    fig3 = go.Figure()

    '''
    if data_es["QUANTITY"] > 100 :
        marker_size = data_es["QUANTITY"] * 0.01
    else :
        marker_size = data_es["QUANTITY"]
    '''
    marker_size = data_es["QUANTITY"].apply(lambda x: x * 0.03 if x > 2000 else x * 0.6 )

    ##marker_size = data_es["QUANTITY"]
    fig3.add_trace(go.Scatter(
        x=data_es["midpoints"],
        y=data_es["QUANTITY"],
        mode='markers',
        marker=dict(
            size = marker_size,
            sizemode='diameter',
            sizeref=0.3,
            opacity=0.1,
        ),
        name='ESMERKEZLILIK',
    ))

    fig3.update_layout(
        autosize=True,
        xaxis=dict(tickmode='auto', title='Midpoints', title_font=dict(size=20, family='Arial')),
        yaxis=dict(tickmode='auto', title='Quantity', title_font=dict(size=20, family='Arial')),
        title=dict(text='Eş Merkezlilik', y=0.95, font=dict(size=25, family='Arial')),
        legend=dict(x=0, y=1.1, traceorder="normal", orientation="h"),
        height = 500,
    )

    return fig, fig2, fig3
