# Import required libraries and modules
from datetime import datetime, date, timedelta
import dash_bootstrap_components as dbc
import dash_table
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash import dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate
from dateutil.relativedelta import relativedelta
from config import valftoreeg, project_directory
from run.agent import ag
from valfapp.app import cache, app

query = f"SELECT MPOINT, SUBSTRING(DATE, 1, 8) AS DATE, SUM(OUTPUT) AS TOTAL FROM VLFENERGY WHERE COSTCENTER = 'TRAFO' GROUP BY MPOINT, SUBSTRING(DATE, 1, 8)"

query_pie = f"SELECT COSTCENTER,SUM(OUTPUT) AS CONSUMPTION FROM VLFENERGY WHERE MPOINT NOT LIKE CASE COSTCENTER WHEN 'CNC' THEN '%-%' ELSE '%ASDF%' END " \
            f"AND MPOINT  LIKE CASE COSTCENTER WHEN 'PRESHANE' THEN '%Pano%' ELSE '%%'  END AND DATE > '20231117' GROUP BY COSTCENTER ORDER BY COSTCENTER"

df = ag.run_query(query)

fig = px.bar(df, x='DATE', y='TOTAL', width=600, height=400)
fig.update_layout(bargap=0.2)


def return_pie():
    df_pie = ag.run_query(query_pie)
    df_pie["COSTCENTER"] = df_pie["COSTCENTER"].apply(lambda x: x.strip())
    df_pie.iloc[-1] = ("DIGER", df_pie.loc[df_pie["COSTCENTER"] == 'TRAFO', "CONSUMPTION"].sum() - df_pie.loc[
        df_pie["COSTCENTER"] != 'TRAFO', "CONSUMPTION"].sum())
    df_pief = df_pie[df_pie["COSTCENTER"] != 'TRAFO']
    return px.pie(data_frame=df_pief, values="CONSUMPTION", names="COSTCENTER")


layout = [dcc.Store(id='generated_data'),dcc.Download(id="download-energy"),
    dbc.Row(html.H1("Valfsan Production Energy Consumption",
                    style={'text-align': 'center', "fontFamily": 'Arial Black', 'fontSize': 30, 'backgroundColor': '#f0f0f0'})),
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dcc.Link(
                    children='Main Page',
                    href='/',
                    style={"color": "black", "font-weight": "bold"}
                ),
                html.Br(),
                html.Div(
                    [
                        # Div for dropdowns and date pickers
                        html.Div(
                            [
                                dcc.Dropdown(
                                    id='machine-type-dropdown',
                                    options=[{'label': k, 'value': k} for k in valftoreeg.keys()],
                                    value=list(valftoreeg.keys())[0],  # Default value
                                    style={'color': '#212121'}
                                ),
                                dcc.Dropdown(
                                    id='machine-dropdown',
                                    style={'color': '#212121'}
                                ),
                                dcc.DatePickerRange(
                                    id='date-picker',
                                    className="dash-date-picker-multi",
                                    start_date=(date.today() - timedelta(weeks=15)).isoformat(),
                                    end_date=(date.today() + timedelta(weeks=4)).isoformat(),
                                    display_format='YYYY-MM',
                                    style={'color': '#212121'}
                                )
                            ],
                            style={'display': 'inline-block', 'width': 'auto', 'marginRight': '20px'}
                        ),
                        # Separate Div for the button
                        html.Div(
                            [
                                html.Button(
                                    'Search',
                                    id='search',
                                    className="dash-empty-button",
                                    n_clicks=0,
                                    style={'backgroundColor': '#007bff', 'color': 'white', 'padding': '10px 20px'}
                                ),
                                html.Button(
                                    'Download',
                                    id='download',
                                    className="dash-empty-button",
                                    n_clicks=0,
                                    style={'backgroundColor': '#007bff', 'color': 'white', 'padding': '10px 20px'}
                                )
                            ],
                            style={'display': 'inline-block', 'textAlign': 'center'}
                        )
                    ],

                )]),
            dbc.Row([
                dash_table.DataTable(
                    id="data_table",
                    data=[],
                    columns=[],
                    filter_action='native',
                    style_cell={
                        "minWidth": "100px",
                        "width": "100px",
                        "maxWidth": "150px",
                        "textAlign": "center",
                        "padding": "10px"
                    },
                    style_table={
                        'width': '100%',
                        'margin': 'auto',
                        'borderCollapse': 'collapse',
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(248, 248, 248)'
                        }
                    ],
                    style_header={
                        'backgroundColor': 'rgb(230, 230, 230)',
                        'fontWeight': 'bold'
                    },
                    sort_action='native',
                ),
                dash_table.DataTable(
                    id="data_table_sum",
                    data=[],
                    columns=[],
                    style_cell={
                        "minWidth": "100px",
                        "width": "100px",
                        "maxWidth": "150px",
                        "textAlign": "center",
                        "padding": "10px"
                    },
                    style_table={
                        'width': '100%',
                        'margin': 'auto',
                        'borderCollapse': 'collapse',
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(248, 248, 248)'
                        }
                    ],
                    style_header={
                        'backgroundColor': 'rgb(230, 230, 230)',
                        'fontWeight': 'bold'
                    },
                    sort_action='native',
                )

            ], style={"marginTop": 50}
            )
        ]),
        dbc.Col([dcc.Graph(id='example-graph', figure=fig),
                 dcc.Graph(id="line_chart_combined"),
                 dcc.Graph(id="pie_chart", figure=return_pie())]
                , width=4)
    ]),
    dbc.Row([
        dbc.Col(),

    ])
]


# Define the callback to update the second dropdown
@app.callback(
    Output('machine-dropdown', 'options'),
    Input('machine-type-dropdown', 'value')
)
def set_machine_options(selected_machine_type):
    return [{'label': v, 'value': k} for k, v in valftoreeg[selected_machine_type].items()]


# @cache.memoize()
def update_table(begin_month, begin_year, final_month, final_year, costcenter, m_point):
    selected_point = m_point
    with open(project_directory + f"\Charting\queries\energy_qandweight.sql", 'r') as file:
        filedata = file.read()
    start_date = datetime(begin_year, begin_month, 1)
    end_date = datetime(final_year, final_month, 1)
    code_works = start_date.strftime('%Y-%m-%dT%H:%M:%S')
    code_worke = end_date.strftime('%Y-%m-%dT%H:%M:%S')

    difference = relativedelta(end_date, start_date)
    # Extract the number of months and years in the difference
    month_difference = difference.months + difference.years * 12

    df_final = pd.DataFrame()
    analizorler = []
    if costcenter != 'Bütün':
        analyzer = valftoreeg[costcenter]
        analizorler.append((m_point, costcenter))
    else:
        analyzer = {}
        for costcenter_tmp in valftoreeg:
            analyzer.update(valftoreeg[costcenter_tmp])
            for item in valftoreeg[costcenter_tmp]:
                analizorler.append((item, costcenter_tmp))
    print(analizorler)
    for m_point in analizorler:

        costcenter_tmp = m_point[1]
        m_point = m_point[0]

        if m_point == 'Bölümler' or m_point == 'Analizörler':
            continue

        if m_point == "K-13','K-18','K-19','K-20','K-21','K-22','K-23','K-25','K-27','K-28":
            m_point_tmp = '10 Kurutma'
        elif m_point == "T-19','T-20','T-21','T-22','T-23','T-24','T-25','T-26','T-27','T-34','T-37','T-43','T-44','T-45":
            m_point_tmp = '10 Tambur'
        elif m_point == "CNCTO-01','CNCTO-02','CNCTO-04','CNCTO-05','CNCTO-06','CNC-TO-07','CNCTO-08','CNCTO-09','CNCTO-10','CNCTO-11','CNCTO-12','CNCTO-13','CNCTO-14','CNC-TO-15','CNCTO-16','CNC-07','CNC-08','CNC-26','CNC-28":
            m_point_tmp = "19 CNC (Pano 1)"
        elif m_point == "CNCTO-01','CNCTO-02','CNCTO-04','CNCTO-05','CNCTO-06','CNCTO-07','CNCTO-08','CNCTO-09','CNCTO-10','CNCTO-11','CNCTO-12','CNCTO-13','CNCTO-14','CNCTO-15','CNCTO-16','CNC-07','CNC-08','CNC-26','CNC-28":
            m_point_tmp = "19 CNC (Pano 1)"
        elif m_point == "CNC-04', 'CNC-11', 'CNC-13', 'CNC-14', 'CNC-15', 'CNC-16', 'CNC-17', 'CNC-18', 'CNC-19', 'CNC-20', 'CNC-21', 'CNC-22', 'CNC-23', 'CNC-29', 'Z-01":
            m_point_tmp = "15 CNC (Pano 2)"
        elif m_point == "CNC-01', 'CNC-03', 'CNC-06', 'CNC-12', 'CNC-24', 'TB-01', 'STASLAMA', 'HONLAMA', 'ZIMPARA":
            m_point_tmp = "5 CNC ve 4 Taslama (Pano 3)"
        elif m_point == "P-04', 'P-08', 'P-24', 'P-36', 'P-46', 'P-50', 'P-69', 'P-76":
            m_point_tmp = "8 Pres (Salter 2)"
        elif m_point == "P-11', 'P-47', 'P-62', 'P-74":
            m_point_tmp = "4 Pres (Salter 3)"
        elif m_point == "P-12', 'P-19', 'P-23', 'P-30', 'P-31', 'P-33', 'P-34', 'P-37', 'P-55', 'P-56', 'P-61', 'P-70', 'P-71":
            m_point_tmp = "13 Pres (Salter 5)"
        elif m_point == "P-14', 'P-26', 'P-64', 'P-67', 'P-68', 'P-75', 'P-63', 'P-65', 'P-73', 'TC-05":
            m_point_tmp = "10 Pres (Salter 4-6)"
        elif m_point == "P-21','P-60','P-09','P-10','P-15','P-32','P-48','P-58','P-20','P-28','P-57":
            m_point_tmp = "11 Pres (Pano 3 Diger)"
        else:
            m_point_tmp = m_point

        if m_point_tmp == '11 Pres (Pano 3 Diger)':
            df_works = ag.run_query(f"WITH ASD AS ( SELECT LEFT(DATE, 4) + '-' + SUBSTRING(DATE, 6, 2)  AS DATE,MPOINT,OUTPUT as OUTPUT,COSTCENTER,INTERVAL FROM VLFENERGY WHERE MPOINT IN "
                                    f"('PRES - Pano 1','8 Pres (Salter 2)','13 Pres (Salter 5)','4 Pres (Salter 3)')  )"
                                    f"SELECT '11 Pres (Pano 3 Diger)' AS MPOINT, SUM(OUTPUT) AS OUTPUT,DATE from ASD GROUP BY DATE")
        else:
            df_works = ag.run_query(f"SELECT LEFT(DATE, 4) + '-' + SUBSTRING(DATE, 6, 2)  AS DATE,MPOINT,SCODE,"
                                f"SUM(OUTPUT) AS OUTPUT,COSTCENTER,INTERVAL FROM VLFENERGY"
                                f" WHERE MPOINT = '{m_point_tmp}' "
                                f"AND  DATE >= '{code_works}' AND '{code_worke}' > DATE "
                                f"GROUP BY LEFT(DATE, 4) + '-' + SUBSTRING(DATE, 6, 2),MPOINT,SCODE,COSTCENTER,INTERVAL")

        print(df_works)
        print("******")

        if len(df_works) == 0:
            continue

        filedata_tmp = filedata.replace("xxxx-yy-zz", str(start_date))
        filedata_tmp = filedata_tmp.replace("aaaa-bb-cc", str(end_date))
        try:
            filedata_tmp = filedata_tmp.replace("XXMATERIALYY", "'" + m_point + "'")
        except (TypeError) as e:
            filedata_tmp = filedata_tmp.replace("XXMATERIALYY", "x")

        # manüpüle ettiğimiz sorguyu çalıştırıyoruz ve yeni bir sütun ekliyoruz.
        df_prddata = ag.run_query(filedata_tmp)
        df_prddata.rename(columns={"TOTALNETWEIGHT": "TOTALNETWEIGHT(ton)"},inplace=True)

        df_prddata["MPOINT"] = m_point_tmp

        if len(df_prddata):
            df_works = df_works.merge(df_prddata, on=['MPOINT', 'DATE'], how='left').fillna(0)
            print(f"{df_works}")
            print(f"***********")

        else:
            df_prddata["MPOINT"] = m_point
            df_prddata["QUANTITY"] = 0
            df_prddata["TOTALNETWEIGHT(ton)"] = 0.000
            df_prddata["kwhPERton"] = 0.000

        df_final = pd.concat([df_works, df_final]).drop_duplicates().reset_index(drop=True)

    print("******")
    print(df_final)
    print("******")

    df_final.rename(columns={"OUTPUT": "OUTPUT(KWH)"},inplace=True)
    df_final["kwhPERton"] = df_final["kwhPERton"].astype(float)
    df_final["TOTALNETWEIGHT(ton)"] = df_final["TOTALNETWEIGHT(ton)"].astype(float)
    df_final["OUTPUT(KWH)"] = df_final["OUTPUT(KWH)"].astype(float)
    print(df_final.dtypes)
    df_final["kwhPERton"] = df_final.apply(lambda x: x["OUTPUT(KWH)"] / x["TOTALNETWEIGHT(ton)"] if x["TOTALNETWEIGHT(ton)"] > 0 else 0, axis=1)
    df_final["kwhPERqty"] = df_final.apply(lambda x: x["OUTPUT(KWH)"] / x["QUANTITY"] if x["QUANTITY"] > 0 else 0, axis=1)
    df_final["kwhPERton"] = df_final["kwhPERton"]
    df_final["kwhPERton"] = df_final["kwhPERton"].apply(lambda x: f"{x:.3f}")
    df_final["kwhPERqty"] = df_final["kwhPERqty"].apply(lambda x: f"{x:.3f}")
    df_final['DATE'] = df_final['DATE'].apply(lambda x: datetime.strptime(x, '%Y-%m'))

    print(df_final['DATE'].dtypes)

    # print(selected_point)
    # if selected_point == 'Bölümler':
    #     mask = ((df_final['COSTCENTER'] == 'CNC') | (df_final['COSTCENTER'] == 'PRESHANE')) & (
    #         ~df_final['ANALYZER'].str.contains('pano', na=False))
    #     df_final.loc[mask, ['CONSUMPTION', 'QUANTITY']] = 0
    #     df_final = df_final.groupby(["COSTCENTER","DATE"]).agg({"TOTALNETWEIGHT(ton)": "sum","kwhPERton": "mean","CONSUMPTION": "sum","QUANTITY":"sum",})
    #     df_final.reset_index(inplace=True)

    df_final.sort_values(by=["DATE", "kwhPERton"], ascending=False, inplace=True)
    df_final = df_final[["DATE","COSTCENTER", "MPOINT","TOTALNETWEIGHT(ton)", "OUTPUT(KWH)", "kwhPERton","QUANTITY","kwhPERqty"]]
    df_final_sum = df_final.loc[(df_final["OUTPUT(KWH)"]) > 0 & (df_final["QUANTITY"] > 0)]

    print("******")
    print(df_final)
    print("******")
    print("******")
    print(df_final_sum)
    print("******")

    # df_final_sum = df_final_sum.groupby(["DATE"]).agg({"OUTPUT(KWH)": "sum", "TOTALNETWEIGHT(ton)": "sum"
    #                                  ,"QUANTITY": "sum"})
    df_final_sum = df_final_sum.iloc[0:0]

    df_final_sum.loc[len(df_final_sum.index)]  = ('0000-00-00T00:00:00+00:00',"ALL","ALL",df_final["TOTALNETWEIGHT(ton)"].sum(),
                          df_final["OUTPUT(KWH)"].sum(),0.000,df_final["QUANTITY"].sum(),0.000)
    df_final_sum["kwhPERton"] = df_final_sum["OUTPUT(KWH)"] / df_final_sum["TOTALNETWEIGHT(ton)"]
    df_final_sum["kwhPERqty"] = df_final_sum.apply(lambda x: x["OUTPUT(KWH)"] / x["QUANTITY"] if x["QUANTITY"] > 0 else 0,
                                           axis=1)
    df_final_sum["kwhPERton"] = df_final_sum["kwhPERton"].apply(lambda x: f"{x:.3f}")
    df_final_sum["kwhPERqty"] = df_final_sum["kwhPERqty"].apply(lambda x: f"{x:.3f}")

    df_final["TOTALNETWEIGHT(ton)"] = df_final["TOTALNETWEIGHT(ton)"].apply(lambda x: f"{x:.3f}")

    print("******")
    print(df_final_sum)
    print("******")

    # if df_final_sum is None:
    #     df_final_sum = pd.DataFrame(columns=["DATE", "OUTPUT(KWH)", "TOTALNETWEIGHT(ton)", "QUANTITY"])
    # else:
    #     df_final_sum["kwhPERton"] = 0.000
    #     df_final_sum["kwhPERqty"] = 0.000
    #     df_final_sum["kwhPERton"] = df_final_sum.apply(lambda x: x["OUTPUT(KWH)"] / x["TOTALNETWEIGHT(ton)"] if x["TOTALNETWEIGHT(ton)"] > 0 else 0, axis=1)
    #     df_final_sum["kwhPERqty"] = df_final_sum.apply(lambda x: x["OUTPUT(KWH)"] / x["QUANTITY"] if x["QUANTITY"] > 0 else 0, axis=1)
    #     df_final_sum["kwhPERton"] = df_final_sum["kwhPERton"] * 1000
    #     df_final_sum["kwhPERton"] = df_final_sum["kwhPERton"].apply(lambda x: f"{x:.1f}")
    #     df_final_sum["kwhPERqty"] = df_final_sum["kwhPERqty"].apply(lambda x: f"{x:.2f}")
    print(df_final)

    return df_final.to_json(date_format='iso', orient='split'),\
        df_final_sum.to_json(date_format='iso', orient='split')




@app.callback(
    Output("data_table", "data"),
    Output("data_table", "columns"),
    Output("data_table_sum", "data"),
    Output("data_table_sum", "columns"),
    Output('generated_data', 'data'),
    [State('date-picker', 'start_date'),
     State('date-picker', 'end_date'),
     State('machine-type-dropdown', 'value'),
     State('machine-dropdown', 'value'),
     Input('search', 'n_clicks')]
)
def cache_to_result(s_date, f_date, costcenter, m_point, button):
    if button <= 0:
        raise PreventUpdate
    f_date = datetime.strptime(f_date, "%Y-%m-%d")
    f_date = str(f_date + relativedelta(months=+1))
    final_month = int(f_date[5:7])
    begin_month = int(s_date[5:7])
    final_year = int(f_date[0:4])
    begin_year = int(s_date[0:4])
    df_final,df_final_sum = update_table(begin_month, begin_year,
                            final_month, final_year, costcenter, m_point)
    df_final = pd.read_json(df_final, orient='split')
    df_final_sum=  pd.read_json(df_final_sum, orient='split')
    columns = [{"name": i, "id": i} for i in df_final.columns]
    columns2 = [{"name": i, "id": i} for i in df_final_sum.columns]
    excel_data =pd.concat([df_final,df_final_sum]).to_json(date_format='iso', orient='split')
    return df_final.to_dict("records"), columns\
        ,df_final_sum.to_dict("records"),columns2,\
        excel_data


@app.callback(
    Output("line_chart_combined", "figure"),
    [Input("data_table", "data")]
)
def line_graph_update(data):
    # Convert the input data to a DataFrame
    print("here")
    df = pd.DataFrame(data)
    df.sort_values(by="DATE", ascending=False, inplace=True)
    fig_combined = go.Figure()

    # Add trace for kwhPERton

    fig_combined.add_trace(go.Scatter(x=df["DATE"], y=df["kwhPERton"], mode='lines+markers', name='kWh/ton'))

    # Add trace for kwhPERqty
    fig_combined.add_trace(
        go.Scatter(x=df["DATE"], y=df["kwhPERqty"] * 1000, mode='lines+markers', name='kWh*1000/Quantity'))

    # Add trace for kwhPERqty
    fig_combined.add_trace(go.Scatter(x=df["DATE"], y=df["OUTPUT(KWH)"], mode='lines+markers', name='Consumption'))

    # Update layout
    fig_combined.update_layout(
        title='Energy Consumption Comparison',
        xaxis_title='Date',
        yaxis_title='Energy Consumption',
        legend_title="Metrics"
    )

    return fig_combined

@app.callback(
    Output("download-energy", "data"),
    Input("download", "n_clicks"),
    State(component_id='generated_data', component_property='data'),
    prevent_initial_call=True
)
def generate_excel(n_clicks,generated_data):
    generated_data = pd.read_json(generated_data, orient='split')
    if n_clicks < 1:
        raise PreventUpdate

    return dcc.send_data_frame(generated_data.to_excel, "energydata.xlsx", index=False)