### Import Packages ###
import dash
import dash_bootstrap_components as dbc
from flask_caching import Cache
from valfapp.functions.functions_prd import calculate_oeemetrics, apply_nat_replacer, get_gann_data
from run.agent import ag
import pandas as pd
from config import project_directory



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

TIMEOUT = 20

@cache.memoize(timeout=TIMEOUT)
def prdconf():
    prd_conf = ag.run_query(r"EXEC [VLFPRODALLINONE]")
    planned_hoursx = pd.read_excel(project_directory + r"\Charting\valfapp\assets\GunlukPlanlar.xlsx", sheet_name='adetler')
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

    prd_conf["BADDATA_FLAG"] = [ 1 if prd_conf["BADDATA_FLAG"][row] == 1
        else 2 if ((prd_conf["RUNTIME"][row] != 0) &
                   (prd_conf["IDEALCYCLETIME"][row] / prd_conf["RUNTIME"][row] > 1.2) &
                   (prd_conf["RUNTIME"][row] <= 3))
        else 3 if ((prd_conf["RUNTIME"][row] != 0) &
                   (prd_conf["IDEALCYCLETIME"][row] / prd_conf["RUNTIME"][row] > 1.2) &
                   (prd_conf["RUNTIME"][row] > 3))
        else 0 for row in range(len(prd_conf))]
    print(prd_conf)
    details, df_metrics, df_metrics_forwc = calculate_oeemetrics(df=prd_conf[prd_conf["BADDATA_FLAG"]==0])
    print(details)
    for item in details:
        details[item]["OEE"] = (100 * details[item]["OEE"])
        details[item]["OEE"] = details[item]["OEE"].astype(int)
        details[item]['OEE'] = details[item]['OEE'].apply(lambda x: str(x) + ' %')
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
            df_baddata_rates.to_json(date_format='iso', orient='split')
            ]


@cache.memoize(timeout=TIMEOUT)
def oee():
    cached_data = cache.get('oee_cached_data')
    if cached_data is not None:
        return cached_data

    oee, metrics, gann_data, df_metrics_forwc, df_baddatas,df_baddata_rates = prdconf()
    oee = {k: pd.read_json(v, orient='split') for k, v in oee.items()}
    metrics = pd.read_json(metrics, orient='split')
    gann_data = pd.read_json(gann_data, orient='split')
    df_metrics_forwc = pd.read_json(df_metrics_forwc, orient='split')
    df_baddatas = pd.read_json(df_baddatas, orient='split')
    df_baddata_rates = pd.read_json(df_baddata_rates, orient='split')
    result = (oee, metrics, gann_data, df_metrics_forwc,df_baddatas,df_baddata_rates)
    cache.set('oee_cached_data', result)
    return result


if __name__ == "__main__":
    app.run(debug=True)
