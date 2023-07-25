from config import project_directory
from valfapp.configuration import daily_work_minute
from canias_web_services import get_work_hour
import pandas as pd
import datetime as dt
import numpy as np
import warnings
import plotly.express as px
import plotly.graph_objs as go
import flask_caching

warnings.filterwarnings("ignore")

pd.set_option('display.float_format', lambda x: '%.2f' % x)
pd.set_option('display.width', 500)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 500)


def weighted_average(x,df_metrics):
    weights = df_metrics.loc[x.index, "PLANNEDTIME"]
    if np.sum(weights) == 0:
        # Handle the case when the sum of the weights is zero
        # You can return a default value, raise an exception, or do whatever makes sense in your context
        return np.mean(x)  # Returning mean as an example
    else:
        return np.average(x, weights=weights)

def apply_nat_replacer(x):
    x = str(x)
    if x == 'NaT':
        x = 'nat_replaced'
    else:
        x = x
    return x


########### ########### ########### ###################### ########### ########### ########### ###########
########### ########### ########### ########### SQL QUERIES START##### ########### ########### ##########
########### ########### ########### ########### ########### ########### ########### ########### ##########

# taking workcenter list from database
# ag = Agent(parse_wclist_querry())
prd_conf = ''
planned_hours = ''
working_machines = ''
onemonth_prdqty = ''

########### ########### ########### ###################### ########### ########### ########### ###########
########### ########### ########### ########### SQL QUERIES END ######## ########### ########### ##########
########### ########### ########### ########### ########### ########### ########### ########### ##########


def working_machinesf(working_machines = working_machines, costcenter='CNC'):
    return working_machines.loc[working_machines["COSTCENTER"] == costcenter, "COUNTOFWC"].tolist()


def calculate_oeemetrics(df=prd_conf, df_x = pd.DataFrame(),piechart_data=1, shiftandmat=0):
    df = df.loc[df["WORKCENTER"] != "CNC-24", ["COSTCENTER", "MATERIAL", "SHIFT", "CONFIRMATION", "CONFIRMPOS",
                                               "QTY", "SCRAPQTY", "REWORKQTY","ADET","LABOUR",
                                               "WORKCENTER", "RUNTIME", "TOTALTIME",
                                               "TOTFAILURETIME", "SETUPTIME", "IDEALCYCLETIME","PLANNEDTIME","STEXT","SCRAPTEXT","DISPLAY"]]

    df.drop_duplicates(inplace=True,subset=['CONFIRMATION', 'CONFIRMPOS'])
    df.reset_index(drop=True, inplace=True)
    df["SCRAPTEXT"] = df["SCRAPTEXT"].astype(str)
    df["DISPLAY"] = df["DISPLAY"].astype(str)

    def custom_agg(group):
        agg_dict = {
            "QTY": group['QTY'].sum(),
            "SCRAPQTY": group['SCRAPQTY'].sum(),
            "REWORKQTY": group['REWORKQTY'].sum(),
            "RUNTIME": group['RUNTIME'].sum(),
            "TOTALTIME": group['TOTALTIME'].sum(),
            "TOTFAILURETIME": group['TOTFAILURETIME'].sum(),
            "IDEALCYCLETIME": group['IDEALCYCLETIME'].sum(),
            "SETUPTIME": group['SETUPTIME'].sum(),
            "PLANNEDTIME": group['PLANNEDTIME'].sum() if (group['ADET'] == 0).any() else group['PLANNEDTIME'].max(),
            "DISPLAY": group['DISPLAY'].max(),
            "SCRAPTEXT": group['SCRAPTEXT'].max(),
        }
        return pd.Series(agg_dict)

    df_metrics = df.groupby(["WORKCENTER", "COSTCENTER", "MATERIAL", "SHIFT"]).apply(custom_agg)

    df_metrics.reset_index(inplace=True)
    # df_metrics_backup = df_metrics.copy()
    # df_metrics = df_metrics_backup
    df_metrics["IDEALCYCLETIME"] = df_metrics["IDEALCYCLETIME"].astype(float)
    df_metrics["TOTFAILURETIME"] = df_metrics["TOTFAILURETIME"].astype(float)


        # buraya machine ile çarpılmış halini otomatik getireceğiz.

    df_metrics["NANTIME"] = df_metrics["PLANNEDTIME"] - df_metrics["TOTALTIME"]
    # There will be counter for broken data.
    df_metrics["NANTIME"] = [0 if df_metrics["NANTIME"][row] < 0
                             else df_metrics["NANTIME"][row] for row in
                             range(len(df_metrics))]
    df_metrics = df_metrics[df_metrics["NANTIME"] > -200]
    df_metrics.reset_index(inplace=True, drop=True)
    df_metrics["PERFORMANCE"] = [
        0 if df_metrics["RUNTIME"][row] <= 0
        else df_metrics["IDEALCYCLETIME"][row] / df_metrics["RUNTIME"][row] for row
        in range(len(df_metrics))]
    df_metrics["AVAILABILITY"] = df_metrics["RUNTIME"] / df_metrics["TOTALTIME"]

    df_metrics["AVAILABILITY"] = [1 if df_metrics["AVAILABILITY"][row] > 1
                                  else df_metrics["AVAILABILITY"][row] for row in range(len(df_metrics))]
    df_metrics["QUALITY"] = df_metrics["QTY"] / (df_metrics["QTY"] + df_metrics["SCRAPQTY"]
                                                 + df_metrics["REWORKQTY"])
    df_metrics["QUALITY"] = [0 if str(df_metrics["QUALITY"][row]) == 'nan'
                             else df_metrics["QUALITY"][row] for row in range(len(df_metrics))]
    df_metrics["OEE"] = df_metrics["QUALITY"] * df_metrics["AVAILABILITY"] * \
                        (df_metrics["PERFORMANCE"])
    df_metrics["TOTFAILURETIME"] = df_metrics["TOTFAILURETIME"] - df_metrics["SETUPTIME"]
    # df_metrics["PERFORMANCEWITHWEIGHT"] = df_metrics["PERFORMANCE"] * df_metrics["VARD"]
    # df_metrics["PERFORMANCEWITHWEIGHT"].sum() / df_metrics["VARD"].sum()
    weights = df_metrics.loc[df_metrics.index, "PLANNEDTIME"]
    weights[weights <= 0] = 1

    def weighted_average(x):
        # Use the updated weights
        return np.average(x, weights=weights.loc[x.index])

    wm = lambda x: weighted_average(x)
    df_metrics.fillna(0, inplace=True)
    # df_metrics["FLAG_BADDATA"] = [1 if df_metrics["PERFORMANCE"][row]> 1.2 else 0
    #                               for row in df_metrics.index]
    df_metrics_forwc = df_metrics.copy()


    df_metrics = df_metrics.groupby(["WORKCENTER", "COSTCENTER"]).agg({"QTY": "sum",
                                                                "SCRAPQTY": "sum",
                                                                "REWORKQTY": "sum",
                                                                "RUNTIME": "sum",
                                                                "TOTALTIME": "sum",
                                                                "TOTFAILURETIME": "sum",
                                                                "IDEALCYCLETIME": "sum",
                                                                "SETUPTIME": "sum",
                                                                "NANTIME": "sum",
                                                                "PLANNEDTIME": "sum",
                                                                "PERFORMANCE": wm,
                                                                "AVAILABILITY": wm,
                                                                "OEE": wm
                                                               })
    df_metrics.reset_index(inplace=True)


    try:
        df_piechart = df_metrics.groupby("COSTCENTER").agg({"RUNTIME": "sum",
                                                            "TOTFAILURETIME": "sum",
                                                            "SETUPTIME": "sum",
                                                            "NANTIME": "sum",
                                                            "PERFORMANCE": wm,
                                                            "AVAILABILITY": wm,
                                                            "OEE": wm})
    except ZeroDivisionError:
        return None

    if piechart_data == 0:
        return df_piechart

    details = {"CNC": None,
               "TASLAMA": None,
               "CNCTORNA": None,
               "MONTAJ": None,
               "PRESHANE1" : None,
               "PRESHANE2" : None,}

    f = lambda a: round(((abs(a) + a) / 2), 3)
    g = lambda a: int((a * 100) / sum_of)
    # h = lambda a: 1 if a > 1 else a

    for costcenter in ['CNC', "TASLAMA", "CNCTORNA", "MONTAJ","PRESHANE1","PRESHANE2"]:
        sum_of = df_piechart.loc[costcenter, "RUNTIME"] + df_piechart.loc[costcenter, "TOTFAILURETIME"] + \
                 df_piechart.loc[costcenter, "SETUPTIME"] + df_piechart.loc[costcenter, "NANTIME"]

        temp_dic = {
            'RATES': [f(1 - df_piechart.loc[costcenter, "PERFORMANCE"]) * g(df_piechart.loc[costcenter, "RUNTIME"]),
                      g(df_piechart.loc[costcenter, "TOTFAILURETIME"]),
                      g(df_piechart.loc[costcenter, "SETUPTIME"]),
                      g(df_piechart.loc[costcenter, "NANTIME"]),
                      # h(df_piechart.loc[costcenter, "PERFORMANCE"]) * g(df_piechart.loc[costcenter, "RUNTIME"]),
                      (100 - (f(1 - df_piechart.loc[costcenter, "PERFORMANCE"]) * g(
                          df_piechart.loc[costcenter, "RUNTIME"]) +
                              g(df_piechart.loc[costcenter, "TOTFAILURETIME"]) +
                              g(df_piechart.loc[costcenter, "SETUPTIME"]) +
                              g(df_piechart.loc[costcenter, "NANTIME"])))
                      ],
            'OEE': [round(df_piechart.loc[costcenter, "OEE"], 3),
                    round(df_piechart.loc[costcenter, "OEE"], 3),
                    round(df_piechart.loc[costcenter, "OEE"], 3),
                    round(df_piechart.loc[costcenter, "OEE"], 3),
                    round(df_piechart.loc[costcenter, "OEE"], 3)],
            'MACHINE': ["PRD", "DOWN", "SETUP", "NAN", "PRD"],
            'OPR': ["FAIL", None, None, None, "SUCCES"]
        }
        df_piechart_final = pd.DataFrame(temp_dic,
                                         index=['SESSIONTIME', 'PLANSIZDURUS', 'SETUP', 'NaN', "SESSIONTIME2"])
        # })
        for index in list(df_piechart_final.index):
            if df_piechart_final["RATES"][index] == 0:
                df_piechart_final["RATES"][index] = 1
            if df_piechart_final["MACHINE"][index] == 0:
                df_piechart_final["MACHINE"][index] = 1
                # df_piechart_final.drop(index, axis=0, inplace=True)
        #        df_piechart_final["OPR"]["SESSIONTIME"] = str(int(df_piechart_final["OPR"]["SESSIONTIME"])) + '%'
        #        df_piechart_final["OPR"]["SESSIONTIME2"] = str(int(df_piechart_final["OPR"]["SESSIONTIME2"])) + '%'
        df_piechart_final.rename(index={'SESSIONTIME2': 'SESSIONTIME'}, inplace=True)
        details[costcenter] = df_piechart_final
    return details, df_metrics, df_metrics_forwc


# df_oee, df_metrics = calculate_oeemetrics()


# def year_summary(dirof_prd=project_directory + r"\Charting\queries\prdt_report_foryear_calculatıon.sql",
#                  dirof_plan=project_directory + r"\Charting\queries\planned_hours_foryerar_calculation.sql"):
#     df_final = pd.DataFrame(
#         columns=['RUNTIME', 'TOTFAILURETIME', 'SETUPTIME', 'NANTIME', 'PERFORMANCE', 'AVAILABILITY', 'OEE',
#                  'COSTCENTER', 'DATEOFY'])
#     date_ofy_f = dt.date(2022, 1, 6)
#     date_ofy_s = date_ofy_f - dt.timedelta(days=1)
#     for i in range(364):
#         # sorguları çektiğimiz yeri değiştirtik, burdaki verilere parametre olarak düzenlenecek
#         df_prd = ag.editandrun_query(dirof_prd, ["xxxx-yy-zz", "aaaa-bb-cc"], [str(date_ofy_s), str(date_ofy_f)])
#         df_plan = ag.editandrun_query(dirof_plan, ["xxxx-yy-zz", "aaaa-bb-cc"], [str(date_ofy_s), str(date_ofy_f)])
#
#         if len(df_prd) == 0 or len(df_plan) == 0:
#             # print(date_ofy_s)
#             date_ofy_s += dt.timedelta(days=1)
#             date_ofy_f += dt.timedelta(days=1)
#             continue
#
#         df_metrics = calculate_oeemetrics(df=df_prd, planned_hoursx=df_plan, piechart_data=0)
#         if df_metrics is None:
#             # print(date_ofy_s)
#             date_ofy_s += dt.timedelta(days=1)
#             date_ofy_f += dt.timedelta(days=1)
#             continue
#
#         df_metrics["COSTCENTER"] = df_metrics.index
#         df_metrics.reset_index(inplace=True, drop=True)
#         df_metrics["DATEOFY"] = date_ofy_s
#         df_final = df_final.append(df_metrics)
#         date_ofy_s += dt.timedelta(days=1)
#         date_ofy_f += dt.timedelta(days=1)
#
#     df_final.to_excel(project_directory + r"\Charting\outputs(xlsx)\2022_machine_performances.xlsx")
#
#     return df_final


def generate_for_sparkline(data='',proses='CNC', type='TOPLAM', ppm=False):
    if type == 'HURDA':
        data["HURDA"] = data["HURDA"].astype(int)
    if not ppm:
        df = pd.DataFrame(data[data["COSTCENTER"] == proses][type])
        df.reset_index(inplace=True)
        df.drop("index", axis=1, inplace=True)
        return df[type].tolist()
    else:
        df = pd.DataFrame(data[data["COSTCENTER"] == proses])
        df["PPM"] = (df["HURDA"] / df["TOPLAM"]) * 1000000
        return df["PPM"].tolist()


def get_daily_qty(df=prd_conf, costcenter='CNC', type="QTY", ppm=False):

    df = df.loc[((df["CONFTYPE"] == "Uretim"))].groupby(["COSTCENTER"]).agg(
        {"QTY": "sum", "SCRAPQTY": "sum"})
    df.reset_index(inplace=True)
    if not ppm:
        return str(df.loc[df["COSTCENTER"] == costcenter, type].values[0])
    else:
        return int(int(df.loc[df["COSTCENTER"] == costcenter, ["SCRAPQTY"]].values) / \
                   int(df.loc[
                           df["COSTCENTER"] == costcenter, ["QTY"]].values) * 1000000)


def scatter_plot(df=prd_conf, report_day="2022-07-26"):
    # df["BREAKDOWNSTART"] = df.apply(lambda row: apply_nat_replacer(row["BREAKDOWNSTART"]), axis=1)
    # df = df.loc[(((df["BREAKDOWNSTART"] != "nat_replaced")) & (df["COSTCENTER"] == costcenter))]

    # df["WORKEND"] = df["WORKEND"].apply(lambda x : str(x))
    df = df.loc[df["CONFTYPE"] != 'Uretim',
                ["WORKSTART", "WORKCENTER", "FAILURETIME", 'SETUPTIME',"STEXT", "CONFTYPE"]]
    df["FAILURETIME"] = df.apply(lambda row: apply_nat_replacer(row["FAILURETIME"]), axis=1)
    df["FAILURETIME"] = [df["FAILURETIME"][row] if df["FAILURETIME"][row] != "nan" else df["SETUPTIME"][row] for row in df.index]

    df.reset_index(inplace=True, drop=True)
    df.sort_values(by="WORKCENTER", inplace=True)
    df["STEXT"] = [df["CONFTYPE"][row] if df["CONFTYPE"][row] == 'Kurulum'\
        else df["STEXT"][row] for row in df.index]
    df["FAILURETIME"] = df["FAILURETIME"].astype(float)
    df_legend = df.groupby(["STEXT"]).agg({"FAILURETIME":sum})
    df_legend.reset_index(inplace=True)
    df_legend = df_legend.sort_values(by="FAILURETIME", ascending=False)
    category_order = list(df_legend["STEXT"])
    return df,category_order


def get_gann_data(df=prd_conf):
    cols = ['MATERIAL', 'COSTCENTER', 'QTY', 'BREAKDOWN', 'PERSONELNUM', 'WORKCENTER', 'BREAKDOWNSTART', 'BREAKDOWNEND',
            'STEXT', 'CONFTYPE','FAILURETIME','RUNTIME',"SCRAPQTY","SETUPTIME"]
    df_helper = df.copy()
    df_helper.drop(["BREAKDOWNSTART", "BREAKDOWNEND"], axis=1, inplace=True)
    df_helper = df_helper.rename(columns={"WORKSTART": "BREAKDOWNSTART",
                                          "WORKEND": "BREAKDOWNEND"})
    df_helper = df_helper.loc[
        ((df_helper["STEXT"].isnull()) | (df_helper["BREAKDOWN"] == 10) |
         (df_helper["CONFTYPE"] == 'Kurulum')), cols]
    df_helper.reset_index(inplace=True, drop=True)
    df_helper["CONFTYPE"] = ["Uretim" if ((df_helper["CONFTYPE"][row] == 'Plansiz Durus')
                                          | (df_helper["CONFTYPE"][row] == 'Ariza Durusu')
                                          | (df_helper["CONFTYPE"][row] == 'Planli Durus'))
                             else df_helper["CONFTYPE"][row] for row in range(df_helper.shape[0])]

    df_helper["BREAKDOWN"] = 11
    df["BREAKDOWNSTART"] = df.apply(lambda row: apply_nat_replacer(row["BREAKDOWNSTART"]), axis=1)
    df = df.loc[(df["BREAKDOWNSTART"] != "nat_replaced"), cols]
    df_final = pd.concat([df, df_helper])
    df_final.reset_index(inplace=True, drop=True)
    # print(df_final)
    df_final["CONFTYPE"] = ["Uretim" if ((df_final["BREAKDOWN"][row]) == 11 & (df_final["CONFTYPE"][row] != 'Kurulum'))
                            else df_final["CONFTYPE"][row] for row in range(df_final.shape[0])]
    df_final = df_final.rename(columns={"BREAKDOWNSTART": "WORKSTART", "BREAKDOWNEND": "WORKEND"})
    df_final = df_final.astype({"WORKSTART": 'datetime64[ns]'})
    df_final.reset_index(inplace=True)
    df_final.drop("index", inplace=True, axis=1)
    df_final.sort_values(by="WORKCENTER", inplace=True)
    return df_final


# def calculate_work_hours(df=get_gann_data()):
#     df["NET_WORKING_TIME1"] = [get_work_hour(df["WORKCENTER"][row], df["WORKSTART"][row], df["WORKEND"][row]) for row in
#                                range(df.shape[0])]

def return_ind_fig(df_metrics=None,df_details = pd.DataFrame(), costcenter='CNC', order=0, colorof='green',coloroftext='black'):
    text = ''
    if df_metrics is None:
        return None
    if type(order) != str:
        df_metrics = df_metrics.sort_values(by="OEE", ascending=False)
        df_metrics.reset_index(inplace=True, drop=True)
        l_card = df_metrics.iloc[order]
        final_card = df_metrics.loc[df_metrics["WORKCENTER"] == l_card['WORKCENTER']]

    else:
        final_card = df_metrics.loc[df_metrics["WORKCENTER"] == order]
    # text = f"{final_card['WORKCENTER']} worked {int(final_card['AVAILABILITY'] * 100)}% of planned time." \
    #        f"Operater <br> processed {int(final_card['QTY'] - (final_card['QTY'] * final_card['RUNTIME']) / final_card['IDEALCYCLETIME'])} " \
    #        f"more material then avarge <br> with only {final_card['SCRAPQTY']} scrap"

    if len(df_details) != 0:
        df_ann = df_details.loc[df_details["WORKCENTER"] == order,["SHIFT","DISPLAY","SCRAPQTY","SCRAPTEXT"]]
        df_ann.drop_duplicates(inplace=True, subset=['SHIFT', 'DISPLAY'], keep='first')
        text = ''
        for index, row in df_ann.iterrows():
            text += f"{row['SHIFT']}.Var:{row['DISPLAY']} <br>"


    if colorof == 'green':
        colorof2 = coloroftext
    else:
        colorof2 = coloroftext

    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=final_card['OEE'].values[0] * 100 ,
        title={
            "text": f"{final_card['WORKCENTER'].values[0]}</span><br><span style='font-size:1em;color:gray'>"},
        gauge={
            'axis': {'range': [None, 150]},
            'bar': {'color': colorof, "thickness": 1},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "black",
            'steps': [
                {'range': [0, 33], 'color': 'white'},
                {'range': [33, 80], 'color': 'white'},
                {'range': [81, 100], 'color': 'white'},
                {'range': [100, 120], 'color': 'white'}
            ],
            'threshold': {
                'line': {'color': "orange", 'width': 6},
                'thickness': 1,
                'value': 80
            }
        },
        number={'suffix': '%'}

        #       delta={'reference': 400, 'relative': True, "font": {"size": 40}},
        #        domain={'x': [0, 1], 'y': [0, 1]}
    ))

    annotation = {
        "height": 600,
        "width": 2000,
        'x':0.55,  # If we consider the x-axis as 100%, we will place it on the x-axis with how many %
        'y':-0.3,  # If we consider the y-axis as 100%, we will place it on the y-axis with how many %
        'text': text,
        # 'showarrow': True,
        # 'arrowhead': 3,
        'font': {'size': 10, 'color': colorof2}
    }

    fig.update_layout({
        "annotations": [annotation],
        # title={
        # # 'text': text,
        # # 'y': 1,
        # # 'x': 0.5,
        # # 'font': {'size': 17}
        # },
        "paper_bgcolor": "rgba(0,0,0,0)", "width": 350, "height": 320})

    return fig

#this metod takes manufacturing companies workcenter data,status refers to the status of the workcenter and it definess backgroundcolor,
#text refers to the text to be displayed on the indicator graph.
#workcenter refers to the workcenter of the manufacturing company, it will be on header
def return_indicatorgraph(status='white',fullname='',
                          workcenter='',material='',durus='',target=0):

    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=target,

        gauge={
            'axis': {'range': [None, 150]},
            'bar': {'color': "black", "thickness": 1},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "black",
            'steps': [
                {'range': [0, 33], 'color': 'white'},
                {'range': [33, 80], 'color': 'white'},
                {'range': [81, 100], 'color': 'white'},
                {'range': [100, 150], 'color': 'white'}
            ],
            'threshold': {
                'line': {'color': "orange", 'width': 6},
                'thickness': 1,
                'value': 80
            }
        },
        number={'suffix': None }

        #       delta={'reference': 400, 'relative': True, "font": {"size": 40}},
        #        domain={'x': [0, 1], 'y': [0, 1]}
    ))

    annotation = {
        "height": 600,
        "width": 2000,
        'x': 0.15,  # If we consider the x-axis as 100%, we will place it on the x-axis with how many %
        'y': 1,  # If we consider the y-axis as 100%, we will place it on the y-axis with how many %
        'text': fullname,
        # 'showarrow': True,
        # 'arrowhead': 3,
        'font': {'size': 24, 'color': 'black'}
    }
    annotation1 = {
        "height": 600,
        "width": 2000,
        'x': 0.99,  # If we consider the x-axis as 100%, we will place it on the x-axis with how many %
        'y': 0.99,  # If we consider the y-axis as 100%, we will place it on the y-axis with how many %
        'text': material,
        # 'showarrow': True,
        # 'arrowhead': 3,
        'font': {'size': 24, 'color': 'black'}
    }
    annotation2 = {
        "height": 600,
        "width": 2000,
        'x': 0.5,  # If we consider the x-axis as 100%, we will place it on the x-axis with how many %
        'y': 0.75,  # If we consider the y-axis as 100%, we will place it on the y-axis with how many %

        'text': '(' + str(durus) + ')',
        # 'showarrow': True,
        # 'arrowhead': 3,
        'font': {'size': 20, 'color': 'black'}
    }

    fig.update_layout({
        "annotations": [annotation,annotation1,annotation2],
        "title" : dict(
        text=workcenter,
        x=0.5,  # Change the x position (0 = left, 0.5 = center, 1 = right)
        y=0.81,
        font = dict(
        size=55
        )
    ),"paper_bgcolor": status, "width": 607, "height": 850})

    return fig