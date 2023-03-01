from valfapp.configuration import daily_work_minute
from run.agent import ag
from canias_web_services import get_work_hour
import pandas as pd
import datetime as dt
import numpy as np
import warnings

warnings.filterwarnings("ignore")

pd.set_option('display.float_format', lambda x: '%.2f' % x)
pd.set_option('display.width', 500)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)


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
wc_list = ag.df
# taking placement list of workcenters from database
wc_usage = ag.run_query("SELECT STAND FROM IASROU009 WHERE STAND != '*'")
# 1 month of daily data of production
onemonth_prdqty = ag.run_query(
    r"SELECT * FROM VLFDAILYPRDQUANTITIES WHERE WORKEND > CAST(DATEADD(DAY,-30,GETDATE()) AS DATE)")
# Working Machines
working_machines = ag.run_query(r"C:\Users\kereviz\PycharmProjects\Charting\queries\working_workcenter.txt")
# Daily Confirmations
prd_conf = ag.run_query(r"C:\Users\kereviz\PycharmProjects\Charting\queries\prdt_report1.sql")
prd_conf["BREAKDOWNSTART"] = prd_conf.apply(lambda row: apply_nat_replacer(row["BREAKDOWNSTART"]), axis=1)
planned_hours = ag.run_query(r"C:\Users\kereviz\PycharmProjects\Charting\queries\planned_hours.sql")

########### ########### ########### ###################### ########### ########### ########### ###########
########### ########### ########### ########### SQL QUERIES END ######## ########### ########### ##########
########### ########### ########### ########### ########### ########### ########### ########### ##########


def working_machinesf(costcenter='CNC'):
    return working_machines.loc[working_machines["COSTCENTER"] == costcenter, "COUNTOFWC"].tolist()


def calculate_oeemetrics(df=prd_conf, planned_hoursx=planned_hours, piechart_data=1):
    df = df.loc[
        df["WORKCENTER"] != "CNC-24", ["COSTCENTER", "CONFIRMATION", "CONFIRMPOS", "QTY", "SCRAPQTY", "REWORKQTY",
                                       "WORKCENTER", "RUNTIME", "TOTALTIME", "TOTFAILURETIME", "SETUPTIME",
                                       "IDEALCYCLETIME"]]
    df.drop_duplicates(inplace=True)
    df.reset_index(drop=True, inplace=True)
    df_metrics = df.groupby(["WORKCENTER", "COSTCENTER"]).agg({"QTY": "sum",
                                                               "SCRAPQTY": "sum",
                                                               "REWORKQTY": "sum",
                                                               "RUNTIME": "sum",
                                                               "TOTALTIME": "sum",
                                                               "TOTFAILURETIME": "sum",
                                                               "IDEALCYCLETIME": "sum",
                                                               "SETUPTIME": "sum"})
    df_metrics.reset_index(inplace=True)
    # df_metrics_backup = df_metrics.copy()
    # df_metrics = df_metrics_backup
    df_metrics = pd.merge(df_metrics, planned_hoursx, how='left', on='WORKCENTER')
    df_metrics["NANTIME"] = df_metrics["VARD"] * 420 - df_metrics["TOTALTIME"]
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
    df_metrics["AVAILABILITY"] = df_metrics["RUNTIME"] / (420 * df_metrics["VARD"])
    df_metrics["QUALITY"] = df_metrics["QTY"] / (df_metrics["QTY"] + df_metrics["SCRAPQTY"]
                                                 + df_metrics["REWORKQTY"])
    df_metrics["QUALITY"] = [0 if str(df_metrics["QUALITY"][row]) == 'nan'
                             else df_metrics["QUALITY"][row] for row in range(len(df_metrics))]
    df_metrics["OEE"] = df_metrics["QUALITY"] * df_metrics["AVAILABILITY"] * \
                        df_metrics["PERFORMANCE"]
    df_metrics["TOTFAILURETIME"] = df_metrics["TOTFAILURETIME"] - df_metrics["SETUPTIME"]
    # df_metrics["PERFORMANCEWITHWEIGHT"] = df_metrics["PERFORMANCE"] * df_metrics["VARD"]
    # df_metrics["PERFORMANCEWITHWEIGHT"].sum() / df_metrics["VARD"].sum()
    wm = lambda x: np.average(x, weights=df_metrics.loc[x.index, "VARD"])
    df_metrics.fillna(0, inplace=True)
    df_metrics = min_max_scale(df_metrics,0.61,0.97)

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
               "CNCTORNA": None}

    f = lambda a: round(((abs(a) + a) / 2), 3)
    g = lambda a: int((a * 100) / sum_of)
    h = lambda a: 1 if a > 1 else a

    for costcenter in ['CNC', "TASLAMA", "CNCTORNA"]:
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
    return details, df_metrics


def year_summary(dirof_prd=r"C:\Users\kereviz\PycharmProjects\Charting\queries\prdt_report_foryear_calculatıon.sql",
                 dirof_plan=r"C:\Users\kereviz\PycharmProjects\Charting\queries\planned_hours_foryerar_calculation.sql"):
    df_final = pd.DataFrame(
        columns=['RUNTIME', 'TOTFAILURETIME', 'SETUPTIME', 'NANTIME', 'PERFORMANCE', 'AVAILABILITY', 'OEE',
                 'COSTCENTER', 'DATEOFY'])
    date_ofy_f = dt.date(2022, 1, 6)
    date_ofy_s = date_ofy_f - dt.timedelta(days=1)
    for i in range(364):
        df_prd = ag.editandrun_query(dirof_prd, ["xxxx-yy-zz", "aaaa-bb-cc"], [str(date_ofy_s), str(date_ofy_f)])
        df_plan = ag.editandrun_query(dirof_plan, ["xxxx-yy-zz", "aaaa-bb-cc"], [str(date_ofy_s), str(date_ofy_f)])

        if len(df_prd) == 0 or len(df_plan) == 0:
            # print(date_ofy_s)
            date_ofy_s += dt.timedelta(days=1)
            date_ofy_f += dt.timedelta(days=1)
            continue

        df_metrics = calculate_oeemetrics(df=df_prd, planned_hoursx=df_plan, piechart_data=0)
        if df_metrics is None:
            # print(date_ofy_s)
            date_ofy_s += dt.timedelta(days=1)
            date_ofy_f += dt.timedelta(days=1)
            continue

        df_metrics["COSTCENTER"] = df_metrics.index
        df_metrics.reset_index(inplace=True, drop=True)
        df_metrics["DATEOFY"] = date_ofy_s
        df_final = df_final.append(df_metrics)
        date_ofy_s += dt.timedelta(days=1)
        date_ofy_f += dt.timedelta(days=1)

    df_final.to_excel(r"C:\Users\kereviz\PycharmProjects\Charting\outputs(xlsx)\2022_machine_performances.xlsx")

    return df_final


def generate_for_sparkline(proses='FR', type='TOPLAM', ppm=False):
    if proses == 'CNC':
        proses = 'FR'
    elif proses == 'CNCTORNA':
        proses = 'TR'
    elif proses == 'TASLAMA':
        proses = 'TS'
    if not ppm:
        df = pd.DataFrame(onemonth_prdqty[onemonth_prdqty["PROSES"] == proses][type])
        df.reset_index(inplace=True)
        df.drop("index", axis=1, inplace=True)
        return df[type].tolist()
    else:
        df = pd.DataFrame(onemonth_prdqty[onemonth_prdqty["PROSES"] == proses])
        df["PPM"] = (df["HURDA"] / df["TOPLAM"]) * 1000000
        return df["PPM"].tolist()


def get_daily_qty(costcenter='CNC', type="QTY", ppm=False):
    df = prd_conf
    df = df.loc[((df["BREAKDOWNSTART"] == "nat_replaced") | (df["BREAKDOWN"] == 10))].groupby(["COSTCENTER"]).agg(
        {"QTY": "sum", "SCRAPQTY": "sum"})
    df.reset_index(inplace=True)
    if not ppm:
        return str(df.loc[df["COSTCENTER"] == costcenter, type].values[0])
    else:
        return int(int(df.loc[df["COSTCENTER"] == costcenter, ["SCRAPQTY"]].values) / \
                   int(df.loc[
                           df["COSTCENTER"] == costcenter, ["QTY"]].values) * 1000000)


def scatter_plot(df=prd_conf, report_day="2022-07-26", costcenter='CNC'):
    df["BREAKDOWNSTART"] = df.apply(lambda row: apply_nat_replacer(row["BREAKDOWNSTART"]), axis=1)
    df = df.loc[(((df["BREAKDOWNSTART"] != "nat_replaced")) & (df["COSTCENTER"] == costcenter))]

    # df["WORKEND"] = df["WORKEND"].apply(lambda x : str(x))
    df = df[["BREAKDOWNSTART", "WORKCENTER", "FAILURETIME", "STEXT", "CONFTYPE"]]
    df.reset_index(inplace=True, drop=True)
    df.sort_values(by="FAILURETIME", inplace=True)
    return ag.draw_bubblechart(df=df)


def get_gann_data(df=prd_conf, work_day="2022-07-26", costcenter='CNC'):
    cols = ['MATERIAL', 'COSTCENTER', 'QTY', 'BREAKDOWN', 'PERSONELNUM', 'WORKCENTER', 'BREAKDOWNSTART', 'BREAKDOWNEND',
            'STEXT', 'CONFTYPE']
    df = df.loc[df["COSTCENTER"] == costcenter]
    df_helper = df.copy()
    df_helper.drop(["BREAKDOWNSTART", "BREAKDOWNEND"], axis=1, inplace=True)
    df_helper = df_helper.rename(columns={"WORKSTART": "BREAKDOWNSTART", "WORKEND": "BREAKDOWNEND"})
    df_helper = df_helper.loc[
        ((df_helper["STEXT"].isnull()) | (df_helper["BREAKDOWN"] == 10) | (df_helper["CONFTYPE"] == 'SETUP')), cols]
    df_helper.reset_index(inplace=True, drop=True)
    df_helper["CONFTYPE"] = ["PROD" if df_helper["CONFTYPE"][row] == 'BREAKDOWN'
                             else df_helper["CONFTYPE"][row] for row in range(df_helper.shape[0])]

    df_helper["BREAKDOWN"] = 11
    df["BREAKDOWNSTART"] = df.apply(lambda row: apply_nat_replacer(row["BREAKDOWNSTART"]), axis=1)
    df = df.loc[(df["BREAKDOWNSTART"] != "nat_replaced"), cols]
    df_final = pd.concat([df, df_helper])
    df_final.reset_index(inplace=True, drop=True)
    # print(df_final)
    df_final["CONFTYPE"] = ["PROD" if ((df_final["BREAKDOWN"][row]) == 11 & (df_final["CONFTYPE"][row] != 'SETUP'))
                            else df_final["CONFTYPE"][row] for row in range(df_final.shape[0])]
    df_final = df_final.rename(columns={"BREAKDOWNSTART": "WORKSTART", "BREAKDOWNEND": "WORKEND"})
    df_final = df_final.astype({"WORKSTART": 'datetime64[ns]'})
    df_final.reset_index(inplace=True)
    df_final.drop("index", inplace=True, axis=1)
    df_final.sort_values(by= 'WORKCENTER', inplace= True)
    # print(df_final)
    return df_final

# def calculate_work_hours(df=get_gann_data()):
#     df["NET_WORKING_TIME1"] = [get_work_hour(df["WORKCENTER"][row], df["WORKSTART"][row], df["WORKEND"][row]) for row in
#                                range(df.shape[0])]

def min_max_scale(df, new_min, new_max):

    for costcenter in ["CNC","CNCTORNA","TASLAMA"]:
        data = df[df["COSTCENTER"] == costcenter]["OEE"]
        min_value = np.min(data)
        max_value = np.max(data)
        df.loc[df["COSTCENTER"] == costcenter,"OEE"] = \
            list(np.around(((data - min_value) / (max_value - min_value) * (new_max - new_min) + new_min),decimals=2,out=None))

    return df