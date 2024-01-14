import pandas as pd
from dash import dcc, html, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from run.agent import agiot as ag
from valfapp.app import app
from datetime import date, timedelta, datetime
from config import kb

data = ag.run_query(r"SELECT * FROM VLFAYIKLAMA")
data['MINIMUM'] = data['MINIMUM'].astype(float)
data['MAXIMUM'] = data['MAXIMUM'].astype(float)
data['QUANTITY'] = data['QUANTITY'].astype(int)
data["midpoints"] = (data['MINIMUM'] + data['MAXIMUM']) / 2
data["MATERIAL"] = data["MATERIAL"].apply(lambda x: x.split('\x00', 1)[0])
data["CURDATETIME"] = pd.to_datetime(data["CURDATETIME"]).dt.strftime('%Y-%m-%d %H:%M:%S')
data["CURDATETIME"] = pd.to_datetime(data["CURDATETIME"]).dt.date


data = data.to_json(date_format='iso', orient='split')

data2 = ag.run_query(r"SELECT MATERIAL,CONFIRMATION,MAX(OK) AS OK , MAX(NOTOKGORSEL) AS NOTOKGORSEL , MAX(NOTOKOLCUSEL) AS NOTOKOLCUSEL FROM  [dbo].[KMR-03]  GROUP BY MATERIAL,CONFIRMATION")
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

    print(f" MINIMUM DEGER VAR r {data} cvbcvbcvbcvbcvb")


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
    print(data["MACHINE"] )
    print(len(data["MACHINE"].iloc[0]))


    data["MACHINE"] = data["MACHINE"].astype(str)

    filtered_data = data.loc[(data["CURDATETIME"] == n) & (data["MACHINE"] == value)]
    print(f" data var cvbcvbcvbcvbcvb")
    print(filtered_data)

    print(len(data["MATERIAL"].iloc[0]))

    material_list = list(filtered_data["MATERIAL"].unique())

    print(material_list)

    print( f"material listim {material_list}")
    print(data["MATERIAL"])

    return  material_list


@app.callback(
    Output(component_id="dist_plot1", component_property="figure"),
    Output(component_id="dist_plot2", component_property="figure"),
    Output(component_id="dist_plot3", component_property="figure"),
    Input("material_ayk", "value"),
    State("ayıklama_data", "data"),
)



def draw_dist_plot(material,data):

    data = pd.read_json(data, orient='split')
    data = data.loc[data["MATERIAL"] == material]
    data["MATERIAL"] = data["MATERIAL"].astype(str)

    # Group by 'ÖlçümTipi' and calculate the sum of 'Miktar' for each group
    # grouped_data = data.groupby('ÖlçümTipi')['Miktar'].sum().reset_index()

    data_ic = data.loc[data["MTYPE"] == 'ICCAP']
    row_data_ic = len(data_ic)
    data_es = data.loc[data["MTYPE"] == 'ESMERKEZLILIK']
    row_data_es = len(data_es)
    data_dıs = data.loc[data["MTYPE"] == 'DISCAP']
    row_data_dıs = len(data_dıs)

    fig = go.Figure()
    # Iterate through each row in the dataframe to add bars to the plot
    # For each range, add a bar to the plot
    fig.add_trace(go.Bar(
        x=list(data_ic["midpoints"]),  # Use the midpoint of the range as the x-value
        y=list(data_ic["QUANTITY"])
    ))


    fig.update_layout(
        margin=dict(l=500, r=0, t=0, b=0),

        xaxis=dict(tickmode='auto',
                                  title='Ölçümler',
                                 title_font=dict(size=20, family='Arial')
                                  ##dtick=0.06
                                  ),
                       yaxis=dict(tickmode='auto',
                                  title='Adet',
                                  title_font=dict(size=20, family='Arial')
                                  ),
                       title=dict(text='İç Çap', y=0.95, font=dict(size=25, family='Arial')),
                      )
    fig.update_layout(barmode='group')

    ##max_x = max(data_ic["midpoints"])
    ##max_y = max(data_ic["QUANTITY"])

    fig.update_layout(
    annotations=[
        dict(
            text=f"Gözlem Sayısı: {data_ic['QUANTITY'].sum()}",
            showarrow=False,
            xref="paper",
            yref="paper",
            x=0,
            y=1.1,
            font=dict(size=20, family='Arial'),

        ),
        dict(
            text=f"Tolerans Değeri : ?",
            showarrow=False,
            xref="paper",
            yref="paper",
            x=1,
            y=1.1,
            font=dict(size=20, family='Arial'),
        )
    ]
)


    fig2 = go.Figure()
    # Iterate through each row in the dataframe to add bars to the plot
    # For each range, add a bar to the plot
    fig2.add_trace(go.Bar(
        x=list(data_dıs["midpoints"]),  # Use the midpoint of the range as the x-value
        y=list(data_dıs["QUANTITY"])
    ))

    fig2.update_layout(xaxis=dict(tickmode='auto',
                                  title='Ölçümler',
                                  title_font=dict(size=20, family='Arial')
                                  ##dtick=0.06
                                  ),
                       yaxis=dict(tickmode='auto',
                                  title='Adet',
                                  title_font=dict(size=20, family='Arial')
                                  ),
                       title=dict(text='Dış Çap', y=0.95, font=dict(size=25, family='Arial')),

                       )
    fig2.update_layout(barmode='stack')


    fig3 = go.Figure()
    # Iterate through each row in the dataframe to add bars to the plot
    # For each range, add a bar to the plot
    fig3.add_trace(go.Bar(
        x=list(data_es["midpoints"]),  # Use the midpoint of the range as the x-value
        y=list(data_es["QUANTITY"])
    ))

    fig3.update_layout(xaxis=dict(tickmode='auto',
                                  title='Ölçümler',
                                  title_font=dict(size=20, family='Arial')
                                  ##dtick=0.06
                                  ),
                       yaxis=dict(tickmode='auto',
                                  title='Adet',
                                  title_font=dict(size=20, family='Arial')
                                  ),
                       title=dict(text='Eş Merkezlilik', y=0.95, font=dict(size=25, family='Arial'))
                       )
    fig3.update_layout(barmode='stack')

    return fig,fig2,fig3
