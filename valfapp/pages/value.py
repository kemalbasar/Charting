import dash
import datetime as dt
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output
from valfapp.app import app
from valfapp.layouts import layout_12
from run.agent import ag

dash.register_page(__name__, path='/')

cur_week = (dt.datetime.now()).strftime('%Y-%U').zfill(6)
df_val = ag.run_query(f"SELECT * FROM VLFVALUATION  WHERE ACIKLAMA != '' ")
df_curval = df_val.loc[df_val["VALDATE"] == cur_week]

layout = [
]


layout = layout_12

color_map = {"HAMMADDE": px.colors.qualitative.Pastel[0],
             'MAMÜL': px.colors.qualitative.Pastel[1],
             'YARDIMCI MALZEME': px.colors.qualitative.Pastel[2],
             'YARIMAMÜL': px.colors.qualitative.Pastel[3]}
color_map2 = {"HAMMADDE": px.colors.qualitative.Pastel[0],
              'MAMÜL': px.colors.qualitative.Pastel[1],
              'YARDIMCI MALZEME': px.colors.qualitative.Pastel[2],
              'YARI MAMÜL': px.colors.qualitative.Pastel[3]}


@app.callback(
    [Output(component_id='HAMMADDE', component_property='figure'),
     Output(component_id='MAMÜL', component_property='figure'),
     Output(component_id='YARDIMCI MALZEME', component_property='figure'),
     Output(component_id='YARI MAMÜL', component_property='figure')],
    [Input(component_id='year', component_property='value')]
)
def plotly_histogram(year):
    types_of_product = list(color_map2.keys())
    labels = ['Raw Materials', 'Products', 'Auxiliary Materials', 'Half Products']
    for mattype, label in zip(types_of_product, labels):
        df = df_curval.loc[df_curval["ACIKLAMA"] == mattype, ["GRUBU", "VALUE"]]
        df["VALUE"] = df["VALUE"].astype(float)
        tshold = df["VALUE"].sum() * 0.01
        df.loc[df["GRUBU"] == "DIGER", "VALUE"] += df[df['VALUE']
                                                      < tshold]["VALUE"].sum()
        df = df[df['VALUE'] >= tshold]

        # Creating the histogram chart
        globals()[mattype] = px.bar(df, y='GRUBU', x='VALUE',
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
            # width=800,
            # height=500,
            bargap=0.80,
            autosize=True

        )

        globals()[mattype].update_yaxes(categoryorder='total ascending')

        globals()[mattype].update_traces(width=1)

    return [globals()[types_of_product[0]], globals()[types_of_product[1]],
            globals()[types_of_product[2]],
            globals()[types_of_product[3]]]


@app.callback(
    [Output(component_id='piec', component_property='figure')],
    [Input(component_id='year', component_property='value')]
)
def plot_3d_pie(df):
    df_sum = df_curval.groupby("ACIKLAMA").agg({"VALUE": "sum"})
    df_sum.reset_index(inplace=True)
    df_sum.sort_values(by="ACIKLAMA", ascending=False, inplace=True)
    df_sum.columns = ["labels", "values"]
    # print(df_sum["labels"].unique())
    piec = px.pie(df_sum, values='values', names='labels', color='labels',
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
    [Input(component_id='year', component_property='value'),
     Input(component_id='rawmat', component_property='n_clicks'),
     Input(component_id='prod', component_property='n_clicks'),
     Input(component_id='halfprod', component_property='n_clicks'),
     Input(component_id='main', component_property='n_clicks')
     ]
)
def create_line_chart(year, rawmat, prod, halfprod,main):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    # print(f"rawmat = {rawmat}")
    # print(f"prod = {prod}")
    # print(f"halfprod = {halfprod}")
    # print(f"main = {main}")
    # print(df_val)
    if rawmat or prod or halfprod or main:
        if 'rawmat' in changed_id:
            df_valhist = df_val[df_val["ACIKLAMA"] == 'HAMMADDE']
            groupby_columns = ['VALDATE', 'GRUBU']
            print("burda")
        elif 'halfprod' in changed_id:
            df_valhist = df_val[df_val["ACIKLAMA"] == 'YARI MAMÜL']
            groupby_columns = ['VALDATE', 'GRUBU']
            print("halfprodBURDADAD")
        elif 'prod' in changed_id:
            df_valhist = df_val[df_val["ACIKLAMA"] == 'MAMÜL']
            groupby_columns = ['VALDATE', 'GRUBU']
            print("prodBURDADAD")
        else:
            df_valhist = df_val
            groupby_columns = ['VALDATE', 'ACIKLAMA']
            colorcheck = 1
        colorcheck = 0
    else:
        df_valhist = df_val
        groupby_columns = ['VALDATE', 'ACIKLAMA']
        colorcheck = 1

    # return [line_chart(df_final)]
    # button_id = callback_context.triggered[0]['prop_id'].split('.')[0]

    lines = []
    df_valhist = df_valhist.groupby(groupby_columns).agg({'VALUE': 'sum'})
    df_valhist.reset_index(inplace=True)
    # df_valhist.sort_values(by="VALUE", ascending=False)[groupby_columns[1]].unique()
    listofype = df_valhist.sort_values(by="VALUE", ascending=False)[groupby_columns[1]].unique()
    if colorcheck == 0:
        print(listofype)
        #creating dictionary for color mapping that match listoftype and  px.colors.qualitative.Pastel color list
        colormap_active = {k:v for k,v in zip(listofype, px.colors.qualitative.Pastel*3)}
        print(colormap_active)
    else:
        colormap_active = color_map2

    for i, mattype in enumerate(listofype):
        df = df_valhist[df_valhist[groupby_columns[1]] == mattype]
        line = go.Scatter(x=df['VALDATE'], y=df['VALUE'], name=mattype, mode='lines',
                          line=dict(color=colormap_active[mattype]))
        lines.append(line)
        if i >= 7:
            break

    layout = go.Layout(title='Line Chart of Total Value by Material '
                             'Type and Date', xaxis={'title': 'Date','tickangle': 50},
                       yaxis={'title': 'Total Value'},
                       font=dict(size=12, color='#cd5c5c'),
                       paper_bgcolor='rgba(0, 0, 0, 0)',
                       plot_bgcolor='rgba(0, 0, 0, 0)',
                       # width=600,
                       # height=300
                       autosize=True)

    linechart = go.Figure(data=lines, layout=layout)

    return [linechart]

# @app.callback(
#     [Output(component_id='linechart2', component_property='n_clicks')],
#     []
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
#     colors = px.colors.qualitative.Set2[0:4]
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
