import dash_table
from dash import dcc, html, Input, Output, State, no_update
import dash_bootstrap_components as dbc
from config import project_directory
import plotly.graph_objs as go
from run.agent import agiot as ag




data = ag.run_query(r"SELECT * FROM VLFAYIKLAMA where MakinaNo = 'KMR-1' AND Malzeme = '1001850800' AND ÖlçümTipi = '[İç Çap]'")
data['MinimumDeğer'] = data['MinimumDeğer'].astype(float)
data['MaksimumDeğer'] = data['MaksimumDeğer'].astype(float)
data['Miktar'] = data['Miktar'].astype(int)

data["midpoints"] = (data['MinimumDeğer'] + data['MaksimumDeğer']) / 2

import plotly.express as px
fig = go.Figure()

# Iterate through each row in the dataframe to add bars to the plot
    # For each range, add a bar to the plot
fig.add_trace(go.Bar(
    x=list(data["midpoints"]), # Use the midpoint of the range as the x-value
    y=list(data["Miktar"])
    # width=int(row['MinimumDeğer'][0][0]) - int(row['MaksimumDeğer'][0][0]), # The width of the bar is the range size
    # name=f"{row['MinimumDeğer']}-{row['MaksimumDeğer']} mm" # Label for each bar
))

# Update the layout of the plot
fig.update_layout(
    title='Distribution of Metal Pieces by Radius',
    xaxis_title='Radius (mm)',
    yaxis_title='Quantity',
    barmode='overlay' # Bars will overlap each other
)


layout = [dbc.Row([html.H1("Ayıklama Robotu Kalite Sonuçları",style={'text-align': 'center', "fontFamily": 'Arial Black', 'fontSize': 30,
                           'backgroundColor': '#f0f0f0'})]),
          dbc.Row([dcc.Input(
                    id="height",
                    placeholder="row",
                    value=500,
                    type = 'number',
                    style={"width": "180px"},
                    persistence=True,  # Enable persistence
                    persistence_type='local' # Store in local storage
                ),
                dcc.Input(
                    id="width",
                    placeholder="col",
                    value=700,
                    type='number',
                    style={"width": "180px"},
                    persistence=True,  # Enable persistence
                    persistence_type='local'  # Store in local storage
                )]),
          dbc.Row([dcc.Graph(figure=fig)])
          ]





# Create an empty figure
