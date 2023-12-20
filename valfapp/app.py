### Import Packages ###
import json
import logging
import numpy as np
import pandas as pd
from pandas.errors import IntCastingNaNError
from dash import ClientsideFunction, Output, Input
from flask_caching import Cache
import dash
import dash_bootstrap_components as dbc
from valfapp.functions.functions_prd import calculate_oeemetrics, apply_nat_replacer, get_gann_data, indicator_with_color
from run.agent import ag
from config import project_directory
import plotly.express as px  # (version 4.7.0 or higher)


MAX_OUTPUT = 25
summary_color = 'black'

logger = logging.getLogger(__name__)

### Dash instance ###

app = dash.Dash(
    __name__,
    meta_tags=[{'name': 'viewport',
                'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'}],
    external_scripts=["https://cdnjs.cloudflare.com/ajax/libs/dragula/3.7.2/dragula.min.js"],
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
    'CACHE_DIR': project_directory + r'\Charting\valfapp\cache-directory'
})

TIMEOUT = 12000


@cache.memoize(timeout=TIMEOUT)
def prdconf(params=None):
    paramswith = params[0:2]
    prd_conf = ag.run_query(query=r"EXEC VLFPRODALLINONEWPARAMS @WORKSTART=?, @WORKEND=?", params=paramswith)
    onemonth_prdqty = ag.run_query(query=r"EXEC VLFPROCPRDFORSPARKLINES @WORKSTART=?, @WORKEND=?, @DATEPART=?",
                                   params=params)
    if len(prd_conf) == 0:
        return [None, None, None, None, None, None, None, None]
    prd_conf["BREAKDOWNSTART"] = prd_conf.apply(lambda row: apply_nat_replacer(row["BREAKDOWNSTART"]), axis=1)
    prd_conf["IDEALCYCLETIME"] = prd_conf["IDEALCYCLETIME"].astype("float")
    prd_conf["WORKDAY"] = prd_conf["WORKSTART"].dt.date

    non_times = prd_conf.loc[
        ((prd_conf["FAILURECODE"] == 'U033') & (prd_conf["BREAKDOWN"] == 10)
         | (prd_conf["FAILURECODE"] == 'M031')), ["COSTCENTER", "CONFIRMATION", "CONFIRMPOS", "FAILURETIME", "WORKDAY",
                                                  "WORKCENTER",
                                                  "SHIFT", "BREAKDOWN"]]

    non_times = non_times.groupby(["COSTCENTER", "WORKCENTER", "WORKDAY", "SHIFT"]).agg({"FAILURETIME": "sum"})
    non_times.reset_index(inplace=True)
    non_times.columns = ["COSTCENTER", "WORKCENTER", "WORKDAY", "SHIFT", "OMTIME"]

    summary_helper = prd_conf[prd_conf["CONFTYPE"] == 'Uretim'].groupby(["WORKCENTER", "SHIFT", "MATERIAL"]) \
        .agg({"IDEALCYCLETIME": "sum", "RUNTIME": "sum"})


    summary_helper.reset_index(inplace=True)
    summary_helper["RATER"] = summary_helper["IDEALCYCLETIME"] / summary_helper["RUNTIME"]
    summary_helper["BADDATA_FLAG"] = [3 if summary_helper["RATER"][row] > 1.2 else 0 for row in
                                      range(len(summary_helper))]
    summary_helper = summary_helper[["WORKCENTER", "SHIFT", "MATERIAL", "BADDATA_FLAG"]]
    prd_conf = pd.merge(prd_conf, summary_helper, on=['MATERIAL', 'SHIFT', 'WORKCENTER'], how='left')
    prd_conf["BADDATA_FLAG"] = [
        0 if "PRES" in prd_conf["COSTCENTER"][row] else
        (1 if prd_conf["MACHINE"][row] == 0 else
         2 if ((prd_conf["TOTALTIME"][row] != 0) and (prd_conf["TOTALTIME"][row] <= 3) and prd_conf["QTY"][row] > 3)
         else 3 if prd_conf["BADDATA_FLAG"][row] == 3
         else 0)
        for row in range(len(prd_conf))
    ]
    details, df_metrics, df_metrics_forwc, df_metrics_forpers = calculate_oeemetrics(
        df=prd_conf[prd_conf["BADDATA_FLAG"] == 0], nontimes=non_times)
    for item in details:
        try:
            details[item]["OEE"] = (100 * details[item]["OEE"])
            details[item]["OEE"] = details[item]["OEE"].astype(int)
            details[item]['OEE'] = details[item]['OEE'].apply(lambda x: str(x) + ' %')
        except (TypeError, IntCastingNaNError) as e:
            print(f"Error: {e}")
            continue
    gann_data = get_gann_data(df=prd_conf)

    df_baddatas = prd_conf.loc[prd_conf["BADDATA_FLAG"] != 0, ["COSTCENTER", "MATERIAL", "QTY", "CONFIRMATION"
        , "CONFIRMPOS", "WORKSTART", "WORKEND", "BADDATA_FLAG"]]
    df_baddatas["CONFIRMATION"] = df_baddatas["CONFIRMATION"].astype('str')
    df_baddatas.drop_duplicates(inplace=True)
    df_baddata_rates = prd_conf[prd_conf["CONFTYPE"] == "Uretim"].groupby(["COSTCENTER", "BADDATA_FLAG"]).agg(
        {"BADDATA_FLAG": "count"})
    df_baddata_rates = df_baddata_rates.rename(columns={'BADDATA_FLAG': 'SUMS'})
    df_baddata_rates.reset_index(inplace=True)
    # cache_key = json.dumps(params)

    details, df_metrics, df_metrics_forwc, df_metrics_forpers = calculate_oeemetrics(
        df=prd_conf[prd_conf["BADDATA_FLAG"] == 0], nontimes=non_times)
    result = [{item: details[item].to_json(date_format='iso', orient='split')
               for item in details.keys()},
              df_metrics.to_json(date_format='iso', orient='split'),
              gann_data.to_json(date_format='iso', orient='split'),
              df_metrics_forwc.to_json(date_format='iso', orient='split'),
              df_baddatas.to_json(date_format='iso', orient='split'),
              df_baddata_rates.to_json(date_format='iso', orient='split'),
              onemonth_prdqty.to_json(date_format='iso', orient='split'),
              df_metrics_forpers.to_json(date_format='iso', orient='split')
              ]

    return result


@cache.memoize(timeout=TIMEOUT)
def oee(params=None):
    oee, metrics, gann_data, df_metrics_forwc, \
        df_baddatas, df_baddata_rates, onemonth_prdqty, df_metrics_forpers = prdconf(params)
    oee = {k: pd.read_json(v, orient='split') for k, v in oee.items()}
    metrics = pd.read_json(metrics, orient='split')
    gann_data = pd.read_json(gann_data, orient='split')
    df_metrics_forwc = pd.read_json(df_metrics_forwc, orient='split')
    df_baddatas = pd.read_json(df_baddatas, orient='split')
    df_baddata_rates = pd.read_json(df_baddata_rates, orient='split')
    onemonth_prdqty = pd.read_json(onemonth_prdqty, orient='split')
    df_metrics_forpers = pd.read_json(df_metrics_forpers, orient='split')
    result = (
    oee, metrics, gann_data, df_metrics_forwc, df_baddatas, df_baddata_rates, onemonth_prdqty, df_metrics_forpers)
    cache.set('oee_cached_data', result)
    return result


# @cache.memoize(timeout=TIMEOUT)
def workcenters(option_slctd, report_type, params, oeelist1w, oeelist3w, oeelist7w,come_from_tvlayout=0):
    oeelist1w = pd.read_json(oeelist1w, orient='split')
    oeelist3w = pd.read_json(oeelist3w, orient='split')
    oeelist7w = pd.read_json(oeelist7w, orient='split')

    list_of_wcs = []
    if report_type == 'wc':
        max_output = len(oeelist1w)
        for item in oeelist1w.loc[oeelist1w["COSTCENTER"] == option_slctd]["WORKCENTER"].unique():
            list_of_wcs.append(item)
    else:
        max_output = len(oeelist7w)
        for item in oeelist7w.loc[oeelist7w["COSTCENTER"] == option_slctd]["DISPLAY"].unique():
            list_of_wcs.append(item)

    df = oeelist1w[oeelist1w["COSTCENTER"] == option_slctd]
    df_wclist = oeelist3w[oeelist3w["COSTCENTER"] == option_slctd]
    df_forpers = oeelist7w[oeelist7w["COSTCENTER"] == option_slctd]

    list_of_figs = []
    list_of_columns = []
    list_of_data = []
    list_of_styles = []

    def weighted_average(x):
        # Use the updated weights
        return np.average(x, weights=weights.loc[x.index])

    wm = lambda x: weighted_average(x)

    # If time interval 'day' then there will be shift and material columns in details table otherwise there wont.
    # i used list indices to manupulate column list of details table
    if params["interval"] == 'day':
        col_ind = 0
        groupby_column = "SHIFT"
    else:
        col_ind = 2
        groupby_column = "DISPLAY"

    wc_col = ["SHIFT", "MATERIAL", "QTY", "DISPLAY", "AVAILABILITY", "PERFORMANCE", "QUALITY", "OEE", "TOTALTIME"]
    pers_col = ["SHIFT", "MATERIAL", "QTY", "DISPLAY", "AVAILABILITY", "PERFORMANCE", "QUALITY", "OEE", "TOTALTIME"]

    for item in range(MAX_OUTPUT):

        if item < len(list_of_wcs):
            if report_type == 'wc':
                fig = indicator_with_color(df_metrics=df, order=list_of_wcs[item], colorof='black', height=420,
                                           width=450)
                df_details = df_wclist.loc[(df_wclist["WORKCENTER"] == list_of_wcs[item]),
                wc_col[col_ind:]]
            else:
                fig = indicator_with_color(df_metrics=df_forpers, order=list_of_wcs[item], colorof='black',
                                           title='DISPLAY', height=420, width=450)
                df_details = df_wclist.loc[(df_wclist["DISPLAY"] == list_of_wcs[item]), pers_col[col_ind:]]

            aggregations = {
                'MATERIAL': max,  # Sum of 'performance' column
                'QTY': "sum",  # Mean of 'availability' column
                'AVAILABILITY': wm,
                'PERFORMANCE': wm,
                'QUALITY': wm,
                'OEE': wm,
                'SHIFT': 'count'
            }

            if col_ind == 2:
                del aggregations['MATERIAL']
                del aggregations['SHIFT']

            if len(df_details) == 0:
                continue
            columns = [{"name": i, "id": i} for i in df_details.columns]
            data = df_details.to_dict("records")
            style = {"display": "flex", "justify-content": "space-between",
                     "align-items": "center", "width": 700,
                     "height": 250}

            # df_details.sort_values(by=["SHIFT"], inplace=True)
            weights = df_details.loc[df_details.index, "TOTALTIME"]
            weights[weights <= 0] = 1
            # Burada vardiya özet satırını oluşturup ekliyoruz.
            # Hatırlayalım col_ind 0 olması günlük rapor olduğuna işaret eder
            summary_row = df_details.groupby(groupby_column).agg(aggregations)
            # summary_row = summary_row[summary_row[groupby_column] > 1]
            summary_row[groupby_column] = summary_row.index
            summary_row[groupby_column] = summary_row[groupby_column].astype(str)

            if report_type == 'wc':
                if col_ind == 0:
                    summary_row[groupby_column] = summary_row[groupby_column] + ' (Özet)'
                    df_details = df_details.append(summary_row)
                else:
                    df_details.drop(columns="TOTALTIME", inplace=True)
                    summary_row.reset_index(inplace=True, drop=True)
                    df_details = summary_row
            else:
                if col_ind == 0:
                    df_details.drop(columns=["DISPLAY"], inplace=True)
                    summary_row["SHIFT"] = summary_row["SHIFT"] + ' (Özet)'
                    summary_row["MATERIAL"] = ''
                    df_details = df_details.append(summary_row)
                else:
                    df_details.drop(columns=["TOTALTIME", "DISPLAY"], inplace=True)
                    summary_row.drop(columns=["DISPLAY"], inplace=True)
                    summary_row.reset_index(inplace=True, drop=True)
                    df_details = summary_row

            # Verileri yüzde formuna getiriyoruz
            df_details["AVAILABILITY"] = (df_details["AVAILABILITY"] * 100).round()
            df_details["AVAILABILITY"] = df_details["AVAILABILITY"].astype(str) + '%'
            df_details["QUALITY"] = (df_details["QUALITY"] * 100).round()
            df_details["QUALITY"] = df_details["QUALITY"].astype(str) + '%'
            df_details["OEE"] = (df_details["OEE"] * 100).round()
            df_details["OEE"] = df_details["OEE"].astype(str) + '%'
            df_details["PERFORMANCE"] = (df_details["PERFORMANCE"] * 100).round()
            df_details["PERFORMANCE"] = df_details["PERFORMANCE"].astype(str) + '%'
            if come_from_tvlayout == 1:
                df_details = df_details[["MATERIAL","QTY","AVAILABILITY","QUALITY"]]
            else:
                if col_ind == 0:
                    df_details["SHIFT"] = df_details["SHIFT"].astype(str)
                    df_details.sort_values(by='SHIFT', inplace=True)
            style = {}
            columns = [{"name": i, "id": i} for i in df_details.columns]
            data = df_details.to_dict("records")
        else:
            fig = {}
            columns = []
            data = []
            style = {"display": "none"}

        list_of_figs.append(fig)
        list_of_data.append(data)
        list_of_columns.append(columns)
        list_of_styles.append(style)
    return list_of_figs,list_of_data,list_of_columns ,list_of_styles

# @cache.memoize(timeout=TIMEOUT)
def return_piechart(option_slctd,oeelist0):
    oeelist0 = {k: pd.read_json(v, orient='split') for k, v in oeelist0.items()}
    df = oeelist0[option_slctd]
    print(df)
    df["OEE"] = df["OEE"] * 100
    try:
        df["OEE"] = df["OEE"].astype(int)
    except pd.errors.IntCastingNaNError:
        df["OEE"] = 0
    if int(df["OEE"][0]*100) > 38:
        print("if doğru ( app.py satır 283 ) ")
        fig = px.sunburst(df, path=["OEE", "MACHINE", "OPR"], values="RATES", width=425, height=425,
                          color="RATES", color_continuous_scale=px.colors.diverging.RdYlGn,
                          color_continuous_midpoint=50)
    else:
        print("if yanlış ( app.py satır 283 ) ")
        fig = px.sunburst(df, path=["OEE", "MACHINE", "OPR"], values="RATES", width=425, height=425,
                          color="RATES", color_continuous_scale=px.colors.diverging.RdYlGn_r,
                          color_continuous_midpoint=50)

    fig.update_traces(hovertemplate='<b>Actual Rate is %{value} </b>',
                      textfont=dict(size=[15,15,15,15,15,60,60]))
    fig.update_layout(showlegend=False,
                      paper_bgcolor='rgba(0, 0, 0, 0)', plot_bgcolor='rgba(0, 0, 0, 0)',
                      # width= 10, height= 10,
                      title_x=0.5, title_xanchor="center",
                      title_font_size=40,
                      annotations=[
                          dict(
                              text="OEE - Kullanılabilirlik - Performans",
                              showarrow=False,
                              xref='paper', yref='paper',
                              x=0.5, y=1,
                              xanchor='center', yanchor='bottom',
                              font=dict(size=18, color=summary_color),
                              bgcolor='darkolivegreen',  # The desired background color for the title
                          )]
                      )
    return fig

app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="make_draggable"),
    Output("drag_container", "data-drag"),
    [Input("drag_container", "id"), Input("drag_container2", "id")],
)
if __name__ == "__main__":
    app.run(debug=True)
