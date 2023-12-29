# Import required libraries and modules
import json
from datetime import date, timedelta
import pandas as pd
from dash import dcc, html, Input, Output, State, callback_context, no_update, exceptions
import dash_bootstrap_components as dbc
from config import kb
import plotly.express as px
from valfapp.app import cache, app, prdconf, workcenters
import dash_table
from dash.exceptions import PreventUpdate
from valfapp.pages.date_class import update_date, update_date_output

# Define constants and initial data
MAX_OUTPUT = 25
costcenters = ["CNC", "CNCTORNA", "TASLAMA", "MONTAJ", "PRESHANE1", "PRESHANE2"]
global work_dates_bk
work_dates_bk = {"workstart": (date.today() - timedelta(days=1)).isoformat(),
                 "workend": date.today().isoformat(),
                 "interval": "day"}


# start_day = (date.today() - timedelta(days=1)).isoformat() if (date.today() - timedelta(days=1)).weekday() != 6 \
#     else (date.today() - timedelta(days=2)).isoformat()
# end_day = (date.today() - timedelta(days=0)).isoformat() if (date.today() - timedelta(days=1)).weekday() != 6 \
#     else (date.today() - timedelta(days=1)).isoformat()
# oeelist = oee((start_day, end_day, "day"))


def generate_output_list(max_output):
    """
    Generates a list of Output elements for the Dash app.

    Args:
        max_output (int): The maximum number of output elements to generate.

    Returns:
        list: A list of Output elements.
    """
    return [Output(f"wc{i + 1}_graph", "figure") for i in range(max_output)] + \
        [Output(f"wc{i + 1}_table", "data") for i in range(max_output)] + \
        [Output(f"wc{i + 1}_table", "columns") for i in range(max_output)] + \
        [Output(f"wc{i + 1}", "style") for i in range(max_output)]


def return_tops_with_visibility(graph_id, visible=True):
    """
    Creates a Dash HTML Div containing a Graph and DataTable with optional visibility.

    Args:
        graph_id (str): The base identifier for the Graph and DataTable elements.
        visible (bool): Whether the Div should be visible initially. Default is True.

    Returns:
        html.Div: A Dash HTML Div containing the Graph and DataTable.
    """
    return html.Div(
        children=[
            dcc.Graph(id=f"{graph_id}_graph", figure={}, style={'margin-left': 120}),
            dash_table.DataTable(id=f"{graph_id}_table", data=[], columns=[],
                                 style_cell={
                                     "minWidth": "80px",
                                     "width": "80px",
                                     "maxWidth": "100px",
                                     "textAlign": "center",
                                 },
                                 style_table={
                                     "height": '150px',
                                     "width": '700px',  # Fixed pixel width
                                     "overflowY": 'auto',
                                 }
                                 )
        ],
        id=graph_id,
        style={"display": "flex", "flex-direction": "column", "justify-content": "center", "width": 1000},
        hidden=not visible
    )


# Create the layout for the app
layout = dbc.Container([
    dbc.Row(
        dcc.Link(
            children='Main Page',
            href='/',
            style={"color": "black", "font-weight": "bold"}
        )),
    dbc.Row(
        [dcc.Store(id="list_of_wcs"),
         dcc.Store(id="max_output"),
         dcc.Store(id='oeelistw1',
                   data=prdconf(((date.today() - timedelta(days=kb)).isoformat(), date.today().isoformat(), "day"))[
                       1]),
         dcc.Store(id='oeelistw2',
                   data=prdconf(((date.today() - timedelta(days=kb)).isoformat(), date.today().isoformat(), "day"))[
                       2]),
         dcc.Store(id='oeelistw3',
                   data=prdconf(((date.today() - timedelta(days=kb)).isoformat(), date.today().isoformat(), "day"))[
                       3]),
         dcc.Store(id='oeelistw4',
                   data=prdconf(((date.today() - timedelta(days=kb)).isoformat(), date.today().isoformat(), "day"))[
                       4]),
         dcc.Store(id='oeelistw5',
                   data=prdconf(((date.today() - timedelta(days=kb)).isoformat(), date.today().isoformat(), "day"))[
                       5]),
         dcc.Store(id='oeelistw7',
                   data=prdconf(((date.today() - timedelta(days=kb)).isoformat(), date.today().isoformat(), "day"))[
                       7]),
         dcc.Store(id='store-costcenter1', storage_type='memory'),
         dcc.Store(id='store-report-type', data='wc', storage_type='memory'),
         dbc.Button("Day", id="btn-day1", n_clicks=0, color="primary", className='day-button'),
         dcc.Dropdown(id="costcenter1",
                      className='dropdown-style',
                      options=[{"label": cc, "value": cc} for cc in costcenters],
                      multi=False,
                      value="CNC",
                      ),
         dcc.DatePickerSingle(id='date-picker1', date=date.today(), className="dash-date-picker",
                              persistence=True, persistence_type='local', style={"color": "white"}),

         dbc.Button("Week", id="btn-week1", n_clicks=0, color="primary", className='week-button'),
         dbc.Button("Month", id="btn-month1", n_clicks=0, color="primary", className='month-button'),
         dbc.Button("Year", id="btn-year1", n_clicks=0, color="primary", className='year-button'),

         html.Button(html.Img(src='/assets/wc.jpg', style={'width': '100%', 'height': '100%'}),
                     id='wc-button', className='wc-button'),
         html.Button(html.Img(src='/assets/pers.png', style={'width': '100%', 'height': '100%'}),
                     id='pers-button', className='pers-button'),
         dbc.Button("Hataları Gizle/Göster", id="toggle_button", n_clicks=2, className="toggle-button"),

         dcc.Store(id="work-dates1", storage_type="memory",
                   data={"workstart": (date.today() - timedelta(days=1)).isoformat(),
                         "workend": date.today().isoformat(),
                         "interval": "day"}),
         html.Button('Reset Cache', id='clear-cache-button', n_clicks=0, className="bbtn btn-primary btn-sm ml-auto",
                     style={"position": "absolute", "right": 200, "top": "3", "width": "150px", "height": "35px"}),
         html.Div(id="toggle_div", children=[
             html.H1("Hatalı Veri Girişleri", style={"textAlign": "center"}),
             html.Hr(),
             html.Hr(),
             html.Div([
                 dbc.Col(
                     dcc.Graph(id="pie_chart", figure={}),
                     width={"size": 4}
                 ),
                 dbc.Col(
                     dash_table.DataTable(
                         id="invalid_data_table",
                         columns=[],
                         # [{"name": i, "id": i} for i in oeelist[4].columns],
                         style_cell={
                             "minWidth": "100px",
                             "width": "100px",
                             "maxWidth": "100px",
                             "textAlign": "center",
                         },
                     ),
                     width={"size": 8}
                 ),
             ]),
         ]),
         html.Div(id='refresh', style={'display': 'none'}),
         html.Div(id='refresh2', style={'display': 'none'}),
         html.Div(id='output-div'),
         # Include this line in your app layout
         dcc.Location(id='location', refresh=True),
         dcc.Location(id='location2', refresh=True),
         html.Button("Oee Data", id="download-button", n_clicks=0, className="bbtn btn-primary btn-sm ml-auto",
                     style={"position": "absolute", "right": "0", "top": "-1", "width": "100px", "height": "35px"}),
         html.Button("Details Data", id="download-button2", n_clicks=0, className="bbtn btn-primary btn-sm ml-auto",
                     style={"position": "absolute", "right": 100, "top": "-1", "width": "100px", "height": "35px"}),
         dcc.Download(id="download-data"),
         dcc.Download(id="download-data2")], ),

    dbc.Row(id='flam', children=[dbc.Col(return_tops_with_visibility(f"wc{i + 1}"), width=5,
                                         style={"height": 600, "margin-left": 100 if i % 2 == 0 else 180}) for i in
                                 range(MAX_OUTPUT)],
            )
], fluid=True)

list_of_callbacks = generate_output_list(MAX_OUTPUT)


@app.callback(Output('store-costcenter1', 'data'),
              Input('costcenter1', 'value'))
def update_store(value):
    return value


@app.callback(Output('costcenter1', 'value'),
              [Input('store-costcenter1', 'modified_timestamp')],
              [State('store-costcenter1', 'data')])
def update_dropdown(ts, stored_data):
    if ts is None:
        # if no data was stored yet, it initializes the dropdown to its default value
        raise exceptions.PreventUpdate
    return stored_data


@app.callback(
    Output('invalid_data_table', 'columns'),
    Output("invalid_data_table", "data"),
    Input('oeelistw4', 'data'),
    Input("costcenter1", "value")
)
def update_table_columns(oeelistw4, costcenter):
    oeelist4w = pd.read_json(oeelistw4, orient='split')
    df_filtered = oeelist4w[oeelist4w["COSTCENTER"] == costcenter]
    df = pd.read_json(oeelistw4, orient='split')
    # df = pd.DataFrame(data)  # Convert the stored data back to DataFrame
    columns = [{"name": i, "id": i} for i in df.columns]
    return columns, df_filtered.to_dict("records")


@app.callback(
    [Output('work-dates1', 'data'),
     Output('refresh2', 'children'),
     Output(component_id='oeelistw1', component_property='data'),
     Output(component_id='oeelistw2', component_property='data'),
     Output(component_id='oeelistw3', component_property='data'),
     Output(component_id='oeelistw4', component_property='data'),
     Output(component_id='oeelistw5', component_property='data'),
     Output(component_id='oeelistw7', component_property='data')],
    [Input('btn-day1', 'n_clicks'),
     Input('date-picker1', 'date'),
     Input('btn-week1', 'n_clicks'),
     Input('btn-month1', 'n_clicks'),
     Input('btn-year1', 'n_clicks')]
)
def update_work_dates(n1, date_picker, n2, n3, n4):
    stored_date = date_picker
    if n1 or date_picker or n2 or n3 or n4:
        data = update_date('1', date_picker, callback_context)
        print(f"params= {data}")
        if data != {}:
            oeelist = prdconf(params=(data["workstart"], data["workend"], data["interval"]))
            a = update_date_output(n1, date_picker, n2, n3, n4, data)
            return (a[0], 0) + (oeelist[1], oeelist[2], oeelist[3], oeelist[4], oeelist[5], oeelist[7])
        else:
            return (work_dates_bk, 0, no_update, no_update, no_update, no_update, no_update, no_update)
    else:
        return (work_dates_bk, 0, no_update, no_update, no_update, no_update, no_update, no_update)


@app.callback(
    Output('store-report-type', 'data'),
    [Input('pers-button', 'n_clicks'),
     Input('wc-button', 'n_clicks')]
)
def update_report_type(n1, n2):
    ctx = callback_context
    # Default case
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'pers-button':
        return 'pers'
    elif button_id == 'wc-button':
        return 'wc'
    else:
        return no_update


@app.callback(
    Output('location2', 'href'),
    Input('refresh2', 'children')
)
def page_refresh2(n2):
    if n2:
        return "/wcreport"
    return no_update


# Inside a callback
# Create a callback for the button
@app.callback(
    Output('refresh', 'children'),
    [Input('clear-cache-button', 'n_clicks'),
     State("work-dates1", 'data')]
)
def clear_cache(n_clicks, key):
    if n_clicks > 0:
        a = cache.get(json.dumps({'workstart': '2023-09-06', 'workend': '2023-09-07', 'interval': 'day'}))
        cache_key = json.dumps(key)
        x = cache.get(cache_key)
        cache.delete_memoized(prdconf, (key["workstart"], key["workend"], key["interval"]))

        # Perform any other necessary operations after clearing the cache
        return no_update  # Change the 'refresh' div when the button is clicked
    else:
        return no_update  # Don't change the 'refresh' div if the button hasn't been clicked


# Add this callback
@app.callback(
    Output('location', 'href'),
    [Input('refresh', 'children')]
)
def page_refresh(n):
    if n:
        return "/wcreport"
    return no_update


# Callback for hiding/showing the first div
@app.callback(
    Output("toggle_div", "style"),
    Output('flam', 'style'),
    Input("toggle_button", "n_clicks")
)
def toggle_first_div(n_clicks):
    if n_clicks and n_clicks % 2 == 1:
        return {"display": "none"}, {"marginTop": "0px"}
    else:
        return {}, {"marginTop": "100px"}


@app.callback(
    Output("pie_chart", "figure"),
    [Input("costcenter1", "value"),
     Input(component_id='oeelistw5', component_property='data')]
)
def update_pie_chart(costcenter, oeelist5w):
    df = pd.read_json(oeelist5w, orient='split')
    df_filtered = df.loc[df["COSTCENTER"] == costcenter]
    labels = ["0 - Geçerli Data", "1 - Tanımlı Süre Yok", "2 - Hatalı Operatör Girişi", "3 - Tanımlı Süre Hatalı"]
    values = [0 if len(df_filtered[df_filtered["BADDATA_FLAG"] == 0]) == 0 else
              int(df_filtered[df_filtered["BADDATA_FLAG"] == 0]["SUMS"]),
              0 if len(df_filtered[df_filtered["BADDATA_FLAG"] == 1]) == 0 else
              int(df_filtered[df_filtered["BADDATA_FLAG"] == 1]["SUMS"]),
              0 if len(df_filtered[df_filtered["BADDATA_FLAG"] == 2]) == 0 else
              int(df_filtered[df_filtered["BADDATA_FLAG"] == 2]["SUMS"]),
              0 if len(df_filtered[df_filtered["BADDATA_FLAG"] == 3]) == 0 else \
                  int(df_filtered[df_filtered["BADDATA_FLAG"] == 3]["SUMS"])
              ]

    fig = px.pie(names=labels, values=values, title="Veri Geçerlilik Dağalımı")
    return fig


@app.callback(
    [*list_of_callbacks],
    [Input("costcenter1", "value"),
     Input("store-report-type", "data"),
     Input("work-dates1", "data"),
     Input(component_id='oeelistw1', component_property='data'),
     Input(component_id='oeelistw3', component_property='data'),
     Input(component_id='oeelistw7', component_property='data')]

)
def update_ind_fig(option_slctd, report_type, params, oeelist1w, oeelist3w, oeelist7w):
    """
    Callback to update individual figures for each work center in the selected cost center.

    Args:
        list_of_wcs (list): The list of work centers to display.
        option_slctd (str): The selected cost center.
        report_day (str): The date for which to display the report. Default is "2022-07-26".

    Returns:
        tuple: A tuple containing lists of figures, data, columns, and styles for each work center.

    Parameters
    ----------
    oeelist7w
    oeelist3w
    params
    report_type
    option_slctd
    oeelist1w
    """

    list_of_figs, list_of_data, list_of_columns, list_of_styles = workcenters(option_slctd, report_type, params,
                                                                              oeelist1w, oeelist3w, oeelist7w)
    return tuple(list_of_figs + list_of_data + list_of_columns + list_of_styles)


@app.callback(
    Output("download-data", "data"),
    Input("download-button", "n_clicks"),
    State("costcenter1", "value"),
    Input(component_id='oeelistw3', component_property='data'),
    prevent_initial_call=True
)
def generate_excel(n_clicks, costcenter, oeelist3w):
    oeelist3w = pd.read_json(oeelist3w, orient='split')
    oeelist3w = oeelist3w[oeelist3w["COSTCENTER"] == costcenter]
    columns = ['WORKCENTER', 'COSTCENTER', 'MATERIAL', 'SHIFT', 'WORKDAY', 'QTY', 'SCRAPQTY', 'REWORKQTY', 'RUNTIME', 'TOTALTIME',
     'TOTFAILURETIME', 'IDEALCYCLETIME', 'SETUPTIME', 'DISPLAY', 'SCRAPTEXT', 'OMTIME', 'QTY_y', 'TOTAL_SHIFT_TIME',
     'NANTIME', 'PLANNEDTIME']
    columns2 = ['WORKCENTER', 'COSTCENTER', 'SHIFT', 'WORKDAY',"AVAILABILITY","PERFORMANCE","QUALITY","OEE"]
    backup_df = oeelist3w.groupby(["WORKCENTER", "COSTCENTER", "SHIFT", "WORKDAY"])["QTY", "SCRAPQTY", "REWORKQTY",
        "RUNTIME", "TOTALTIME", "TOTFAILURETIME", "IDEALCYCLETIME", "SETUPTIME",
        "TOTAL_SHIFT_TIME", "NANTIME", "PLANNEDTIME"].sum()

    backup_df.reset_index(inplace=True)
    backup_df["AVAILABILITY"] = backup_df["RUNTIME"] / backup_df["PLANNEDTIME"]
    backup_df["PERFORMANCE"] = backup_df["IDEALCYCLETIME"] / backup_df["RUNTIME"]
    backup_df["QUALITY"] = (backup_df["QTY"] - backup_df["SCRAPQTY"]) / backup_df["QTY"]
    backup_df["OEE"] = backup_df["AVAILABILITY"]*backup_df["QUALITY"]*backup_df["PERFORMANCE"]
    dff = oeelist3w[columns].merge(backup_df[columns2], on=["WORKCENTER", "COSTCENTER", "SHIFT", "WORKDAY"], how='left')

    return dcc.send_data_frame(dff.to_excel, "mydata.xlsx", index=False)

@app.callback(
    Output("download-data2", "data"),
    Input("download-button2", "n_clicks"),
    State("costcenter1", "value"),
    Input(component_id='oeelistw2', component_property='data'),
    prevent_initial_call=True
)
def generate_excel(n_clicks, costcenter, oeelist2w):
    oeelist2w = pd.read_json(oeelist2w, orient='split')
    # backup_df = oeelist2w.groupby(["WORKCENTER", "COSTCENTER", "SHIFT", "WORKDAY"])["QTY", "SCRAPQTY", "REWORKQTY",
    #     "RUNTIME", "TOTALTIME", "TOTFAILURETIME", "IDEALCYCLETIME", "SETUPTIME", "DISPLAY", "SCRAPTEXT", "OMTIME",
    #     "TOTAL_SHIFT_TIME", "NANTIME", "PLANNEDTIME"].sum()

    # backup_df.reset_index(inplace=True)

    dff2 = oeelist2w[oeelist2w["COSTCENTER"] == costcenter]

    return dcc.send_data_frame(dff2.to_excel, "mydata.xlsx", index=False)
