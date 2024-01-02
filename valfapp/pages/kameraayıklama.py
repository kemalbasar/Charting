import pandas as pd
from dash import dcc, html, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from run.agent import agiot as ag
from valfapp.app import app
from datetime import date, timedelta, datetime
from config import kb

data = ag.run_query(r"SELECT * FROM VLFAYIKLAMA WHERE ÖlçümTipi = 'İç Çap' OR ÖlçümTipi = 'Eş Merkezlilik'")
data['MinimumDeğer'] = data['MinimumDeğer'].astype(float)
data['MaksimumDeğer'] = data['MaksimumDeğer'].astype(float)
data['Miktar'] = data['Miktar'].astype(int)
data["midpoints"] = (data['MinimumDeğer'] + data['MaksimumDeğer']) / 2
data["Malzeme"] = data["Malzeme"].apply(lambda x: x.split('\x00', 1)[0])
data = data.to_json(date_format='iso', orient='split')

layout = [
    dcc.Store(id='ayıklama_data',
              data=data),
    dbc.Row([html.H1("Ayıklama Robotu Kalite Sonuçları",
                     style={'text-align': 'center', "fontFamily": 'Arial Black', 'fontSize': 30,
                            'backgroundColor': '#f0f0f0'})])
    ,
    dbc.Row(html.Div(children=[
        dcc.Dropdown(id="material_ayk",
                     className='dropdown-style',
                     options=[3, 4, 5],
                     multi=False,
                     value='Burası',
                     )
        , html.Button(id="search_button", name='Search', className="dash-empty-button"),
        dcc.DatePickerSingle(id='date-picker_ayk', className="dash-date-picker",
                             date=date.today() + timedelta(days=-kb),
                             persistence=True,
                             persistence_type='memory'
                             )
        , dcc.Dropdown(id="machine_ayk",
                     className='dropdown-style',
                     options=['KMR-1','KMR-2','KMR-3','KMR-4','KMR-5','KMR-6'],
                     multi=False,
                     value='Makinalar',
                     )
    ])
    ),

    dbc.Col([dcc.Graph(id="dist_plot1")]),
    dbc.Col([dcc.Graph(id="dist_plot2")]),
    dcc.Interval(id="data_refresh", interval=1000000)

]


@app.callback(
    Output("ayıklama_data", 'data'),
    Input("data_refresh", 'n_interval'),
)
def store_data(n):
    data = ag.run_query(r"SELECT * FROM VLFAYIKLAMA WHERE ÖlçümTipi = 'İç Çap' OR ÖlçümTipi = 'Eş Merkezlilik'")
    data['MinimumDeğer'] = data['MinimumDeğer'].astype(float)
    data['MaksimumDeğer'] = data['MaksimumDeğer'].astype(float)
    data['Miktar'] = data['Miktar'].astype(int)
    data["midpoints"] = (data['MinimumDeğer'] + data['MaksimumDeğer']) / 2
    data["Malzeme"] = data["Malzeme"].apply(lambda x: x.split('\x00', 1)[0])
    data["Tarih"] = data["Tarih"].apply(lambda x: x.split(' ', 1)[0])
    data["MakinaNo"] = data["MakinaNo"].apply(lambda x: x.split(' ', 1)[0])

    data = data.to_json(date_format='iso', orient='split')
    return data


@app.callback(
    Output("material_ayk", 'options'),
    State("ayıklama_data", 'data'),
    Input ("machine_ayk", 'value'),
    Input ("date-picker_ayk" , 'date')
)
def material_data(data,value,n):
    data = pd.read_json(data, orient='split')
    print(f" datam var {data} asdasdasdasd")

    a_date = data["Tarih"]
    a_date = a_date.str.strip()
    a_date = a_date[a_date != '']
    a_date = pd.to_datetime(a_date, format='%m/%d/%Y', errors='coerce')
    a_formatted = a_date.dt.strftime('%Y-%m-%d')

    data["Tarih"] = a_formatted
    data["MakinaNo"] = data["MakinaNo"].astype(str)
    ##data["MakinaNo"] = list(data["MakinaNo"].unique())

    ##print(f" makineler {m_ayk} makinalar")

    ##data = data.loc[data["Tarih"] == n]
    ##data = data.loc[m_ayk == value]
    filtered_data = data.loc[(data["Tarih"] == n) & (data["MakinaNo"] == value)]
    material_list = list(filtered_data["Malzeme"].unique())

    ##material_list = list(data["Malzeme"].unique())

    data["Malzeme"] = data["Malzeme"].astype(str)
    print(f" data var {data} cvbcvbcvbcvbcvb")

    return  material_list


@app.callback(
    Output(component_id="dist_plot1", component_property="figure"),
    Output(component_id="dist_plot2", component_property="figure"),
    Input("material_ayk", "value"),
    State("ayıklama_data", "data"),
)

def draw_dist_plot(material,data):

    data = pd.read_json(data, orient='split')


    data = data.loc[data["Malzeme"] == material]

    data["Malzeme"] = data["Malzeme"].astype(str)



    data_ic = data.loc[data["ÖlçümTipi"] == 'Iç Çap']
    row_data_ic = len(data_ic)

    ##step_data_ic =  (data['MaksimumDeğer'] - data['MinimumDeğer'] ) /  row_data_ic

    data_es = data.loc[data["ÖlçümTipi"] == 'Es Merkezlilik']
    row_data_es = len(data_es)
    ##step_data_es = (data['MaksimumDeğer'] - data['MinimumDeğer'] ) /  row_data_es



    fig = go.Figure()
    # Iterate through each row in the dataframe to add bars to the plot
    # For each range, add a bar to the plot
    fig.add_trace(go.Bar(
        x=list(data_ic["midpoints"]),  # Use the midpoint of the range as the x-value
        y=list(data_ic["Miktar"])
    ))

    fig.update_layout(xaxis=dict(tickmode='auto',
                                  title='Ölçümler',
                                 title_font=dict(size=25, family='Arial')
                                  ##dtick=0.06
                                  ),
                       yaxis=dict(title='Adet',
                                  title_font=dict(size=25, family='Arial')
                                  ))
    fig.update_layout(barmode='group')

    fig2 = go.Figure()
    # Iterate through each row in the dataframe to add bars to the plot
    # For each range, add a bar to the plot
    fig2.add_trace(go.Bar(
        x=list(data_es["midpoints"]),  # Use the midpoint of the range as the x-value
        y=list(data_es["Miktar"])
    ))

    fig2.update_layout(xaxis=dict(tickmode='auto',
                                  title='Ölçümler',
                                  title_font=dict(size=25, family='Arial')
                                  ##dtick=0.06
                                  ),
                       yaxis=dict(title='Adet',
                                  title_font=dict(size=25, family='Arial')
                                  ))
    fig2.update_layout(barmode='stack')

    return fig,fig2
