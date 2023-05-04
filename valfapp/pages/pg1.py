from config import project_directory
import dash
import numpy as np
import dash_bootstrap_components as dbc
from valfapp.app import app
from valfapp.functions.functions_val import total_value, df_histval, df_histstocks
import plotly.graph_objects as go
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd

df_val = pd.read_excel(project_directory + r"\Charting\outputs(xlsx)\val2022.xlsx")
dash.register_page(__name__, path='/')
total_value = format(int(total_value), ",")
layout = []
layout = dbc.Container([
    dbc.Row(html.Button(id='year', value="2022", children='Click me')),
    dbc.Row([

        dbc.Col([html.Div(dcc.Graph(id="piec", figure={}, style={"margin-top": 20}))],
                style={"width": 300, "height": 500, "border-right": "6px black inset"}),

        dbc.Col(html.Div(children=[html.Div(["Current Value", html.Br(), total_value],
                                            style={'margin-top': 50, 'margin-left': 100,
                                                   "fontSize": 24,
                                                   "text-align": "center", "color": "white",
                                                   "font-weight": "bold",
                                                   "background-color": "firebrick",
                                                   "height": 70,
                                                   "width": 300}),
                                   html.Br(),
                                   dcc.Graph(id="linechart", figure={},
                                             style={"margin-top": 1,'margin-right': 520})],
                         style={"height": 100, "width": 250})),
        dbc.Col(html.Div(children=[html.Div(["Current Value2", html.Br(), total_value],
                                            style={"fontSize": 24, "text-align": "center",
                                                   "color": "white",
                                                   "font-weight": "bold",
                                                   "background-color": "firebrick",
                                                   'margin-top': 50,
                                                   'margin-right': 80, "height": 70,
                                                   "width": 300}),
                                   html.Div(children=[
                                       html.Button(id='rawmat', n_clicks=0,
                                                   children='Raw Material'),
                                       html.Button(id='prod', n_clicks=0,
                                                   children='Product'),
                                       html.Button(id='halfprod', n_clicks=0,
                                                   children='Half Product')],
                                       style={"margin-top": 50,
                                              "background-color": "burlywood"})
                                   ], style={}))],
            style={"background-color": "#FFEBCD", "width": 1900, "height": 500}),
    dbc.Row(
        [

            html.Div(children=["Div 1", html.Div(dcc.Graph(id="MAMÜL",
                                                           figure={}))],
                     style={"background-color": "#FFEBCD", "width": 944, "height": 600,
                            "margin-top": 9}),

            html.Div(children=["Div 2", html.Div(dcc.Graph(id="HAMMADDE",
                                                           figure={}))],
                     style={"background-color": "#FFEBCD", "width": 944, "height": 600,
                            "margin-left": 6,
                            "margin-top": 9})

        ]
    ),
    dbc.Row(
        [
            html.Div(children=["Div 1", html.Div(dcc.Graph(id="YARI MAMÜL",
                                                           figure={}))],
                     style={"background-color": "#FFEBCD", "width": 944,
                            "height": 600,
                            "margin-top": 1, }),
            html.Div(children=["Div 2", html.Div(dcc.Graph(id="YARDIMCI MALZEME",
                                                           figure={}))],
                     style={"background-color": "#FFEBCD", "width": 944,
                            "height": 600,
                            "margin-left": 6,
                            "margin-top": 1, })

        ], style={"margin-top": 15}
    )

], fluid=True
)


@app.callback(
    [Output(component_id='HAMMADDE', component_property='figure'),
     Output(component_id='MAMÜL', component_property='figure'),
     Output(component_id='YARDIMCI MALZEME', component_property='figure'),
     Output(component_id='YARI MAMÜL', component_property='figure')],
    [Input(component_id='year', component_property='value')]
)
def plotly_histogram(year):
    print(df_val)
    types_of_product = list(df_val["ACIKLAMA"].unique())
    labels = ['Raw Materials', 'Products', 'Auxiliary Materials',
              'Half Products']
    for mattype, label in zip(types_of_product, labels):
        df = df_val.loc[df_val["ACIKLAMA"] == mattype, ["GRUBU", "TOTVAL"]]
        tshold = df["TOTVAL"].sum() * 0.01
        df.loc[df["GRUBU"] == "DIGER", "TOTVAL"] += df[df['TOTVAL']
                                           < tshold]["TOTVAL"].sum()
        df = df[df['TOTVAL'] >= tshold]

        # Creating the histogram chart
        globals()[mattype] = px.bar(df, y='GRUBU', x='TOTVAL',
                                    color_discrete_sequence=["firebrick"],
                                    text_auto='.2s',
                                    orientation='h',
                                    title="Current Valueus of Products")

        # Adding nice design elements
        globals()[mattype].update_layout(
            title=f'Current Values of {label}',
            xaxis_title='Value',
            yaxis_title='Material Types',
            font=dict(size=12, color='#cd5c5c'),
            paper_bgcolor='rgba(0, 0, 0, 0)',
            plot_bgcolor='rgba(0, 0, 0, 0)',
            xaxis={'categoryorder': 'total ascending'},
            width=800,
            height=500,
            bargap=0.80

        )

        globals()[mattype].update_traces(width=1)

    return [globals()[types_of_product[0]], globals()[types_of_product[1]],
            globals()[types_of_product[2]],
            globals()[types_of_product[3]]]


@app.callback(
    [Output(component_id='piec', component_property='figure')],
    [Input(component_id='year', component_property='value')]
)
def plot_3d_pie(df):
    df_sum = df_val.groupby("ACIKLAMA").agg({"TOTVAL": "sum"})
    df_sum.reset_index(inplace=True)
    df_sum.columns = ["labels", "values"]
    piec = px.pie(df_sum, values='values', names='labels',
                  color_discrete_map=px.colors.qualitative.Set2)
    # piec.update_layout(scene=dict(
    #     xaxis_title='X Axis',
    #     yaxis_title='Y Axis',
    #     zaxis_title='Z Axis'))

    piec.update_layout(
        title=f'Value Share',
        xaxis_title='Value',
        yaxis_title='Material Types',
        font=dict(size=12, color='#cd5c5c'),
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        width=485,
        height=485
    )
    return [piec]


@app.callback(
    [Output(component_id='linechart', component_property='figure')],
    [Input(component_id='year', component_property='value')]
)
def create_line_chart(year):
    colors = ['red', 'blue', 'green', 'orange']
    lines = []
    for i, mattype in enumerate(df_histval['MATTYPE'].unique()):
        df = df_histval[df_histval['MATTYPE'] == mattype]
        line = go.Scatter(x=df['DATEOF'], y=df['TOTALVALUE'], name=mattype, mode='lines',
                          line=dict(color=colors[i]))
        lines.append(line)

    layout = go.Layout(title='Line Chart of Total Value by Material '
                             'Type and Date', xaxis={'title': 'Date'},
                       yaxis={'title': 'Total Value'},
                       font=dict(size=12, color='#cd5c5c'),
                       paper_bgcolor='rgba(0, 0, 0, 0)',
                       plot_bgcolor='rgba(0, 0, 0, 0)',
                       width=600,
                       height=300)

    linechart = go.Figure(data=lines, layout=layout)

    return [linechart]


# @app.callback(
#     [Output(component_id='linechart2', component_property='n_clicks')],
#     [Input(component_id='rawmat', component_property='n_clicks'),
#      Input(component_id='prod', component_property='n_clicks'),
#      Input(component_id='halfprod', component_property='n_clicks')]
# )
# def create_line_chart(year):
#     changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
#     if 'rawmat' in changed_id:
#         df_final = df_histstocks[df_histstocks["ACIKLAMA"] == 'HAMMADDE']
#     elif 'prod' in changed_id:
#         df_final = df_histstocks[df_histstocks["ACIKLAMA"] == 'MAMÜL']
#     elif 'halfprod' in changed_id:
#         df_final = df_histstocks[df_histstocks["ACIKLAMA"] == 'YARI MAMÜL']
#
#     colors = ['red', 'blue', 'green', 'orange']
#     lines = []
#
#     for i, mattype in enumerate(
#             np.delete(df_final['GRUBU'].unique(), np.where(df_final['GRUBU'].unique() == "AMORPRC"))):
#         df = df_final[df_final['MATTYPE'] == mattype]
#         line = go.Scatter(x=df['DATEOF'], y=df['TOTALVALUE'], name=mattype, mode='lines',
#                           line=dict(color=colors[i]))
#         lines.append(line)
#
#     layout = go.Layout(title='Line Chart of Total Value by Material Type and Date', xaxis={'title': 'Date'},
#                        yaxis={'title': 'Total Value'},
#                        font=dict(size=12, color='#cd5c5c'),
#                        paper_bgcolor='rgba(0, 0, 0, 0)',
#                        plot_bgcolor='rgba(0, 0, 0, 0)',
#                        width=600,
#                        height=300)
#
#     linechart = go.Figure(data=lines, layout=layout)
#     linechart.update_yaxes(title_text='Y2-axis', secondary_y=True)
#     linechart.add_trace(px.line(df, x='x', y='y2', color='y2'))
#     return [linechart]
