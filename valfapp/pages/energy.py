# Import required libraries and modules
from datetime import datetime, date, timedelta
import dash_bootstrap_components as dbc
import dash_table
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from _plotly_utils.colors.qualitative import Alphabet
from dash import dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate
from dateutil.relativedelta import relativedelta
from config import valftoreeg, project_directory
from run.agent import ag
from valfapp.app import cache, app
from valfapp.configuration import layout_color

query = f"SELECT  TOP 3 MPOINT, SUM(OUTPUT) AS TOTAL,SUBSTRING(DATE, 1, 7)  as DATE " \
        f"FROM VLFENERGY " \
        f"WHERE COSTCENTER = 'TRAFO' " \
        f"AND CAST(SUBSTRING(DATE, 1, 10) AS DATE) > DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()) - 3, 0) " \
        f"GROUP BY MPOINT, SUBSTRING(DATE, 1, 7) " \
        f"ORDER BY SUBSTRING(DATE, 1, 7) DESC"

query_pie = f"SELECT COSTCENTER,SUM(OUTPUT) AS CONSUMPTION FROM VLFENERGY WHERE MPOINT NOT LIKE CASE COSTCENTER WHEN 'CNC' THEN '%-%' ELSE '%ASDF%' END " \
            f"AND MPOINT  LIKE CASE COSTCENTER WHEN 'PRESHANE' THEN '%Pano%' ELSE '%%'  END AND DATE > '20231117' GROUP BY COSTCENTER ORDER BY COSTCENTER"

df = ag.run_query(query)

fig = px.bar(df,orientation='h',x='TOTAL', y='DATE', width=350, height=400)
fig.update_layout(xaxis=dict(
        showgrid=True,  # Show gridlines for x-axis
        gridcolor='LightPink',  # Change to desired gridline color for x-axis
        gridwidth=2  # Change to desired gridline width for x-axis
    ),
    yaxis=dict(
        dtick="M1",
        showgrid=True,  # Show gridlines for y-axis
        gridcolor='LightBlue',  # Change to desired gridline color for y-axis
        gridwidth=2  # Change to desired gridline width for y-axis
    ),bargap=0.2,paper_bgcolor=layout_color,plot_bgcolor='rgba(0, 0, 0, 0)')



def return_pie():
    df_pie = ag.run_query(query_pie)
    df_pie["COSTCENTER"] = df_pie["COSTCENTER"].apply(lambda x: x.strip())
    df_pie.iloc[-1] = ("DIGER", df_pie.loc[df_pie["COSTCENTER"] == 'TRAFO', "CONSUMPTION"].sum() - df_pie.loc[
        df_pie["COSTCENTER"] != 'TRAFO', "CONSUMPTION"].sum())
    df_pief = df_pie[df_pie["COSTCENTER"] != 'TRAFO']
    fig=px.pie(data_frame=df_pief, values="CONSUMPTION", names="COSTCENTER").update_layout(legend=dict(
        font=dict(size=9),  # Decrease font size for legend text
    ),paper_bgcolor=layout_color,width=480, height=400)
    fig.update_traces(textinfo='percent', textfont_size = 12,marker = dict(colors=Alphabet, line=dict(color='#000000', width=2)))


    return fig

layout = [
    # Your commented-out buttons
    # dbc.Button("Day", id="btn-day_en", n_clicks=0, color="primary", className='day-button'),
    # dbc.Button("Week", id="btn-week1_en", n_clicks=0, color="primary", className='week-button'),
    # dbc.Button("Month", id="btn-month1_en", n_clicks=0, color="primary", className='month-button'),
    # dbc.Button("Year", id="btn-year1_en", n_clicks=0, color="primary", className='year-button'),

    # Store and Download components
    dcc.Store(id='generated_data'), dcc.Download(id="download-energy"),

    # Navigation Bar
    html.Nav(className="main-menu side-bar", children=[
        dbc.Container([
            html.Div(className="logo-div resim-container", children=[
                html.A(className="logo", href="/", children=[
                    html.Img(src='/assets/valf-logo.gif', className="logo")
                ])
            ]),
            html.Div(className="settings"),
            html.Div(id="style-1", className="scrollbar", children=[
                html.Ul(children=[
                    html.Li(children=[
                        html.A(href="/", children=[
                            html.Img(src="../assets/home.png", className="nav-icon"),
                            html.Span(className="nav-text nav-text-2", children="MAIN")
                        ])
                    ]),
                    html.Li(className="darkerlishadow",children=[
                        html.A(href="/value", children=[
                            html.Img(src="../assets/tutarlama-icon.PNG", className="nav-icon"),
                            html.Span(className="nav-text", children="Tutarlama")
                        ])
                    ]),
                    html.Li(className="darkerli",children=[
                        html.A(href="/uretimrapor", children=[
                            html.Img(src="../assets/uretim-raporlari-icon.png", className="nav-icon"),
                            html.Span(className="nav-text", children="Üretim Raporları")
                        ])
                    ]),
                    html.Li(className="darkerli", children=[
                        html.A(href="/liveprd", children=[
                            html.Img(src="../assets/uretim-takip-icon.PNG", className="nav-icon"),
                            html.Span(className="nav-text", children="Üretim Takip")
                        ])
                    ]),
                    html.Li(className="darkerli",children=[
                        html.A(href="/tvmonitor", children=[
                            html.Img(src="../assets/tvmonitor-ıcon.png", className="nav-icon"),
                            html.Span(className="nav-text", children="Tv Monitor")
                        ])
                    ]),
                    html.Ul(className="darkerlishadowdown", children=[
                        html.Li(children=[
                            html.A(href="/energy", children=[
                               html.Img(src="../assets/enerji-takibi.png", className="nav-icon"),
                                html.Span(className="nav-text", children="Energy")
                            ])
                        ])
                    ])
                ])
            ])
        ]),
    ]),

    # Energy Search and Filter Components

    dbc.Row(
        [
            dbc.Col(
                html.Div(
                    [
                        dcc.Dropdown(
                            id='machine-type-dropdown',
                            options=[
                                {'label': k, 'value': k}
                                for k in valftoreeg.keys()
                            ],
                            value=list(valftoreeg.keys())[0],
                            style={
                                'color': 'white',
                                'width': 220,
                            },
                        )],style={"margin-top":18}),width =1),
            dbc.Col(
                html.Div(
                    [dcc.Dropdown(
                            id='machine-dropdown',
                            style={
                                'color': 'white',
                                'width': 220,
                            },
                            value='Analizörler'
                        )],style={"margin-top":18}),width =1),
            dbc.Col(
                html.Div(
                    [dcc.Dropdown(
                            id='date-dropdown',
                            options=[
                                {'label': i, 'value': i}
                                for i in ['Day', 'Month']
                            ],
                            style={
                                'color': 'white',
                                'font': {'color': '#2149b4'},
                                'width': 220,
                            },
                            value='month',
                        ),
                    ],
                    style={"margin-top":18},
                ),
                className="",width =1
            ),
            dbc.Col(
                html.Div(
                    [
                        dcc.DatePickerRange(
                            id='date-picker',
                            className="dash-date-picker-multi",
                            start_date=(date.today() - timedelta(weeks=1)).isoformat(),
                            end_date=(date.today()).isoformat(),
                            display_format='YYYY-MM-DD',
                            style={'color': '#212121'},
                            persistence=True,
                            persistence_type='session',
                        ),
                        html.Button(
                            'Search',
                            id='search',
                            className="dash-empty-button",
                            n_clicks=0,
                        ),
                        html.Button(
                            'Download',
                            id='download',
                            className="dash-empty-button",
                            n_clicks=0,
                        ),
                    ],
                ),style={"margin-left":100,"margin-top":15}
            ),
        ],style= {"margin-top":40,'border': '3px dashed blue',"margin-left":44}, className="g-0"
    ),
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col(
                    dcc.Graph(id="pie_chart", figure=return_pie()),
                    className="",style={"margin-top":49}
                ),
                dbc.Col(
                    html.Div([
                        dcc.Graph(id='example-graph', figure=fig),
                    ],style={"margin-left":75,"margin-top":49}),
                    className="",
                ),
            ]),

            dbc.Row([
                dash_table.DataTable(
                    id="data_table",
                    data=[],
                    columns=[],
                    filter_action='native',
                    style_cell={
                        "textAlign": "center",
                        "padding": "10px",
                        "color":"black",
                        'max-width': 100
                    },
                    style_table={
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
                    sort_action='native'
                ),
                dash_table.DataTable(
                    id="data_table_sum",
                    data=[],
                    columns=[],
                    style_cell={
                        "textAlign": "center",
                        "padding": "10px",
                        "color":"black",
                        'max-width': 115

                    },
                    style_table={
                        'margin': 'auto',
                        'borderCollapse': 'collapse',
                        "margin-top": "20px",
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
            ], style={"margin-top":75}, className="")
            ],width=7,style={"margin-left":"100px"}),

        dbc.Col(
            html.Div(id="wc-output-container_energy"),
            style={ "margin-top": 50}
        ,width=4)])
]



# Define the callback to update the second dropdown
@app.callback(
    Output('machine-dropdown', 'options'),
    Input('machine-type-dropdown', 'value')
)
def set_machine_options(selected_machine_type):
    if selected_machine_type in ["Bütün", "HAVALANDIRMA - FAN"]:
        return [{'label': v, 'value': k} for k, v in valftoreeg[selected_machine_type].items()]
    else:
        print("herehere")
        list_of_mpoints = [{'label': v, 'value': k} for k, v in valftoreeg[selected_machine_type].items()]
        list_of_mpoints.append({"label": "Hepsi", "value": "Hepsi"})
        print(list_of_mpoints)
        return list_of_mpoints


# @cache.memoize()
def update_table(s_date, f_date, costcenter, m_point, date_interval):
    if m_point == 'Bölümler':
        gruplamami = 1
    else:
        gruplamami = 0

    if date_interval == 'Day':
        with open(project_directory + f"\Charting\queries\energy_qandweight_daily.sql", 'r') as file:
            filedata = file.read()
    else:
        with open(project_directory + f"\Charting\queries\energy_qandweight.sql", 'r') as file:
            filedata = file.read()

        # f_date = datetime.strptime(f_date, "%Y-%m-%d")
        # f_date = str(f_date + relativedelta(months=+1))
        # final_month = int(f_date[5:7])
        # begin_month = int(s_date[5:7])
        # final_year = int(f_date[0:4])
        # begin_year = int(s_date[0:4])
        # start_date = datetime(begin_year, begin_month, 1)
        # end_date = datetime(final_year, final_month, 1)
    f_date = datetime.strptime(f_date, "%Y-%m-%d")
    s_date = datetime.strptime(s_date, "%Y-%m-%d")
    code_works = s_date.strftime('%Y-%m-%dT%H:%M:%S')
    code_worke = f_date.strftime('%Y-%m-%dT%H:%M:%S')
    start_date = s_date.strftime('%Y-%m-%d')
    end_date = f_date.strftime('%Y-%m-%d')

    # Extract the number of months and years in the difference

    df_final = pd.DataFrame()
    analizorler = []
    if costcenter != 'Bütün':
        if m_point == 'Hepsi':
            for m_point in valftoreeg[costcenter]:
                print(f"qsdsadasd{m_point}")
                analizorler.append((m_point, costcenter))
        else:
            analizorler.append((m_point, costcenter))
    else:
        analyzer = {}
        if m_point == 'Bölümler':

            my_keys = ["KURUTMA", "YUZEY ISLEM", "PRESHANE", "CNC", "ISIL ISLEM", "TASLAMA", "DOGRULTMA", "YIKAMA"]
            for costcenter_tmp in {key: valftoreeg[key] for key in my_keys}:
                analyzer.update(valftoreeg[costcenter_tmp])
                for m_point in valftoreeg[costcenter_tmp]:
                    analizorler.append((m_point, costcenter_tmp))

        else:
            for costcenter_tmp in valftoreeg:
                analyzer.update(valftoreeg[costcenter_tmp])
                for m_point in valftoreeg[costcenter_tmp]:
                    analizorler.append((m_point, costcenter_tmp))

    for m_point in analizorler:

        costcenter_tmp = m_point[1]
        m_point = m_point[0]
        print(f"*****{m_point}")

        if m_point == 'Bölümler' or m_point == 'Analizörler':
            continue
        if m_point == "K-13','K-18','K-19','K-20','K-21','K-22','K-23','K-25','K-27','K-28":
            m_point_tmp = '10 Kurutma'
        elif m_point == "T-19','T-20','T-21','T-22','T-23','T-24','T-25','T-26','T-27','T-34','T-37','T-43','T-44'," \
                        "'T-45":
            m_point_tmp = '14 Tambur'
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
        elif m_point == "S-03','V-01','V-02":
            m_point_tmp = "S-03,V-01,V-02"
        elif m_point == "OTEC-03','OTEC-04":
            m_point_tmp = "OTEC-03,OTEC-04"
        else:
            m_point_tmp = m_point

        print(f"mpointtmp={m_point_tmp}")

        # ENERJİ DATALARINI ÇEKİYORUZ!! ENERJİ DATALARINI ÇEKİYORUZ!! ENERJİ DATALARINI ÇEKİYORUZ!!
        # ENERJİ DATALARINI ÇEKİYORUZ!! ENERJİ DATALARINI ÇEKİYORUZ!! ENERJİ DATALARINI ÇEKİYORUZ!!
        # ENERJİ DATALARINI ÇEKİYORUZ!! ENERJİ DATALARINI ÇEKİYORUZ!! ENERJİ DATALARINI ÇEKİYORUZ!!

        if date_interval == 'Day':

            if m_point_tmp == '11 Pres (Pano 3 Diger)':
                df_works = ag.run_query(f"WITH ASD AS ( SELECT CAST(DATE AS DATETIME) AS DATE,"
                                        f"SUM(OUTPUT) as OUTPUT,"
                                        f"COSTCENTER,INTERVAL FROM VLFENERGY WHERE MPOINT IN "
                                        f"('PRES - Pano 1','8 Pres (Salter 2)','13 Pres (Salter 5)','4 Pres (Salter 3)') "
                                        f"AND  DATE >= '{code_works}' AND '{code_worke}' >= DATE "
                                        f"GROUP BY CAST(DATE AS DATETIME),COSTCENTER,INTERVAL )"
                                        f"SELECT '11 Pres (Pano 3 Diger)' AS MPOINT, OUTPUT,DATE,COSTCENTER from ASD ")
            # elif m_point_tmp == 'Hepsi':
            #     df_works = ag.run_query(f"SELECT CAST(DATE AS DATETIME) AS DATE,MPOINT,SCODE,"
            #                             f"OUTPUT,COSTCENTER,INTERVAL FROM VLFENERGY"
            #                             f" WHERE COSTCENTER = '{costcenter_tmp}' "
            #                             f"AND  DATE >= '{code_works}' AND '{code_worke}' >= DATE ")
            else:
                df_works = ag.run_query(f"SELECT CAST(DATE AS DATETIME) AS DATE,MPOINT,SCODE,"
                                        f"OUTPUT,COSTCENTER,INTERVAL FROM VLFENERGY"
                                        f" WHERE MPOINT = '{m_point_tmp}' "
                                        f"AND  DATE >= '{code_works}' AND '{code_worke}' >= DATE ")
        else:

            if m_point_tmp == '11 Pres (Pano 3 Diger)':
                df_works = ag.run_query(
                    f"WITH ASD AS ( SELECT LEFT(DATE, 4) + '-' + SUBSTRING(DATE, 6, 2)  AS DATE,MPOINT,OUTPUT as OUTPUT,"
                    f"COSTCENTER,INTERVAL FROM VLFENERGY WHERE MPOINT IN "
                    f"('PRES - Pano 1','8 Pres (Salter 2)','13 Pres (Salter 5)','4 Pres (Salter 3)')  )"
                    f" AND  DATE >= '{code_works}' AND '{code_worke}' >= DATE "
                    f"SELECT '11 Pres (Pano 3 Diger)' AS MPOINT, SUM(OUTPUT) AS OUTPUT,DATE,COSTCENTER FROM ASD GROUP BY DATE,COSTCENTER")
            elif m_point_tmp == 'Hepsi':
                df_works = ag.run_query(f"SELECT CAST(DATE AS DATETIME) AS DATE,MPOINT,SCODE,"
                                        f"OUTPUT,COSTCENTER,INTERVAL FROM VLFENERGY"
                                        f" WHERE COSTCENTER = '{costcenter_tmp}' "
                                        f"AND  DATE >= '{code_works}' AND '{code_worke}' >= DATE ")
            else:
                df_works = ag.run_query(f"SELECT LEFT(DATE, 4) + '-' + SUBSTRING(DATE, 6, 2)  AS DATE,MPOINT,SCODE,"
                                        f"SUM(OUTPUT) AS OUTPUT,COSTCENTER,INTERVAL FROM VLFENERGY"
                                        f" WHERE MPOINT = '{m_point_tmp}' "
                                        f"AND  DATE >= '{code_works}' AND '{code_worke}' >= DATE "
                                        f"GROUP BY LEFT(DATE, 4) + '-' + SUBSTRING(DATE, 6, 2),MPOINT,SCODE,COSTCENTER,INTERVAL")

        if df_works is None:
            continue
        if len(df_works) == 0:
            continue

        # URETIM DATALARINI ICIN SORGUNUN YAZILI OLDU TXT DOSYASINA GİDİYORUZ
        # URETIM DATALARINI ICIN SORGUNUN YAZILI OLDU TXT DOSYASINA GİDİYORUZ
        # URETIM DATALARINI ICIN SORGUNUN YAZILI OLDU TXT DOSYASINA GİDİYORUZ

        filedata_tmp = filedata.replace("xxxx-yy-zz", str(start_date))
        filedata_tmp = filedata_tmp.replace("aaaa-bb-cc", str(end_date))

        try:
            filedata_tmp = filedata_tmp.replace("XXMATERIALYY", "'" + m_point + "'")
        except (TypeError) as e:
            filedata_tmp = filedata_tmp.replace("XXMATERIALYY", "x")

        # manüpüle ettiğimiz sorguyu çalıştırıyoruz ve yeni bir sütun ekliyoruz.
        df_prddata = ag.run_query(filedata_tmp)

        df_prddata.rename(columns={"TOTALNETWEIGHT": "TOTALNETWEIGHT(ton)"}, inplace=True)
        df_prddata["MPOINT"] = m_point_tmp
        df_prddata["DATE"] = pd.to_datetime(df_prddata["DATE"])
        df_works["DATE"] = pd.to_datetime(df_works["DATE"])
        if len(df_prddata):

            df_works = df_works.merge(df_prddata, on=['MPOINT', 'DATE'], how='left').fillna(0)

        else:
            df_works["MPOINT"] = m_point_tmp
            df_wcs = ag.run_query(f"SELECT WORKCENTER FROM IASWORKCENT"
                                  f" WHERE  WORKCENTER IN ('{m_point}')")

            if len(df_wcs):
                df_works["QUANTITY"] = 0
                df_works["TOTALNETWEIGHT(ton)"] = 0.000
                df_works["kwhPERton"] = 0.000
            else:
                df_works["QUANTITY"] = None
                df_works["TOTALNETWEIGHT(ton)"] = None
                df_works["kwhPERton"] = None

        df_final = pd.concat([df_works, df_final]).drop_duplicates().reset_index(drop=True)

    # df_final[['DATE','MPOINT','OUTPUT']].to_excel(r"F:\pycarhm projects\Charting\outputs(xlsx)\ısıldatas.xlsx")

    df_final.rename(columns={"OUTPUT": "OUTPUT(KWH)"}, inplace=True)
    df_final["kwhPERton"] = df_final["kwhPERton"].astype(float)
    df_final["TOTALNETWEIGHT(ton)"] = df_final["TOTALNETWEIGHT(ton)"].astype(float)
    df_final["OUTPUT(KWH)"] = df_final["OUTPUT(KWH)"].astype(float)

    df_final["kwhPERton"] = df_final.apply(
        lambda x: x["OUTPUT(KWH)"] / x["TOTALNETWEIGHT(ton)"] if x["TOTALNETWEIGHT(ton)"] > 0 else 0, axis=1)
    df_final["kwhPERqty"] = df_final.apply(lambda x: x["OUTPUT(KWH)"] /
                                                     x["QUANTITY"] if x["QUANTITY"] else 0, axis=1)
    df_final["kwhPERton"] = df_final.apply(lambda x: x["kwhPERton"] if x["QUANTITY"] else None, axis=1)
    df_final["kwhPERqty"] = df_final.apply(lambda x: x["kwhPERqty"] if x["QUANTITY"] else None, axis=1)

    # if date_interval == 'month':
    #     df_final['DATE'] = df_final['DATE'].apply(lambda x: datetime.strptime(x, '%Y-%m'))

    df_final.sort_values(by=["DATE", "kwhPERton"], ascending=False, inplace=True)
    df_final = df_final[
        ["DATE", "COSTCENTER", "MPOINT", "TOTALNETWEIGHT(ton)", "OUTPUT(KWH)", "kwhPERton", "QUANTITY", "kwhPERqty"]]

    if gruplamami == 1:

        df_final["COSTCENTER"] = df_final.apply(lambda x: x["COSTCENTER"].replace(" ", ""), axis=1)
        print("*****")
        print(df_final)
        df_final = df_final.loc[
            ((df_final["COSTCENTER"].isin(['TASLAMA', 'DOGRULTMA', 'YIKAMA', 'ISILISLEM', 'YUZEYISLEM', 'KURUTMA'])) |
             (df_final["MPOINT"].isin(["5 CNC ve 4 Taslama (Pano 3)", "15 CNC (Pano 2)",
                                       "19 CNC (Pano 1)", 'PRES - Pano 3', 'PRES - Pano 2',
                                       'PRES - Pano 1'])))]

        if date_interval == 'Month':
            print("*****")
            print(df_final)
            df_final = df_final.groupby(["COSTCENTER", "DATE"]).agg({"TOTALNETWEIGHT(ton)": "sum",
                                                                     "OUTPUT(KWH)": "sum",
                                                                     "QUANTITY": "sum"})
            df_final.reset_index(inplace=True)

            # GETTING ALL PRESS PRODUCTION DATA WITH SUM
            with open(project_directory + f"\Charting\queries\energy_pres_monthly.sql", 'r') as file:
                filedata_pres = file.read()
            filedata_pres_tmp = filedata_pres.replace("xxxx-yy-zz", str(start_date))
            filedata_pres_tmp = filedata_pres_tmp.replace("aaaa-bb-cc", str(end_date))
            df_presuradet = ag.run_query(filedata_pres_tmp)

            df_presuradet["DATE"] = pd.to_datetime(df_presuradet["DATE"])

            # Convert "QUANTITY" column in df_final to int64 with error handling
            # Convert "TOTALNETWEIGHT" column in df_presuradet to float64 with error handling
            df_presuradet.rename(columns={"TOTALNETWEIGHT": "TOTALNETWEIGHT(ton)"}, inplace=True)

            df_final["QUANTITY"] = df_final["QUANTITY"].astype("int")
            df_presuradet["TOTALNETWEIGHT(ton)"] = df_presuradet["TOTALNETWEIGHT(ton)"].astype("float")
            df_presuradet["TOTALNETWEIGHT(ton)"] = df_presuradet["TOTALNETWEIGHT(ton)"].astype("float")

            df_final.loc[df_final["COSTCENTER"] == 'PRESHANE', "TOTALNETWEIGHT(ton)"] = list(
                df_presuradet["TOTALNETWEIGHT(ton)"])
            df_final.loc[df_final["COSTCENTER"] == 'PRESHANE', "QUANTITY"] = list(df_presuradet["QUANTITY"])

            df_final["MPOINT"] = 0.000
            df_final["kwhPERton"] = 0.000
            df_final["kwhPERqty"] = 0.000

            df_final["kwhPERton"] = df_final["OUTPUT(KWH)"] / df_final["TOTALNETWEIGHT(ton)"]
            df_final["kwhPERqty"] = df_final.apply(
                lambda x: x["OUTPUT(KWH)"] / x["QUANTITY"] if x["QUANTITY"] > 0 else 0,
                axis=1)
            df_final["kwhPERton"] = df_final["kwhPERton"].apply(lambda x: f"{x:.3f}" if x is not None else x)
            df_final["kwhPERqty"] = df_final["kwhPERqty"].apply(lambda x: f"{x:.5f}" if x is not None else x)
            df_final["TOTALNETWEIGHT(ton)"] = df_final["TOTALNETWEIGHT(ton)"].apply(lambda x: f"{x:.3f}")
            df_final["MPOINT"] = df_final["COSTCENTER"]
            df_final_sum = pd.DataFrame()

    else:
        df_final_sum = df_final.loc[(df_final["OUTPUT(KWH)"] > 0.00) & (df_final["QUANTITY"] > 0)]

        df_final_sum = df_final_sum.iloc[0:0]

        df_final_sum.loc[len(df_final_sum.index)] = (
            '0000-00-00T00:00:00+00:00', "ALL", "ALL", df_final["TOTALNETWEIGHT(ton)"].sum(),
            df_final["OUTPUT(KWH)"].sum(), 0.000, df_final["QUANTITY"].sum(), 0.000)
        df_final["kwhPERton"] = df_final["kwhPERton"].apply(lambda x: f"{x:.3f}" if x is not None else x)
        df_final["kwhPERqty"] = df_final["kwhPERqty"].apply(lambda x: f"{x:.5f}" if x is not None else x)
        df_final_sum["kwhPERton"] = df_final_sum["OUTPUT(KWH)"] / df_final_sum["TOTALNETWEIGHT(ton)"]
        df_final_sum["kwhPERqty"] = df_final_sum.apply(
            lambda x: x["OUTPUT(KWH)"] / x["QUANTITY"] if x["QUANTITY"] > 0 else 0,
            axis=1)
        df_final_sum["kwhPERton"] = df_final_sum["kwhPERton"].apply(lambda x: f"{x:.3f}" if x is not None else x)
        df_final_sum["kwhPERqty"] = df_final_sum["kwhPERqty"].apply(lambda x: f"{x:.5f}" if x is not None else x)
        df_final["TOTALNETWEIGHT(ton)"] = df_final["TOTALNETWEIGHT(ton)"].apply(lambda x: f"{x:.3f}")

    df_final["OUTPUT(KWH)"] = df_final["OUTPUT(KWH)"].apply(lambda x: '{:.2f}'.format(x))
    df_final.rename(columns={"COSTCENTER": "Prod.Process"}, inplace=True)
    df_final.rename(columns={"MPOINT ": "MPoint.Analyser"}, inplace=True)

    return df_final.to_json(date_format='iso', orient='split'), \
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
     State('date-dropdown', 'value'),
     Input('search', 'n_clicks')]
)
def cache_to_result(s_date, f_date, costcenter, m_point, date_interval, button):
    if button <= 0:
        raise PreventUpdate

    df_final, df_final_sum = update_table(s_date, f_date, costcenter, m_point, date_interval)
    df_final = pd.read_json(df_final, orient='split')
    df_final_sum = pd.read_json(df_final_sum, orient='split')
    columns = [{"name": i, "id": i} for i in df_final.columns]
    columns2 = [{"name": i, "id": i} for i in df_final_sum.columns]
    excel_data = pd.concat([df_final, df_final_sum]).to_json(date_format='iso', orient='split')
    return df_final.to_dict("records"), columns \
        , df_final_sum.to_dict("records"), columns2, \
        excel_data


@app.callback(
    Output("wc-output-container_energy", "children"),
    [Input("data_table", "data")]
)
def line_graph_update(data):
    # Convert the input data to a DataFrame
    df = pd.DataFrame(data)
    df.sort_values(by="DATE", ascending=False, inplace=True)
    fig_combined_perton = go.Figure()
    fig_combined_perqty = go.Figure()
    fig_combined_cons = go.Figure()

    # Add trace for kwhPERton
    traces_perton = []
    traces_perqty = []
    traces_cons = []

    for m_point in df["MPOINT"].unique():
        print(m_point)
        df_tmp = df.loc[df["MPOINT"] == m_point]

        fig_combined_perton.add_trace(
            go.Scatter(x=df_tmp["DATE"], y=df_tmp["kwhPERton"], mode='lines+markers', name=m_point))

        # Add trace for kwhPERqty
        fig_combined_perqty.add_trace(
            go.Scatter(x=df_tmp["DATE"], y=df_tmp["kwhPERqty"] * 1000, mode='lines+markers', name=m_point))

        # Add trace for kwhPERqty
        fig_combined_cons.add_trace(
            go.Scatter(x=df_tmp["DATE"], y=df_tmp["OUTPUT(KWH)"], mode='lines+markers', name=m_point))

        # Update layout
    fig_combined_perton.update_layout(
        title='Energy Consumption Per Ton',
        xaxis_title='Date',
        yaxis_title='Consumption Per Ton',
        legend_title="Metrics",
        paper_bgcolor=layout_color,
        plot_bgcolor='rgba(0, 0, 0, 0)'
    )
    fig_combined_perqty.update_layout(
        title='Energy Consumption Per Quantity',
        xaxis_title='Date',
        yaxis_title='Consumption Per Quantıy',
        legend_title="Metrics",
        paper_bgcolor=layout_color,
        plot_bgcolor='rgba(0, 0, 0, 0)'
    )
    fig_combined_cons.update_layout(
        title='Energy Consumption Comparison',
        xaxis_title='Date',
        yaxis_title='Energy Consumption',
        legend_title="Metrics",
        paper_bgcolor=layout_color,
        plot_bgcolor='rgba(0, 0, 0, 0)'
    )

    return html.Div(children=[dcc.Graph(figure=fig_combined_perton), dcc.Graph(figure=fig_combined_perqty),
                              dcc.Graph(figure=fig_combined_cons)])


@app.callback(
    Output("download-energy", "data"),
    Input("download", "n_clicks"),
    State(component_id='generated_data', component_property='data'),
    prevent_initial_call=True
)
def generate_excel(n_clicks, generated_data):
    generated_data = pd.read_json(generated_data, orient='split')
    if n_clicks < 1:
        raise PreventUpdate

    return dcc.send_data_frame(generated_data.to_excel, "energydata.xlsx", index=False)
