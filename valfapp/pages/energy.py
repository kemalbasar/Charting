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


layout = [
    # dbc.Button("Day", id="btn-day_en", n_clicks=0, color="primary", className='day-button'),
    # dbc.Button("Week", id="btn-week1_en", n_clicks=0, color="primary", className='week-button'),
    # dbc.Button("Month", id="btn-month1_en", n_clicks=0, color="primary", className='month-button'),
    # dbc.Button("Year", id="btn-year1_en", n_clicks=0, color="primary", className='year-button'),

    dcc.Store(id='generated_data'), dcc.Download(id="download-energy"),
    dbc.Row(html.H1("Valfsan Production Energy Consumption",
                    style={'text-align': 'center', "fontFamily": 'Arial Black', 'fontSize': 30,
                           'backgroundColor': '#f0f0f0'})),
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dcc.Link(
                        children='Main Page',
                        href='/',
                        style={"color": "black", "font-weight": "bold"}
                    ),
                    html.Br(),
                    html.Br(),
                    html.Div(
                        [
                            # Div for dropdowns and date pickers
                            html.Div(
                                [
                                    dbc.Row([dcc.Dropdown(
                                        id='machine-type-dropdown',
                                        options=[{'label': k, 'value': k} for k in valftoreeg.keys()],
                                        value=list(valftoreeg.keys())[0],  # Default value
                                        style={'color': 'yellow', "width": 150}
                                    ),
                                        html.Br(),
                                        dcc.Dropdown(
                                            id='machine-dropdown',
                                            style={'color': 'yellow', "width": 220},
                                            value='Analizörler'
                                        )]),
                                    dcc.Dropdown(
                                        id='date-dropdown',
                                        options=['day', 'month'],
                                        style={'color': 'yellow', 'font': {'color': 'white'}, "width": 150},
                                        value='month'
                                    ),
                                    html.Br(),
                                    dcc.DatePickerRange(
                                        id='date-picker',
                                        className="dash-date-picker-multi",
                                        start_date=(date.today() - timedelta(weeks=1)).isoformat(),
                                        end_date=(date.today()).isoformat(),
                                        display_format='YYYY-MM-DD',
                                        style={'color': '#212121'},
                                        persistence=True, persistence_type='session'
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
                                    ),
                                    html.Button(
                                        'Download',
                                        id='download',
                                        className="dash-empty-button",
                                        n_clicks=0,
                                    )
                                ],
                                style={'display': 'inline-block', 'textAlign': 'center'}
                            )
                        ],

                    )], width=3),
                dbc.Col([
                    dcc.Graph(id="pie_chart", figure=return_pie())], width=4),
                dbc.Col([dcc.Graph(id='example-graph', figure=fig)], width=2)
            ]),
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
        dbc.Col([
            html.Div(id="wc-output-container_energy"), ]
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
    if selected_machine_type not in ["KURUTMA", "YUZEY ISLEM", "PRESHANE", "CNC", "ISIL ISLEM"]:
        return [{'label': v, 'value': k} for k, v in valftoreeg[selected_machine_type].items()]
    else:
        list_of_mpoints = [{'label': v, 'value': k} for k, v in valftoreeg[selected_machine_type].items()]
        list_of_mpoints.append({"label": "Hepsi", "value": "Hepsi"})
        print(list_of_mpoints)
        return [{'label': v, 'value': k} for k, v in valftoreeg[selected_machine_type].items()]


# @cache.memoize()
def update_table(s_date, f_date, costcenter, m_point, date_interval):
    if m_point == 'Bölümler':
        gruplamami = 1
    else:
        gruplamami = 0

    if date_interval == 'day':
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
        analizorler.append((m_point, costcenter))
    else:
        analyzer = {}
        if m_point == 'Bölümler':

            my_keys = ["KURUTMA", "YUZEY ISLEM", "PRESHANE", "CNC", "ISIL ISLEM", "TASLAMA", "DOGRULTMA", "YIKAMA"]
            for costcenter_tmp in {key: valftoreeg[key] for key in my_keys}:
                analyzer.update(valftoreeg[costcenter_tmp])
                for m_point in valftoreeg[costcenter_tmp]:
                    analizorler.append((m_point, costcenter_tmp))
        elif m_point == 'Hepsi':
            for costcenter_tmp in valftoreeg[costcenter]:
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
        elif m_point == "T-19','T-20','T-21','T-22','T-23','T-24','T-25','T-26','T-27','T-34','T-37','T-43','T-44','T-45":
            m_point_tmp = '10 Tambur'
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

        if date_interval == 'day':

            if m_point_tmp == '11 Pres (Pano 3 Diger)':
                df_works = ag.run_query(f"WITH ASD AS ( SELECT CAST(DATE AS DATETIME) AS DATE,"
                                        f"SUM(OUTPUT) as OUTPUT,"
                                        f"COSTCENTER,INTERVAL FROM VLFENERGY WHERE MPOINT IN "
                                        f"('PRES - Pano 1','8 Pres (Salter 2)','13 Pres (Salter 5)','4 Pres (Salter 3)') "
                                        f"AND  DATE >= '{code_works}' AND '{code_worke}' >= DATE "
                                        f"GROUP BY CAST(DATE AS DATETIME),COSTCENTER,INTERVAL )"
                                        f"SELECT '11 Pres (Pano 3 Diger)' AS MPOINT, OUTPUT,DATE,COSTCENTER from ASD ")
            elif m_point_tmp == 'Hepsi':
                df_works = ag.run_query(f"SELECT CAST(DATE AS DATETIME) AS DATE,MPOINT,SCODE,"
                                        f"OUTPUT,COSTCENTER,INTERVAL FROM VLFENERGY"
                                        f" WHERE COSTCENTER = '{costcenter_tmp}' "
                                        f"AND  DATE >= '{code_works}' AND '{code_worke}' >= DATE ")
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

        if date_interval == 'month':
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
        legend_title="Metrics"
    )
    fig_combined_perqty.update_layout(
        title='Energy Consumption Per Quantity',
        xaxis_title='Date',
        yaxis_title='Consumption Per Quantıy',
        legend_title="Metrics"
    )
    fig_combined_cons.update_layout(
        title='Energy Consumption Comparison',
        xaxis_title='Date',
        yaxis_title='Energy Consumption',
        legend_title="Metrics"
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
