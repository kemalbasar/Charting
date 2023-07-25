### Import Packages ###
import logging
import pandas as pd
from flask import request,g
from flask_caching import Cache
import dash
import dash_bootstrap_components as dbc
from valfapp.functions.functions_prd import calculate_oeemetrics, apply_nat_replacer, get_gann_data
from run.agent import ag
from config import project_directory

logger = logging.getLogger(__name__)


### Dash instance ###
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.PULSE],
    suppress_callback_exceptions=True)

app.css.append_css({
    "external_url": (
        "https://cdnjs.cloudflare.com/ajax/libs/"
        "twitter-bootstrap/4.5.0/css/bootstrap.css"
    ),
    "raw": ".row-cols {margin-right: -0.5rem; margin-left: -0.5rem;}"
})

cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})
@app.server.before_request
def before_request():
    user_agent = request.user_agent
    if user_agent.platform in ["android", "iphone", "ipad"]:
        g.device_type = "Mobile"
    else:
        g.device_type = "Desktop"

TIMEOUT = 12000


@cache.memoize(timeout=TIMEOUT)
def prdconf(params = None):
    print(params)
    paramswith = params[0:2]
    prd_conf = ag.run_query(query = r"EXEC VLFPRODALLINONEWPARAMS @WORKSTART=?, @WORKEND=?", params=paramswith)
    print(prd_conf)
    planned_hoursx = pd.read_excel(project_directory + r"\Charting\valfapp\assets\GunlukPlanlar.xlsx", sheet_name='adetler')
    onemonth_prdqty = ag.run_query(query = r"EXEC VLFPROCPRDFORSPARKLINES @WORKSTART=?, @WORKEND=?, @DATEPART=?", params=params)
    # prd_conf["DISPLAY"] = [prd_conf["DISPLAY"][row][0]  for row in prd_conf.index]
    prd_conf["BREAKDOWNSTART"] = prd_conf.apply(lambda row: apply_nat_replacer(row["BREAKDOWNSTART"]), axis=1)
    prd_conf = pd.merge(prd_conf, planned_hoursx, how='left',
                        on=['WORKCENTER', "SHIFT", "MATERIAL"])
    prd_conf["LABOUR"] = prd_conf.apply(lambda row: apply_nat_replacer(row["LABOUR"]), axis=1)

    prd_conf["ADET"] = [0 if not prd_conf["ADET"][row] > 0 else prd_conf["ADET"][row] for row in prd_conf.index]
    prd_conf["IDEALCYCLETIME"] = prd_conf["IDEALCYCLETIME"].astype("float")
    prd_conf["LABOUR"] =  [99 if prd_conf["LABOUR"][row] == 'nan' else prd_conf["LABOUR"][row] for row in prd_conf.index]
    prd_conf["LABOUR"] = pd.to_numeric(prd_conf["LABOUR"], errors='coerce')
    prd_conf["IDEALCYCLETIME"] = [prd_conf["IDEALCYCLETIME"][row] if prd_conf["LABOUR"][row] == 99 else prd_conf["IDEALCYCLETIME"][row] * (
                prd_conf["SELLAB"][row] / prd_conf["LABOUR"][row]) for row in prd_conf.index]
    # prd_conf.to_excel(project_directory + r"\Charting\valfapp\assets\prd_conf.xlsx")
    prd_conf["PLANNEDTIME"] = [prd_conf["ADET"][row] * prd_conf["IDEALCYCLETIME"][row] \
                               / prd_conf["QTY"][row] if prd_conf["ADET"][row] != 0 else
                               prd_conf["TOTALTIME"][row] for row in prd_conf.index]
    summary_helper = prd_conf[prd_conf["CONFTYPE"] == 'Uretim'].groupby(["WORKCENTER", "SHIFT", "MATERIAL"])\
        .agg({"IDEALCYCLETIME": "sum","RUNTIME": "sum"})
    summary_helper.reset_index(inplace=True)
    summary_helper["RATER"] = summary_helper["IDEALCYCLETIME"]/summary_helper["RUNTIME"]
    summary_helper["BADDATA_FLAG"] = [3 if summary_helper["RATER"][row] > 1.2 else 0 for row in range(len(summary_helper))]
    summary_helper = summary_helper[["WORKCENTER", "SHIFT", "MATERIAL", "BADDATA_FLAG"]]
    prd_conf = pd.merge(prd_conf, summary_helper, on=['MATERIAL', 'SHIFT', 'WORKCENTER'], how='left')
    prd_conf["BADDATA_FLAG"] = [ 1 if prd_conf["MACHINE"][row] == 0
        else 2 if ((prd_conf["TOTALTIME"][row] != 0) &
                   (prd_conf["TOTALTIME"][row] <= 3) &
                   (prd_conf["QTY"][row] > 3))
        else 3 if prd_conf["BADDATA_FLAG"][row] == 3
        else 0 for row in range(len(prd_conf))]


    details, df_metrics, df_metrics_forwc, df_metrics_forpers= calculate_oeemetrics(df=prd_conf[prd_conf["BADDATA_FLAG"]==0])
    for item in details:
        try:
            details[item]["OEE"] = (100 * details[item]["OEE"])
            details[item]["OEE"] = details[item]["OEE"].astype(int)
            details[item]['OEE'] = details[item]['OEE'].apply(lambda x: str(x) + ' %')
        except TypeError as e:
            print(f"Error: {e}")
            print(details)
            continue
    gann_data = get_gann_data(df=prd_conf)

    df_baddatas = prd_conf.loc[prd_conf["BADDATA_FLAG"] != 0,["COSTCENTER","MATERIAL","QTY","CONFIRMATION"
                ,"CONFIRMPOS","WORKSTART","WORKEND","BADDATA_FLAG"]]
    df_baddatas["CONFIRMATION"] = df_baddatas["CONFIRMATION"].astype('str')
    df_baddatas.drop_duplicates(inplace=True)
    df_baddata_rates = prd_conf[prd_conf["CONFTYPE"] == "Uretim"].groupby(["COSTCENTER", "BADDATA_FLAG"]).agg({"BADDATA_FLAG": "count"})
    df_baddata_rates = df_baddata_rates.rename(columns={'BADDATA_FLAG': 'SUMS'})
    df_baddata_rates.reset_index(inplace=True)

    return [{item: details[item].to_json(date_format='iso', orient='split')
             for item in details.keys()},
            df_metrics.to_json(date_format='iso', orient='split'),
            gann_data.to_json(date_format='iso', orient='split'),
            df_metrics_forwc.to_json(date_format='iso', orient='split'),
            df_baddatas.to_json(date_format='iso', orient='split'),
            df_baddata_rates.to_json(date_format='iso', orient='split'),
            onemonth_prdqty.to_json(date_format='iso', orient='split'),
            df_metrics_forpers.to_json(date_format='iso', orient='split')
            ]


@cache.memoize(timeout=TIMEOUT)
def oee(params = None):

    oee, metrics, gann_data, df_metrics_forwc, \
        df_baddatas,df_baddata_rates,onemonth_prdqty,df_metrics_forpers = prdconf(params)
    oee = {k: pd.read_json(v, orient='split') for k, v in oee.items()}
    metrics = pd.read_json(metrics, orient='split')
    gann_data = pd.read_json(gann_data, orient='split')
    df_metrics_forwc = pd.read_json(df_metrics_forwc, orient='split')
    df_baddatas = pd.read_json(df_baddatas, orient='split')
    df_baddata_rates = pd.read_json(df_baddata_rates, orient='split')
    onemonth_prdqty = pd.read_json(onemonth_prdqty, orient='split')
    df_metrics_forpers = pd.read_json(df_metrics_forpers, orient='split')
    result = (oee, metrics, gann_data, df_metrics_forwc,df_baddatas,df_baddata_rates,onemonth_prdqty,df_metrics_forpers)
    cache.set('oee_cached_data', result)
    return result


if __name__ == "__main__":
    app.run(debug=True)
