import dash
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output

from config import project_directory
from valfapp.app import app
from valfapp.functions.functions_val import total_value, df_histval, df_histstocks
from valfapp.layouts import layout_12

df_val = pd.read_excel(project_directory + r"\Charting\outputs(xlsx)\val2022.xlsx")
dash.register_page(__name__, path='/')
total_value = format(int(total_value), ",")
layout = []
layout = layout_12

px.colors.qualitative.Pastel[0]
color_map = {"HAMMADDE":px.colors.qualitative.Pastel[0],
                'MAMÜL' :px.colors.qualitative.Pastel[1],
                'YARDIMCI MALZEME' :px.colors.qualitative.Pastel[2],
                'YARIMAMÜL':px.colors.qualitative.Pastel[3]}
color_map2 = {"HAMMADDE":px.colors.qualitative.Pastel[0],
                'MAMÜL' :px.colors.qualitative.Pastel[1],
                'YARDIMCI MALZEME' :px.colors.qualitative.Pastel[2],
                'YARI MAMÜL':px.colors.qualitative.Pastel[3]}

@app.callback(
    [Output(component_id='HAMMADDE', component_property='figure'),
     Output(component_id='MAMÜL', component_property='figure'),
     Output(component_id='YARDIMCI MALZEME', component_property='figure'),
     Output(component_id='YARI MAMÜL', component_property='figure')],
    [Input(component_id='year', component_property='value')]
)
def plotly_histogram(year):
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
            # width=800,
            # height=500,
            bargap=0.80,
            autosize=True

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
    df_sum.sort_values(by="ACIKLAMA", ascending=False, inplace=True)
    df_sum.columns = ["labels", "values"]
    print(df_sum["labels"].unique())
    piec = px.pie(df_sum, values='values', names='labels',color='labels',
                  color_discrete_map=color_map2)

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
    lines = []
    list  = df_histval['MATTYPE'].unique()
    list.sort()
    for i, mattype in enumerate(list):
        df = df_histval[df_histval['MATTYPE'] == mattype]
        line = go.Scatter(x=df['DATEOF'], y=df['TOTALVALUE'], name=mattype, mode='lines',
                          line=dict(color=color_map[mattype]))
        lines.append(line)

    layout = go.Layout(title='Line Chart of Total Value by Material '
                             'Type and Date', xaxis={'title': 'Date'},
                       yaxis={'title': 'Total Value'},
                       font=dict(size=12, color='#cd5c5c'),
                       paper_bgcolor='rgba(0, 0, 0, 0)',
                       plot_bgcolor='rgba(0, 0, 0, 0)',
                       # width=600,
                       # height=300
                       autosize=True)

    linechart = go.Figure(data=lines, layout=layout)

    return [linechart]


@app.callback(
    [Output(component_id='linechart2', component_property='n_clicks')],
    [Input(component_id='rawmat', component_property='n_clicks'),
     Input(component_id='prod', component_property='n_clicks'),
     Input(component_id='halfprod', component_property='n_clicks')]
)
def create_line_chart(year):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'rawmat' in changed_id:
        df_final = df_histstocks[df_histstocks["ACIKLAMA"] == 'HAMMADDE']
    elif 'prod' in changed_id:
        df_final = df_histstocks[df_histstocks["ACIKLAMA"] == 'MAMÜL']
    elif 'halfprod' in changed_id:
        df_final = df_histstocks[df_histstocks["ACIKLAMA"] == 'YARI MAMÜL']

    colors = px.colors.qualitative.Set2[0:4]
    lines = []

    for i, mattype in enumerate(
            np.delete(df_final['GRUBU'].unique(), np.where(df_final['GRUBU'].unique() == "AMORPRC"))):
        df = df_final[df_final['MATTYPE'] == mattype]
        line = go.Scatter(x=df['DATEOF'], y=df['TOTALVALUE'], name=mattype, mode='lines',
                          line=dict(color=colors[i]))
        lines.append(line)

    layout = go.Layout(title='Line Chart of Total Value by Material Type and Date', xaxis={'title': 'Date'},
                       yaxis={'title': 'Total Value'},
                       font=dict(size=12, color='#cd5c5c'),
                       paper_bgcolor='rgba(0, 0, 0, 0)',
                       plot_bgcolor='rgba(0, 0, 0, 0)',
                       width=600,
                       height=300)

    linechart = go.Figure(data=lines, layout=layout)
    linechart.update_yaxes(title_text='Y2-axis', secondary_y=True)
    linechart.add_trace(px.line(df, x='x', y='y2', color='y2'))
    return [linechart]
