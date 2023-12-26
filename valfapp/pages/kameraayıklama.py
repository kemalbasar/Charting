import pandas as pd
from dash import dcc, html, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from run.agent import agiot as ag
from valfapp.app import app


layout = [
    dcc.Store(id='ayıklama_data',
              data={}),
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
        , html.Button(id="search_button", name='Search', className="dash-empty-button")])
    ),

    dbc.Row([dcc.Graph(id="dist_plot")])
]


@app.callback(
    Output("ayıklama_data", 'data'),
    Output('material_ayk', 'options'),
    Input("search_button", 'n_clicks'),
)
def store_data(n):
    data = ag.run_query(r"SELECT * FROM VLFAYIKLAMA WHERE ÖlçümTipi = 'İç Çap'")
    data['MinimumDeğer'] = data['MinimumDeğer'].astype(float)
    data['MaksimumDeğer'] = data['MaksimumDeğer'].astype(float)
    data['Miktar'] = data['Miktar'].astype(int)
    data["midpoints"] = (data['MinimumDeğer'] + data['MaksimumDeğer']) / 2
    data["Malzeme"] = data["Malzeme"].apply(lambda x: x.split('\x00', 1)[0])

    material_list = list(data["Malzeme"].unique())

    data = data.to_json(date_format='iso', orient='split')
    return data, material_list



@app.callback(
    Output(component_id="dist_plot", component_property="figure"),
    Input("material_ayk", "value"),
    State("ayıklama_data", "data"),
)
def draw_dist_plot(material,data):
    data = pd.read_json(data, orient='split')
    print(type(material))
    print(data["Malzeme"].dtype)
    data["Malzeme"] = data["Malzeme"].astype(str)
    data = data.loc[data["Malzeme"] == material]
    print(f"burada filtrelenmiş data datam var {data} ********************")


    fig = go.Figure()
    # Iterate through each row in the dataframe to add bars to the plot
    # For each range, add a bar to the plot
    fig.add_trace(go.Bar(
        x=list(data["midpoints"]),  # Use the midpoint of the range as the x-value
        y=list(data["Miktar"])
    ))


    return fig