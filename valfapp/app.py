### Import Packages ###
import os
import logging
import numpy as np
import pandas as pd
from pandas.errors import IntCastingNaNError
from dash import ClientsideFunction, Output, Input, html, dcc
from flask_caching import Cache
import dash
import dash_bootstrap_components as dbc
from valfapp.functions.functions_prd import calculate_oeemetrics, apply_nat_replacer, get_gann_data, indicator_with_color
from run.agent import ag
from config import project_directory, kb
import plotly.express as px  # (version 4.7.0 or higher)
from datetime import date, timedelta, datetime


MAX_OUTPUT = 25
summary_color = 'black'

logger = logging.getLogger(__name__)

### Dash instance ###

app = dash.Dash(
    __name__,
    meta_tags=[{'name': 'viewport',
                'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'}],
    external_scripts=[r"assets\ag_grid_custom_renderers.js",
                      "https://cdnjs.cloudflare.com/ajax/libs/dragula/3.7.2/dragula.min.js",
                      "/website/css/uicons-outline-rounded.css",
                      "https://netdna.bootstrapcdn.com/font-awesome/4.0.3/css/font-awesome.css",
                      "https://cdn.jsdelivr.net/npm/sparkline@1.0.0/sparkline.min.js"],
    external_stylesheets=[dbc.themes.PULSE],
    suppress_callback_exceptions=True,
)

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

TIMEOUT = 1200000

@app.server.route('/clear-cache')
def clear_cache():
    cache.clear()
    return "Cache has been cleared!"
# data=[date.today() - timedelta(days=kb)).isoformat(), (date.today() - timedelta(days=1)).isoformat(),"day"]
# params = ['2023-12-25','2023-12-25','day']

@cache.memoize(timeout=TIMEOUT)
def prdconf(params=None):
    paramswith = params[0:2]
    print("*****")
    print(params)
    print("*****")
    prd_conf = ag.run_query(query=r"EXEC VLFPRODALLINONEWPARAMS @WORKSTART=?, @WORKEND=?", params=paramswith)

    if os.path.isfile(r"F:\pycarhm projects\Charting\outputs(xlsx)\bul.xlsx"):
        os.remove(project_directory + r"\Charting\outputs(xlsx)\bul.xlsx")

    onemonth_prdqty = ag.run_query(query=r"EXEC VLFPROCPRDFORSPARKLINES @WORKSTART=?, @WORKEND=?, @DATEPART=?",
                                   params=params)
    if len(prd_conf) == 0:
        return [None, None, None, None, None, None, None, None]
    prd_conf["BREAKDOWNSTART"] = prd_conf.apply(lambda row: apply_nat_replacer(row["BREAKDOWNSTART"]), axis=1)
    prd_conf["IDEALCYCLETIME"] = prd_conf["IDEALCYCLETIME"].astype("float")


    # 2 de biten mesai için gün ayarlaması.
    def adjust_workday(row):
        if row.hour < 2:  # Checks if the hour is between 00:00 and 01:59
            return (row - timedelta(days=1)).date()
        else:
            return row.date()

    # Apply the function to the 'WORKSTART' column to create/adjust 'WORKDAY' column
    prd_conf['WORKDAY'] = prd_conf['WORKSTART'].apply(adjust_workday)


    #Planlanan Süreden Düşülecek  Duruş Süreleri
    non_times = ag.run_query(query=r"EXEC VLFPRODEMPTYFAILURE @WORKSTART=?, @WORKEND=?", params=paramswith)
    non_times["WORKDAY"] = non_times["BREAKDOWNSTART"].dt.date


    summary_helper = prd_conf[prd_conf["CONFTYPE"] == 'Uretim'].groupby(["WORKCENTER", "SHIFT", "MATERIAL"]) \
        .agg({"IDEALCYCLETIME": "sum", "RUNTIME": "sum"})


    summary_helper.reset_index(inplace=True)
    summary_helper["RATER"] = summary_helper["IDEALCYCLETIME"] / summary_helper["RUNTIME"]
    summary_helper["BADDATA_FLAG"] = 0
        # [3 if summary_helper["RATER"][row] > 1.3
        #                               else 0 for row in range(len(summary_helper))]
    summary_helper = summary_helper[["WORKCENTER", "SHIFT", "MATERIAL", "BADDATA_FLAG"]]
    prd_conf = pd.merge(prd_conf, summary_helper, on=['MATERIAL', 'SHIFT', 'WORKCENTER'], how='left')


    gann_data = get_gann_data(df=pd.concat([prd_conf,non_times]))
    if params[2] in ['week','month']:
        gann_data['WORKEND'] = gann_data['WORKEND'].apply(
            lambda x: pd.to_datetime(params[1]) if x > pd.to_datetime(params[1]) else x)
    prd_conf['RATER'] = prd_conf["RUNTIME"] / prd_conf["IDEALCYCLETIME"]
    prd_conf["BADDATA_FLAG"] = np.where(prd_conf["RATER"] < 0.82, 1, 0)
    df_baddatas = prd_conf.loc[prd_conf["BADDATA_FLAG"] != 0, ["COSTCENTER","WORKCENTER", "MATERIAL", "QTY", "CONFIRMATION"
        , "CONFIRMPOS", "WORKSTART", "WORKEND","RUNTIME", "IDEALCYCLETIME", "BADDATA_FLAG"]]
    df_baddatas["CONFIRMATION"] = df_baddatas["CONFIRMATION"].astype('str')
    df_baddatas.drop_duplicates(inplace=True)
    df_baddata_rates = prd_conf[prd_conf["CONFTYPE"] == "Uretim"].groupby(["COSTCENTER", "BADDATA_FLAG"]).agg(
        {"BADDATA_FLAG": "count"})
    df_baddata_rates = df_baddata_rates.rename(columns={'BADDATA_FLAG': 'SUMS'})
    df_baddata_rates.reset_index(inplace=True)
    # cache_key = json.dumps(params)

    details, df_metrics, df_metrics_forwc, df_metrics_forpers = calculate_oeemetrics(
        df=prd_conf, nontimes=non_times)
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

    list_of_items = []

    if option_slctd == 'CNC1' or option_slctd == 'CNC2':

        if  option_slctd == 'CNC1':
            list_of_items = ["CNC-07", "CNC-19", "CNC-26", "CNC-28", "CNC-08", "CNC-29"]
            list_of_wcs = ["CNC-07", "CNC-19", "CNC-26", "CNC-28", "CNC-08", "CNC-29"]


        else:
            list_of_items = ["CNC-01", "CNC-03", "CNC-04", "CNC-11", "CNC-12", "CNC-13", "CNC-14", "CNC-15", "CNC-16",
                       "CNC-17", "CNC-18",
                       "CNC-20", "CNC-21", "CNC-22", "CNC-23"]
            list_of_wcs = ["CNC-01", "CNC-03", "CNC-04", "CNC-11", "CNC-12", "CNC-13", "CNC-14", "CNC-15", "CNC-16",
                       "CNC-17", "CNC-18",
                       "CNC-20", "CNC-21", "CNC-22", "CNC-23"]


        if report_type == 'wc':
            max_output = len(oeelist1w)
            for item in oeelist1w.loc[oeelist1w["WORKCENTER"].isin(list_of_items)]["WORKCENTER"].unique():
                list_of_items.append(item)
        else:
            max_output = len(oeelist7w)
            list_of_items =  oeelist3w.loc[oeelist3w["WORKCENTER"].isin(list_of_items)]["DISPLAY"].unique()

        df = oeelist1w[oeelist1w["WORKCENTER"].isin(list_of_wcs)]
        df_wclist = oeelist3w[oeelist3w["WORKCENTER"].isin(list_of_wcs)]
        df_forpers = oeelist7w[oeelist7w["DISPLAY"].isin(list_of_items)]

    else:
        if report_type == 'wc':
            max_output = len(oeelist1w)
            for item in oeelist1w.loc[oeelist1w["COSTCENTER"] == option_slctd]["WORKCENTER"].unique():
                list_of_items.append(item)
        else:
            max_output = len(oeelist7w)
            for item in oeelist7w.loc[oeelist7w["COSTCENTER"] == option_slctd]["DISPLAY"].unique():
                list_of_items.append(item)

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

        if item < len(list_of_items):
            if report_type == 'wc':
                fig = indicator_with_color(df_metrics=df, order=list_of_items[item], colorof='black', height=420,
                                           width=450)
                df_details = df_wclist.loc[(df_wclist["WORKCENTER"] == list_of_items[item]),
                wc_col[col_ind:]]
            else:
                fig = indicator_with_color(df_metrics=df_forpers, order=list_of_items[item], colorof='black',
                                           title='DISPLAY', height=420, width=450)
                df_details = df_wclist.loc[(df_wclist["DISPLAY"] == list_of_items[item]), pers_col[col_ind:]]

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
                df_details.columns = ["Malzeme","Adet","Kullanb.","Klite"]

            else:
                if col_ind == 0:
                    df_details["SHIFT"] = df_details["SHIFT"].astype(str)
                    df_details.sort_values(by='SHIFT', inplace=True)

                    if report_type == 'wc':
                        df_details.columns = ["Vard.", "Mal.", "Adet", "Opr.", "Kul.", "Perf.", "Klite", "OEE", 'Süre']
                    else:
                        df_details.columns = ["Vard.", "Adet", "Opr.", "Kul.", "Perf.", "Klite", "OEE", 'Süre']




            style = {}
            columns = [{"name": i, "id": i} for i in df_details.columns]
            data = df_details.to_dict("records")

        else:
            continue

        list_of_figs.append(fig)
        list_of_data.append(data)
        list_of_columns.append(columns)
        list_of_styles.append(style)

    return list_of_figs,list_of_data,list_of_columns ,list_of_styles

# @cache.memoize(timeout=TIMEOUT)
def return_piechart(option_slctd,oeelist0,forreports=0):

    oeelist0 = {k: pd.read_json(v, orient='split') for k, v in oeelist0.items()}
    df = oeelist0[option_slctd]
    df["OEE"] = df["OEE"] * 100
    try:
        df["OEE"] = df["OEE"].astype(int)
    except pd.errors.IntCastingNaNError:
        df["OEE"] = 0

    def sunburst_statusbar():
        # Assuming 'df' and 'fig' are already defined and 'fig' is your sunburst chart

        # Generate a list of color values from the color scale used in the sunburst chart

        # rates_min = df["RATES"].min()
        # rates_max = df["RATES"].max()

        rates_min = 0
        rates_max = 100

        rates_range = np.linspace(rates_min, rates_max, num=10)  # Create 10 intervals for the example

        if int(df["OEE"][0] * 100) > 38:
            color_scale = px.colors.diverging.RdYlGn  # Replace with the color scale you used in your sunburst chart
        else:
            color_scale = px.colors.diverging.RRdYlGn_r

        # Map each rate to a color
        rate_to_color = {rate: color_scale[int((rate - rates_min) / (rates_max - rates_min) * (len(color_scale) - 1))]
                         for rate in rates_range}

        # Create custom color scale bar
        color_scale_divs = [
            html.Div(
                style={
                    'backgroundColor': rate_to_color[rate],
                    'height': '20px',  # Fixed height for each color segment
                    'color': 'black' if rate < (rates_max + rates_min) / 2 else 'white',
                    # Adjust text color for contrast
                    'textAlign': 'center',  # Center the text
                    'fontWeight': 'bold'  # Optional: make the text bold
                },
                children=str(int(rate))  # Display the rate value
            )
            for rate in rates_range
        ]

        color_scale_legend = html.Div(color_scale_divs, style={
            'display': 'flex',
            'flexDirection': 'column',  # Stack divs vertically
            'margin-left':30,
            'margin-top':85
        })

        return color_scale_legend

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

    fig.update_traces(hoverinfo='none')  # Disables hover information

    fig.update_layout(showlegend=False,coloraxis_showscale=False if forreports == 1 else True,
                      paper_bgcolor='rgba(0, 0, 0, 0)', plot_bgcolor='rgba(0, 0, 0, 0)',
                      # width= 10, height= 10,
                      )
    return fig if forreports ==0 \
        else dbc.Row([dbc.Col(dcc.Graph(figure=fig), width=8), dbc.Col(sunburst_statusbar(), width=4)])

app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="make_draggable"),
    Output("drag_container", "data-drag"),
    [Input("drag_container", "id"), Input("drag_container2", "id")],
)




if __name__ == "__main__":
    app.run(debug=True)

