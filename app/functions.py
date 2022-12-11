from app.configuration import daily_work_minute
from run.agent import Agent, parse_wclist_querry
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

# taking workcenter list from database
ag = Agent(parse_wclist_querry())
wc_list = ag.df
# taking placement list of workcenters from database
wc_usage = ag.run_querry("SELECT STAND FROM IASROU009 WHERE STAND != '*'")
# Perfomance data of operaters and workcenters.
prd_summary = ag.run_querry(r"C:\Users\kereviz\PycharmProjects\Charting\queries\production_times.txt")
# Production Quantities.
daily_prdqty = ag.run_querry(r"C:\Users\kereviz\PycharmProjects\Charting\queries\production_quantity.txt")
# Production Means.
means_prdqty = ag.run_querry(r"C:\Users\kereviz\PycharmProjects\Charting\queries\avgofqty.txt")
# 1 month of daily data of production
onemonth_prdqty = ag.run_querry(
    r"SELECT * FROM VLFDAILYPRDQUANTITIES WHERE WORKEND > CAST(DATEADD(DAY,-30,GETDATE()) AS DATE)")
# Working Machines
working_machines = ag.run_querry(r"C:\Users\kereviz\PycharmProjects\Charting\queries\working_workcenter.txt")
working_machines = working_machines["COUNTOFWC"].tolist()
# Daily Confirmations
prd_conf = ag.run_querry(r"C:\Users\kereviz\PycharmProjects\Charting\queries\prdt_report1.sql")


def generate_for_sparkline(proses='FR', type='TOPLAM', ppm=False):
    if not ppm:
        df = pd.DataFrame(onemonth_prdqty[onemonth_prdqty["PROSES"] == proses][type])
        df.reset_index(inplace=True)
        df.drop("index", axis=1, inplace=True)
        return df[type].tolist()
    else:
        df = pd.DataFrame(onemonth_prdqty[onemonth_prdqty["PROSES"] == proses])
        df["PPM"] = (df["HURDA"] / df["TOPLAM"]) * 1000000
        return df["PPM"].tolist()


def production_quantities(df1=daily_prdqty, df2=means_prdqty):
    if len(daily_prdqty) == 0:
        return df2
    else:
        return pd.merge(df1, df2, on='PROSES', how='left')


def get_daily_qty(process='FR', type="TOPLAM", ppm=False):
    if not ppm:
        return str(production_quantities().loc[production_quantities()["PROSES"] == process, type].values[0])
    else:
        return int(int(production_quantities().loc[production_quantities()["PROSES"] == 'FR', ["HURDA"]].values) / \
                   int(production_quantities().loc[
                           production_quantities()["PROSES"] == 'FR', ["TOPLAM"]].values) * 1000000)


def get_mean_prdqty(process='FR'):
    return round(production_quantities().loc[production_quantities()["PROSES"] == "FR", "M_TOPLAM"].values[0], 1)


def production_times(df, report_day="2022-07-21", workcenter=None):
    summary_df = df[df["SHIFT"] == 0].groupby("TDATE").agg({"ADET": "sum",
                                                            "SESSIONTIME": "sum",
                                                            "PLANSIZDURUS": "sum",
                                                            "SETUP": "sum",
                                                            "URETIMVERIM": "mean"
                                                            })

    summary_df.reset_index(inplace=True)
    summary_df["MAKINA_VERIM"] = 100 * (summary_df["SESSIONTIME"]) / daily_work_minute

    return summary_df[summary_df["TDATE"] == report_day]


def df_for_sunburst(df=prd_summary, report_day="2022-07-26"):
    df = production_times(df, report_day)
    df_sum = df.T
    df_sum.drop(["TDATE", "ADET"], inplace=True)
    df_sum.columns = ["RATES"]
    df_sum["RATES"][0:3] = [100 * (df_sum["RATES"][row] / daily_work_minute) if df_sum["RATES"][row] != 0 else None for
                            row in [0, 1, 2]]
    df_sum = df_sum.applymap(lambda x: round(x, 0))
    df_sum = pd.concat([df_sum, pd.DataFrame(
        {"RATES": [100 - int(df_sum["RATES"][0:3].sum()),
                   df_sum["RATES"][3] * df_sum["RATES"][4] / 100]}, index=["NaN", "OEE"])]
                       )
    df_sum = df_sum.applymap(lambda x: int(x))
    df_sum["OEE"] = [int((df_sum["RATES"]["URETIMVERIM"] * df_sum["RATES"]["MAKINA_VERIM"]) / 100) if df_sum["RATES"][
                                                                                                          row] is not None else None
                     for row in df_sum.index]
    # df_sum["RATES"]["OEE"] = 100 - df_sum["RATES"]["MAKINA_VERIM"]
    df_sum.loc[7] = [int(df_sum.iloc[0, 0] * df_sum.iloc[3, 0] / 100), 53]
    df_sum = df_sum.rename(index={7: 'SESSIONTIME'})
    df_sum.iloc[0, 0] = df_sum.iloc[0, 0] - df_sum.iloc[7, 0]
    df_sum["MACHINE"] = [df_sum["RATES"]["MAKINA_VERIM"], df_sum["RATES"]["PLANSIZDURUS"], 1,
                         None, None, df_sum["RATES"]["NaN"], None, df_sum["RATES"]["MAKINA_VERIM"]]

    df_sum["OPR"] = [100 - df_sum["RATES"]["URETIMVERIM"], None, None, None, None, None, None,
                     df_sum["RATES"]["URETIMVERIM"]]
    df_sum.drop(["URETIMVERIM", "MAKINA_VERIM", "OEE"], axis=0, inplace=True)
    print(df_sum)

    if df_sum["RATES"]["SETUP"] == 0:
        df_sum.drop("SETUP", axis=0, inplace=True)
    return df_sum


def scatter_plot(df=prd_summary, report_day="2022-07-26"):
    df = df[(df["TDATE"] == report_day) & (df["FAILURETEXT"] != '')]
    # df["WORKEND"] = df["WORKEND"].apply(lambda x : str(x))
    failure_summary_df = pd.DataFrame(
        df.groupby(["WORKEND", "WORKCENTER", "FAILURETEXT", "DRAWNUM", "DISPLAY"])["PLANSIZDURUS"].sum())
    failure_summary_df.reset_index(inplace=True)
    failure_sum_df = failure_summary_df[np.array(failure_summary_df.columns)[[0, 1, 5, 2, 3, 4]]]
    print(failure_sum_df)
    return ag.draw_bubblechart(df=failure_sum_df)


def apply_nat_replacer(x):
    x = str(x)
    if x == 'NaT':
        x = 'nat_replaced'
    else:
        x = x
    return x


def get_gann_data(df=prd_conf, work_day="2022-07-26"):
    cols = ['MATERIAL', 'COSTCENTER', 'QTY', 'BREAKDOWN', 'PERSONELNUM', 'WORKCENTER', 'BREAKDOWNSTART', 'BREAKDOWNEND',
            'STEXT', 'CONFTYPE']
    df_helper = df.copy()
    df_helper.drop(["BREAKDOWNSTART", "BREAKDOWNEND"], axis=1, inplace=True)
    df_helper = df_helper.rename(columns={"WORKSTART": "BREAKDOWNSTART", "WORKEND": "BREAKDOWNEND"})
    df_helper = df_helper.loc[df_helper["STEXT"].isnull(), cols]
    df["BREAKDOWNSTART"] = df.apply(lambda row: apply_nat_replacer(row["BREAKDOWNSTART"]), axis=1)
    df = df.loc[df["BREAKDOWNSTART"] != "nat_replaced", cols]
    df_final = pd.concat([df, df_helper])
    df_final["STEXT"] = ["PROD" if df_final["STEXT"][row] is None else df_final["STEXT"][row] for row in
                         range(df_final.shape[0])]
    df_final = df_final.rename(columns={"BREAKDOWNSTART": "WORKSTART", "BREAKDOWNEND": "WORKEND"})
    df_final = df_final.astype({"WORKSTART": 'datetime64[ns]'})
    df_final.reset_index(inplace=True)
    df_final.drop("index", inplace=True, axis=1)
    return df_final


def calculate_work_hours(df=get_gann_data()):
    df["NET_WORKING_TIME1"] = [get_work_hour(df["WORKCENTER"][row], df["WORKSTART"][row], df["WORKEND"][row]) for row in
                               range(df.shape[0])]
