from datetime import datetime, timedelta
import plotly.graph_objs as go

from dash import html
import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, Input, Output, State, ctx , no_update
from dash_ag_grid import AgGrid

from run.agent import ag
import plotly.express as px
from valfapp.app import app, cache, TIMEOUT


def generate_monthly_columns():
    # Bugünün tarihini al
    today = datetime.today()

    # İçinde bulunduğumuz yıl ve ilk ayı belirle
    start_year = today.year
    start_month = 1

    # Son ay ve yılı belirle (içinde bulunduğumuz yılın Aralık ayı)
    end_year = start_year
    end_month = 12

    # Her format için kolon isimleri listesi oluştur
    format1 = []
    format2 = []
    format3 = []

    # Başlangıç tarihinden itibaren kolon isimlerini oluştur
    current_date = datetime(start_year, start_month, 1)
    end_date = datetime(end_year, end_month, 1)

    i = 0
    while current_date <= end_date:
        year = current_date.year
        month_num = current_date.month

        # Format 1
        if i == 0:
            format1.append(f"0 AS [{year}-{str(month_num).zfill(2)}]")
        else:
            format1.append(f"SUM(B.[{year}-{str(month_num).zfill(2)}]) AS [{year}-{str(month_num).zfill(2)}]")

        # Format 2
        format2.append(f"SUM([{year}-{str(month_num).zfill(2)}]) AS [{year}-{str(month_num).zfill(2)}]")

        # Format 3
        format3.append(f"{year}-{str(month_num).zfill(2)}")

        # Bir sonraki aya geç
        next_month = current_date.month + 1
        if next_month > 12:
            next_month = 1
            current_date = datetime(current_date.year + 1, next_month, 1)
        else:
            current_date = datetime(current_date.year, next_month, 1)

        i += 1

    # Kolonları virgülle ayrılmış string olarak döndür
    columns_str_dict = {
        'format1': ", ".join(format1),
        'format2': ", ".join(format2),
        'format3': ", ".join(format3)
    }
    return columns_str_dict


#@cache.memoize(timeout=TIMEOUT)
def generate_weekly_columns():
    start_date = datetime.now() - timedelta(weeks=1)
    format1 = []
    format2 = []
    format3 = []

    for i in range(14):  # Bu hafta dahil olmak üzere toplamda 14 hafta
        week_start = start_date + timedelta(weeks=i)
        year, week_num, _ = week_start.isocalendar()

        # Format 1
        format1.append(f"SUM([{year}-{str(week_num).zfill(2)}]) AS [{year}-{str(week_num).zfill(2)}]")

        # Format 2
        if i == 0:
            format2.append(f"0 AS [{year}-{str(week_num).zfill(2)}]")
        else:
            format2.append(f"SUM(B.[{year}-{str(week_num).zfill(2)}]) AS [{year}-{str(week_num).zfill(2)}]")

        # Format 3
        format3.append(f"{year}-{str(week_num).zfill(2)}")

    # Kolonları virgülle ayrılmış string olarak döndür
    columns_str_dict = {
        'format1': ", ".join(format1),
        'format2': ", ".join(format2),
        'format3': ", ".join(format3)
    }
    return columns_str_dict

layout = dbc.Container([
    dcc.Store(id='isfirst_trigger', data = 0),
    dcc.Store(id='iscapacity_trigger', data = 0),
    dcc.Store(id='table_name'),
    dcc.Store(id='kolon_sumb'),
    dcc.Store(id='kolon_sum'),
    dcc.Store(id='kolon_list'),
    dbc.Row([
      dbc.Col(html.Div([
        html.Button("Cache Temizle", id="clear-cache-button"),
        html.Div(id="clear-cache-output")
        ])
      ),

      dbc.Col(html.Div([dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0, max_intervals=1),
            dcc.Dropdown(
            id='data-type-dropdown',
            options=["İhtiyaç Miktarı", "Sipariş Miktarı", "Öngörü Miktarı"],
            value="İhtiyaç Miktarı"
            )
        ])
      ),

      dbc.Col(html.Div([

            html.Label('Verimlilik:'),
            dcc.Input(
                id='numeric-input',
                type='number',
                value=80  # Varsayılan değer
            )
      ])),

      dbc.Col(html.Div([dcc.Checklist(
                id='unit-checkbox',
                options=[
                    {'label': 'Dakika', 'value': 'minutes'},
                    {'label': 'Saat', 'value': 'hours'},
                    {'label': 'Vardiya', 'value': 'shifts'}
                ],
                value=['minutes'],  # Varsayılan olarak dakika seçili
                labelStyle={'display': 'inline-block'}
            )

      ])),
    ]),


    dbc.Row([
        dbc.Col(html.Div([
            dcc.Dropdown(
            id='costcenter-dropdown',
            options=[],
            value=None
        )
        ]), width={"size": 3, "offset": 0}),
        dbc.Col(html.Div([
            html.Button('Costcenter Tablosunu İndir', id='btn-download-costcenter'),
            dcc.Download(id='download-costcenter')
        ]), style={'textAlign': 'right'}
        ),

    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='fig')
        ]),
        dbc.Col([
            AgGrid(
                id='costcenter_table',

                #columnDefs=transform_multilevel_columns_to_aggrid_defs(merged_df, buttons=0),
                #defaultColDef=defaultColDef,
                className="ag-theme-alpine-dark",
                columnSize="sizeToFit",
            )
        ])
    ]),

    dbc.Row([
        dbc.Col(html.Div([
            html.Button('Costcenter Kapasite Tablosunu İndir', id='btn-download-costcenter_kapasite'),
            dcc.Download(id='download-costcenter_kapasite')
        ]), width={"size": 3, "offset": 0}),  # Bu, butonu sağa hizalar
    ]),

    dbc.Row([
             AgGrid(
                id='capasity_table_costcenter',

                #columnDefs=transform_multilevel_columns_to_aggrid_defs(merged_df, buttons=0),
                #defaultColDef=defaultColDef,
                className="ag-theme-alpine-dark",
                columnSize="sizeToFit",
            )
    ]),

    dbc.Row([
        dbc.Col(html.Div([dcc.Dropdown(
            id='workcenter-dropdown',
            options=[],
            value=None
        )
        ]), width={"size": 3, "offset": 0}),
        dbc.Col(html.Div([dcc.Dropdown(
            id='workcenter-capacity-dropdown',
            options=[],
            value='Kapasite Grubu'
        )
        ]), width={"size": 3, "offset": 0}),
        dbc.Col(html.Div([
            html.Button('Workcenter Tablosunu İndir', id='btn-download-workcenter'),
            dcc.Download(id='download-workcenter')
        ]), style={'textAlign': 'right'}
        ),

    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='figx')
        ], style={'width': '600px'}),
        dbc.Col([
             AgGrid(
                id='workcenter_table',

                #columnDefs=transform_multilevel_columns_to_aggrid_defs(merged_df, buttons=0),
                #defaultColDef=defaultColDef,
                className="ag-theme-alpine-dark",
                columnSize="sizeToFit",
             )
        ])
    ]),

    dbc.Row([
        dbc.Col(html.Div([
            html.Button('Workcenter Kapasite Tablosunu İndir', id='btn-download-workcenter_kapasite'),
            dcc.Download(id='download-workcenter_kapasite')
        ]), width={"size": 3, "offset": 0}),  # Bu, butonu sağa hizalar
    ]),

    dbc.Row([
        AgGrid(
            id='capasity_table_workcenter',

            # columnDefs=transform_multilevel_columns_to_aggrid_defs(merged_df, buttons=0),
            # defaultColDef=defaultColDef,
            className="ag-theme-alpine-dark",
            columnSize="sizeToFit",
        )

    ]),

    dbc.Row([
        dbc.Col(html.Div([
            html.Button('Malzeme Tablosunu İndir', id='btn-download-malzeme'),
            dcc.Download(id='download-malzeme')
        ]), width={"size": 3, "offset": 5}),  # Bu, butonu sağa hizalar
    ]),

    dbc.Row([
        AgGrid(
            id='material_table',

            # columnDefs=transform_multilevel_columns_to_aggrid_defs(merged_df, buttons=0),
            # defaultColDef=defaultColDef,
            className="ag-theme-alpine-dark",
            columnSize="sizeToFit",
        )
    ])
], fluid=True)

@app.callback(
     Output("table_name", "data"),
     Output('unit-checkbox', 'value'),
     Output("kolon_sumb", "data"),
     Output("kolon_sum", "data"),
     Output("kolon_list", "data"),
     Input("interval-component", "n_intervals"),
     Input('unit-checkbox', 'value'),
     Input('data-type-dropdown', 'value')
)
def selected_table(n,selected_units,selected_type):


    if 'İhtiyaç Miktarı' in selected_type:
        table_name = 'VLFCAPFINALPIVOT'
        monthly_columns = generate_weekly_columns()

        format1_sumb = monthly_columns['format1']
        format2_sum = monthly_columns['format2']
        format3_list = monthly_columns['format3']

    elif 'Sipariş Miktarı' in selected_type:
        table_name = 'VLFCAPFINALSIPARIS'
        monthly_columns = generate_weekly_columns()

        format1_sumb = monthly_columns['format1']
        format2_sum = monthly_columns['format2']
        format3_list = monthly_columns['format3']
    elif 'Öngörü Miktarı' in selected_type:
        table_name = 'VLFCAPFINALOY'
        monthly_columns = generate_monthly_columns()

        format1_sumb = monthly_columns['format1']
        format2_sum = monthly_columns['format2']
        format3_list = monthly_columns['format3']

    if len(selected_units) > 1:
        selected_units = [selected_units[-1]]
    return table_name,selected_units,format1_sumb,format2_sum,format3_list
@app.callback(
     Output("costcenter-dropdown", "options"),
     Output("costcenter-dropdown", "value"),
     Output('costcenter_table', 'rowData'),
     Output('costcenter_table', 'columnDefs'),
     Input("table_name", "data"),
     State('unit-checkbox', 'value'),
     State("table_name", "data"),
     State("kolon_sum", "data"),
)
def update_graph(n,selected_units,table_name,kolon_sum):

    df = f"SELECT DISTINCT COSTCENTER FROM {table_name} GROUP BY COSTCENTER ORDER BY COSTCENTER"
    df = ag.run_query(df)

    sorted_costcenters = df['COSTCENTER'].tolist()
    sorted_costcenters = sorted(sorted_costcenters)
    options_list = [{'label': wc, 'value': wc} for wc in sorted_costcenters]
    first_option = options_list[0]['value'] if options_list else None

    sql_query = f"SELECT COSTCENTER,{kolon_sum} FROM {table_name} GROUP BY COSTCENTER ORDER BY COSTCENTER"
    df_pivot = ag.run_query(sql_query)
    print(df_pivot)
    print("here")
    df_pivot = df_pivot.round(0)
    if 'hours' in selected_units:
        df_pivot.iloc[:, 1:] = df_pivot.iloc[:, 1:] / 60
        df_pivot = df_pivot.round(1)
    elif 'shifts' in selected_units:
        df_pivot.iloc[:, 1:] = df_pivot.iloc[:, 1:] / 510
        df_pivot = df_pivot.round(1)

    data = df_pivot.to_dict('records')  # rowData için uygun format
    column_definitions = [{'headerName': col, 'field': col, 'sortable': True, 'filter': True} for col in
                          df_pivot.columns]
    return options_list, first_option, data, column_definitions


@app.callback(Output('workcenter-capacity-dropdown', 'options'),
              Output('fig', 'figure'),
              Input('costcenter-dropdown', 'value'),
              State('unit-checkbox', 'value'),
              State("table_name", "data"),
              State("kolon_sum", "data"),
)
def update_capacity_dropdown(selected_costcenter,selected_units,table_name,kolon_sum):
    sum_df_wc_cap_query = f"SELECT DISTINCT CAPGRUP FROM {table_name} WHERE COSTCENTER = '{selected_costcenter}' ORDER BY CAPGRUP"
    sum_df_wc_cap = ag.run_query(sum_df_wc_cap_query)
    unique_workcenters_cap = sum_df_wc_cap["CAPGRUP"].unique().tolist()
    sorted_workcenters_cap = sorted(unique_workcenters_cap)
    sorted_workcenters_cap.insert(0, "Kapasite Grubu")
    # sorted_workcenters_cap.append("Hepsi")
    options_list_cap = [{'label': wc, 'value': wc} for wc in sorted_workcenters_cap]

    sum_df_fig = f"SELECT COSTCENTER,{kolon_sum} FROM {table_name} WHERE COSTCENTER = '{selected_costcenter}' GROUP BY COSTCENTER ORDER BY COSTCENTER"
    sum_df_fig = ag.run_query(sum_df_fig)
    if 'hours' in selected_units:
        sum_df_fig.iloc[:, 1:] = sum_df_fig.iloc[:, 1:] / 60
        sum_df_fig = sum_df_fig.round(1)
    elif 'shifts' in selected_units:
        sum_df_fig.iloc[:, 1:] = sum_df_fig.iloc[:, 1:] / 510
        sum_df_fig = sum_df_fig.round(1)
    pivot_df_fig = pd.melt(sum_df_fig, id_vars=['COSTCENTER'], var_name='current_week', value_name='value_min')

    print(pivot_df_fig)
    print("gör")

    if len(pivot_df_fig) == 0:
        fig = go.Figure()
    else:
        fig = px.bar(pivot_df_fig, x='current_week', y='value_min')
        fig.update_xaxes(type='category')
    return options_list_cap,fig





@app.callback(
    [Output('capasity_table_costcenter', 'rowData'),
     Output('workcenter_table', 'rowData'),
     Output('capasity_table_costcenter', 'columnDefs'),
     Output('workcenter_table', 'columnDefs'),
     Output('workcenter-dropdown', 'options'),
     Output('workcenter-dropdown', 'value'),
     Output('iscapacity_trigger', 'data')],
    [Input('costcenter-dropdown', 'value'),
     Input('workcenter-capacity-dropdown', 'value')],
    State('unit-checkbox', 'value'),
    State('numeric-input', 'value'),
    State("table_name", "data"),
    State("kolon_sumb", "data"),
    State("kolon_sum", "data"),
    State("kolon_list", "data"),
)
def update_costcenter_table(selected_costcenter, selected_capgrp,selected_units,selected_verimlilik,table_name,kolon_sumb,kolon_sum,kolon_list):
    # Default case
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'costcenter-dropdown':
        df_pivot = f"SELECT COSTCENTER,{kolon_sum} FROM {table_name} WHERE COSTCENTER = '{selected_costcenter}' GROUP BY COSTCENTER ORDER BY COSTCENTER"
        sum_df = ag.run_query(df_pivot)
        sum_df_wc_cap_query = f"SELECT CAPWORK,{kolon_sum} FROM {table_name} WHERE COSTCENTER = '{selected_costcenter}' GROUP BY CAPWORK ORDER BY CAPWORK"
        sum_df_wc_cap = ag.run_query(sum_df_wc_cap_query)
        sum_df_wc = ag.run_query(sum_df_wc_cap_query)
        sum_df_wc_cap_work = f"SELECT {kolon_sumb} FROM (SELECT COSTCENTER,CAPWORK FROM {table_name} GROUP BY CAPWORK,COSTCENTER) A LEFT JOIN VLFVARDIYASURE B ON A.CAPWORK = B.WORKCENTER WHERE A.COSTCENTER = '{selected_costcenter}' GROUP BY A.COSTCENTER"
        sum_df_wc_cap_work = ag.run_query(sum_df_wc_cap_work)
        iscapacity_control = 1

    elif button_id == 'workcenter-capacity-dropdown':
        df_pivot = f"SELECT COSTCENTER,{kolon_sum} FROM {table_name} WHERE COSTCENTER = '{selected_costcenter}' GROUP BY COSTCENTER ORDER BY COSTCENTER"
        sum_df = ag.run_query(df_pivot)
        sum_df_wc_cap_query = f"SELECT CAPWORK,{kolon_sum} FROM {table_name} WHERE CAPGRUP = '{selected_capgrp}' AND  COSTCENTER = '{selected_costcenter}' GROUP BY CAPWORK ORDER BY CAPWORK"
        sum_df_wc_cap = ag.run_query(sum_df_wc_cap_query)

        filtered_df_cap = f"SELECT CAPWORK,{kolon_sum} FROM {table_name} WHERE CAPGRUP = '{selected_capgrp}' AND COSTCENTER = '{selected_costcenter}' GROUP BY CAPWORK ORDER BY CAPWORK"
        sum_df_wc = ag.run_query(filtered_df_cap)
        sum_df_wc_cap_work = f"SELECT {kolon_sumb} FROM (SELECT COSTCENTER,CAPWORK,CAPGRUP FROM {table_name} GROUP BY CAPWORK,COSTCENTER,CAPGRUP) A LEFT JOIN VLFVARDIYASURE B ON A.CAPWORK = B.WORKCENTER WHERE A.COSTCENTER = '{selected_costcenter}' AND A.CAPGRUP = '{selected_capgrp}' GROUP BY A.COSTCENTER"
        sum_df_wc_cap_work = ag.run_query(sum_df_wc_cap_work)
        iscapacity_control = 2

    if 'hours' in selected_units:
        sum_df.iloc[:, 1:] = sum_df.iloc[:, 1:] / 60
        sum_df = sum_df.round(1)
        sum_df_wc.iloc[:, 1:] = sum_df_wc.iloc[:, 1:] / 60
        sum_df_wc = sum_df_wc.round(1)
    elif 'shifts' in selected_units:
        sum_df.iloc[:, 1:] = sum_df.iloc[:, 1:] / 510
        sum_df = sum_df.round(1)
        sum_df_wc.iloc[:, 1:] = sum_df_wc.iloc[:, 1:] / 510
        sum_df_wc = sum_df_wc.round(1)
    sum_df['STAT'] = 'Kapasite İhtiyacı'
    weeks = list(kolon_list.values())
    filtered_sum_df = sum_df[['STAT'] + weeks]

    sum_df_wc_cap_work.iloc[:, 1:] = sum_df_wc_cap_work.iloc[:, 1:] * selected_verimlilik
    sum_df_wc_cap_work.iloc[:, 1:] = sum_df_wc_cap_work.iloc[:, 1:] / 100

    if 'hours' in selected_units:
        sum_df_wc_cap_work.iloc[:, 1:] = sum_df_wc_cap_work.iloc[:, 1:] / 60
        sum_df_wc_cap_work = sum_df_wc_cap_work.round(1)

    elif 'shifts' in selected_units:
        sum_df_wc_cap_work.iloc[:, 1:] = sum_df_wc_cap_work.iloc[:, 1:] / 510
        sum_df_wc_cap_work = sum_df_wc_cap_work.round(1)
    else:
        sum_df_wc_cap_work = sum_df_wc_cap_work.round(0)
    data_for_new_row = {'STAT': 'Toplam Kapasite'}
    data_for_new_row.update(sum_df_wc_cap_work.iloc[0].to_dict())  # Bu satırda dict nesnesine çeviriyoruz
    new_row = pd.Series(data_for_new_row)  # Dict'i Series'e dönüştürüyoruz
    # Yeni satırı DataFrame'e ekle

    cap_df = pd.concat([filtered_sum_df, new_row.to_frame().T], ignore_index=True)

    result_row = {'STAT': 'Kapasite Farkı'}
    result_row.update(cap_df[list(kolon_list.values())].iloc[1] - cap_df[list(kolon_list.values())].iloc[0])

    # Append the result as a new row in the DataFrame
    cap_df = cap_df.append(result_row, ignore_index=True)

    numeric_cols = cap_df.columns.difference(['STAT'])
    # 'result_row' satırının kümülatif toplamını hesaplayın
    cumulative_sum = cap_df.loc[cap_df['STAT'] == 'Kapasite Farkı', numeric_cols].cumsum(axis=1)
    if 'hours' in selected_units:
        cumulative_sum = cumulative_sum.round(1)
    elif 'shifts' in selected_units:
        cumulative_sum = cumulative_sum.round(1)
    else:
        cumulative_sum = cumulative_sum.round(0)

    # Kümülatif toplam sonuçlarını yeni bir satıra ekleyin
    new_cumulative_row = {'STAT': 'Kümülatif Toplam'}
    new_cumulative_row.update(cumulative_sum.iloc[0])

    # Yeni kümülatif toplam satırını cap_df DataFrame'ine ekleyin
    cap_df = cap_df.append(new_cumulative_row, ignore_index=True)

    # 'Kapasite İhtiyacı' ve 'Toplam Kapasite' satırlarını seçin
    uretim_ihtiyaci = cap_df[cap_df['STAT'] == 'Kapasite İhtiyacı'].iloc[0]
    toplam_kapasite = cap_df[cap_df['STAT'] == 'Toplam Kapasite'].iloc[0]

    # Doluluk oranını hesaplamak için bir boş liste oluşturun
    doluluk_orani = []
    # Her bir numeric kolon için doluluk oranını hesaplayın
    for col in kolon_list:
        # İlk kolon için özel durum: Eğer 'Toplam Kapasite' 0 ise, doluluk oranı da 0 olmalıdır
        if toplam_kapasite[col] == 0:
            doluluk_orani.append(0)
        else:
            # Doluluk oranını hesaplayın ve listeye ekleyin
            oran = (uretim_ihtiyaci[col] / toplam_kapasite[col]) * 100
            doluluk_orani.append(oran)

    # Doluluk oranlarını içeren yeni bir satır oluşturun
    doluluk_orani_satiri = pd.DataFrame([doluluk_orani], columns=kolon_list)
    doluluk_orani_satiri['STAT'] = 'Doluluk Oranı'
    if 'hours' in selected_units:
        doluluk_orani_satiri = doluluk_orani_satiri.round(1)
    elif 'shifts' in selected_units:
        doluluk_orani_satiri = doluluk_orani_satiri.round(1)
    else:
        doluluk_orani_satiri = doluluk_orani_satiri.round(0)

    # Yeni satırı DataFrame'e ekleyin
    cap_df_prepared = pd.concat([cap_df, doluluk_orani_satiri], ignore_index=True)

    column_definitions = [{'headerName': col, 'field': col, 'sortable': True, 'filter': True} for col in
                          sum_df_wc.columns]
    column_definitions_cap = [{'headerName': col, 'field': col, 'sortable': True, 'filter': True} for col in
                          cap_df_prepared.columns]

    unique_workcenters = sum_df_wc_cap["CAPWORK"].unique().tolist()
    sorted_workcenters = sorted(unique_workcenters)
    # sorted_workcenters.append("Hepsi")
    sorted_workcenters.insert(0, "Hepsi")
    options_list = [{'label': wc, 'value': wc} for wc in sorted_workcenters]
    first_option = options_list[0] if options_list else None

    return (cap_df_prepared.to_dict('records'), sum_df_wc.to_dict('records'),column_definitions_cap,column_definitions,
            options_list,first_option["value"],iscapacity_control)





@app.callback(
    [Output('figx', 'figure'),
     Output('material_table', 'rowData'),
     Output('material_table', 'columnDefs'),
     Output('capasity_table_workcenter', 'rowData'),
     Output('capasity_table_workcenter', 'columnDefs'),
     Output('isfirst_trigger', 'data')],
    Input('workcenter-dropdown', 'value'),
    Input('workcenter-capacity-dropdown', 'value'),
    State('costcenter-dropdown', 'value'),
    State('isfirst_trigger', 'data'),
    State('iscapacity_trigger', 'data'),
    State('unit-checkbox', 'value'),
    State('numeric-input', 'value'),
    State("table_name", "data"),
    State("kolon_sumb", "data"),
    State("kolon_sum", "data"),
    State("kolon_list", "data"),
)
def update_workcenter_table(selected_workcenter,selected_capgrp,selected_costcenter,isfirst,is_capasity,selected_units,selected_verimlilik,table_name,kolon_sumb,kolon_sum,kolon_list):

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    print(button_id)
    print("here5")
    print(selected_workcenter)
    print("here6")
    print("here6")
    print(isfirst)
    print("here6")

    if selected_workcenter == "Hepsi":

        if (button_id == 'workcenter-dropdown') | (isfirst == 0):
             if is_capasity == 1:
                filtered_df_pivot_cap_list = f"SELECT * FROM {table_name} WHERE COSTCENTER = '{selected_costcenter}'"
                filtered_df_pivot_cap_list = ag.run_query(filtered_df_pivot_cap_list)
                filtered_df_pivot_cap = filtered_df_pivot_cap_list

                sum_df_pivot = filtered_df_pivot_cap_list.groupby(['COSTCENTER'], as_index=False).sum()
                print("summmm")
                print(sum_df_pivot)

             elif is_capasity == 2:
                 filtered_df_pivot_cap_list = f"SELECT * FROM {table_name} WHERE CAPGRUP = '{selected_capgrp}' AND COSTCENTER = '{selected_costcenter}'"

                 filtered_df_pivot_cap_list = ag.run_query(filtered_df_pivot_cap_list)
                 sum_df_pivot = filtered_df_pivot_cap_list.groupby(['CAPGRUP'], as_index=False).sum()
                 print("summmm2")
                 print(sum_df_pivot)
                 filtered_df_pivot_cap = filtered_df_pivot_cap_list
             print(filtered_df_pivot_cap_list)
             print("workhere2")
             unique_workcenters = filtered_df_pivot_cap_list["CAPWORK"].unique().tolist()
             print(unique_workcenters)
             print("workhere3")
             #sorted_workcenters = sorted(unique_workcenters)
             #first_element = sorted_workcenters[0] if sorted_workcenters else None
             #filtered_df_pivot_cap = filtered_df_pivot_cap_list[filtered_df_pivot_cap_list['CAPWORK'] == first_element]

             filtered_df_pivot = filtered_df_pivot_cap_list.groupby(['MATERIAL'], as_index=False).sum()
             filtered_df_pivot = filtered_df_pivot.round(0)
             if 'hours' in selected_units:
                 filtered_df_pivot.iloc[:, 1:] = filtered_df_pivot.iloc[:, 1:] / 60
                 filtered_df_pivot = filtered_df_pivot.round(1)

             elif 'shifts' in selected_units:
                 filtered_df_pivot.iloc[:, 1:] = filtered_df_pivot.iloc[:, 1:] / 510
                 filtered_df_pivot = filtered_df_pivot.round(1)
             print(filtered_df_pivot)
             print("workhere4")


        elif button_id == 'workcenter-capacity-dropdown':
             filtered_df_pivot_cap_list = f"SELECT * FROM {table_name} WHERE CAPGRUP = '{selected_capgrp}' AND COSTCENTER = '{selected_costcenter}'"
             filtered_df_pivot_cap_list = ag.run_query(filtered_df_pivot_cap_list)
             filtered_df_pivot_cap = filtered_df_pivot_cap_list
             print(filtered_df_pivot_cap_list)
             print("here2")
             unique_workcenters = filtered_df_pivot_cap_list["CAPWORK"].unique().tolist()
             print(unique_workcenters)
             print("here3")
             #sorted_workcenters = sorted(unique_workcenters)
             #first_element = sorted_workcenters[0] if sorted_workcenters else None
             #filtered_df_pivot_cap = filtered_df_pivot_cap_list[filtered_df_pivot_cap_list['CAPWORK'] == first_element]
             filtered_df_pivot = filtered_df_pivot_cap_list.groupby(['MATERIAL'], as_index=False).sum()
             filtered_df_pivot = filtered_df_pivot.round(0)
             if 'hours' in selected_units:
                 filtered_df_pivot.iloc[:, 1:] = filtered_df_pivot.iloc[:, 1:] / 60
                 filtered_df_pivot = filtered_df_pivot.round(1)

             elif 'shifts' in selected_units:
                 filtered_df_pivot.iloc[:, 1:] = filtered_df_pivot.iloc[:, 1:] / 510
                 filtered_df_pivot = filtered_df_pivot.round(1)
             print(filtered_df_pivot)
             print("here4")
             sum_df_pivot = filtered_df_pivot_cap_list.groupby(['CAPGRUP'], as_index=False).sum()
             print("summmm3")
             print(sum_df_pivot)

    else:
        if button_id == 'workcenter-dropdown':
             if is_capasity == 1:
                filtered_df_pivot_cap = f"SELECT * FROM {table_name} WHERE COSTCENTER = '{selected_costcenter}'"
                filtered_df_pivot_cap = ag.run_query(filtered_df_pivot_cap)
             elif is_capasity == 2:
                 filtered_df_pivot_cap = f"SELECT * FROM {table_name} WHERE CAPGRUP = '{selected_capgrp}' AND COSTCENTER = '{selected_costcenter}'"
                 filtered_df_pivot_cap = ag.run_query(filtered_df_pivot_cap)
             filtered_df_pivot_cap = filtered_df_pivot_cap[filtered_df_pivot_cap['CAPWORK'] == selected_workcenter]
             filtered_df_pivot = filtered_df_pivot_cap[filtered_df_pivot_cap['CAPWORK'] == selected_workcenter]
             filtered_df_pivot = filtered_df_pivot.groupby(['MATERIAL'], as_index=False).sum()
             filtered_df_pivot = filtered_df_pivot.round(0)
             if 'hours' in selected_units:
                 filtered_df_pivot.iloc[:, 1:] = filtered_df_pivot.iloc[:, 1:] / 60
                 filtered_df_pivot = filtered_df_pivot.round(1)

             elif 'shifts' in selected_units:
                 filtered_df_pivot.iloc[:, 1:] = filtered_df_pivot.iloc[:, 1:] / 510
                 filtered_df_pivot = filtered_df_pivot.round(1)
             sum_df_pivot = filtered_df_pivot_cap.groupby(['CAPWORK'], as_index=False).sum()
             print("summmm4")
             print(sum_df_pivot)

        elif button_id == 'workcenter-capacity-dropdown':
             filtered_df_pivot_cap = f"SELECT * FROM {table_name} WHERE CAPGRUP = '{selected_capgrp}' AND COSTCENTER = '{selected_costcenter}'"
             filtered_df_pivot_cap = ag.run_query(filtered_df_pivot_cap)
             print(filtered_df_pivot_cap)
             print("workcen3")
             filtered_df_pivot = filtered_df_pivot_cap[filtered_df_pivot_cap['CAPGRUP'] == selected_capgrp]
             filtered_df_pivot = filtered_df_pivot.groupby(['MATERIAL'], as_index=False).sum()
             filtered_df_pivot = filtered_df_pivot.round(0)
             if 'hours' in selected_units:
                 filtered_df_pivot.iloc[:, 1:] = filtered_df_pivot.iloc[:, 1:] / 60
                 filtered_df_pivot = filtered_df_pivot.round(1)

             elif 'shifts' in selected_units:
                 filtered_df_pivot.iloc[:, 1:] = filtered_df_pivot.iloc[:, 1:] / 510
                 filtered_df_pivot = filtered_df_pivot.round(1)
             sum_df_pivot = filtered_df_pivot_cap.groupby(['CAPGRUP'], as_index=False).sum()
             print("summmm5")
             print(sum_df_pivot)


    sum_df_pivot['STAT'] = 'Kapasite İhtiyacı'
    weeks = list(kolon_list.values())
    filtered_sum_df = sum_df_pivot[['STAT'] + weeks]

    #####################################

    if (button_id == 'workcenter-dropdown') | (isfirst == 0):
       print("den")
       if is_capasity == 1:
            if selected_workcenter == "Hepsi":
              filtered_df_fig = f"SELECT COSTCENTER,{kolon_sum} FROM {table_name} WHERE COSTCENTER = '{selected_costcenter}' GROUP BY COSTCENTER ORDER BY COSTCENTER"
              filtered_df_fig = ag.run_query(filtered_df_fig)
              print(filtered_df_fig)
              print("kar")
              sum_df = filtered_df_fig.round(0)
              if 'hours' in selected_units:
                  filtered_df_fig.iloc[:, 1:] = filtered_df_fig.iloc[:, 1:] / 60
                  sum_df = filtered_df_fig.round(1)

              elif 'shifts' in selected_units:
                  filtered_df_fig.iloc[:, 1:] = filtered_df_fig.iloc[:, 1:] / 510
                  sum_df = filtered_df_fig.round(1)
              sum_df = pd.melt(sum_df, id_vars=['COSTCENTER'], var_name='current_week', value_name='value_min')
            else:
              filtered_df_fig = f"SELECT CAPWORK,{kolon_sum} FROM {table_name} WHERE CAPWORK = '{selected_workcenter}' AND COSTCENTER = '{selected_costcenter}' GROUP BY CAPWORK ORDER BY CAPWORK"
              filtered_df_fig = ag.run_query(filtered_df_fig)
              sum_df = filtered_df_fig.round(0)
              if 'hours' in selected_units:
                  filtered_df_fig.iloc[:, 1:] = filtered_df_fig.iloc[:, 1:] / 60
                  sum_df = filtered_df_fig.round(1)

              elif 'shifts' in selected_units:
                  filtered_df_fig.iloc[:, 1:] = filtered_df_fig.iloc[:, 1:] / 510
                  sum_df = filtered_df_fig.round(1)
              sum_df = pd.melt(sum_df, id_vars=['CAPWORK'], var_name='current_week', value_name='value_min')
       elif is_capasity == 2:
           if selected_workcenter == "Hepsi":
              filtered_df_fig = f"SELECT CAPGRUP,{kolon_sum} FROM {table_name} WHERE CAPGRUP = '{selected_capgrp}' AND COSTCENTER = '{selected_costcenter}' GROUP BY CAPGRUP ORDER BY CAPGRUP"
              filtered_df_fig = ag.run_query(filtered_df_fig)
              sum_df = filtered_df_fig.round(0)
              if 'hours' in selected_units:
                  filtered_df_fig.iloc[:, 1:] = filtered_df_fig.iloc[:, 1:] / 60
                  sum_df = filtered_df_fig.round(1)

              elif 'shifts' in selected_units:
                  filtered_df_fig.iloc[:, 1:] = filtered_df_fig.iloc[:, 1:] / 510
                  sum_df = filtered_df_fig.round(1)
              sum_df = pd.melt(sum_df, id_vars=['CAPGRUP'], var_name='current_week', value_name='value_min')
           else:
              filtered_df_fig = f"SELECT CAPWORK,{kolon_sum} FROM {table_name} WHERE CAPWORK = '{selected_workcenter}' AND CAPGRUP = '{selected_capgrp}' AND COSTCENTER = '{selected_costcenter}' GROUP BY CAPWORK ORDER BY CAPWORK"
              filtered_df_fig = ag.run_query(filtered_df_fig)
              sum_df = filtered_df_fig.round(0)
              if 'hours' in selected_units:
                  filtered_df_fig.iloc[:, 1:] = filtered_df_fig.iloc[:, 1:] / 60
                  sum_df = filtered_df_fig.round(1)

              elif 'shifts' in selected_units:
                  filtered_df_fig.iloc[:, 1:] = filtered_df_fig.iloc[:, 1:] / 510
                  sum_df = filtered_df_fig.round(1)
              sum_df = pd.melt(sum_df, id_vars=['CAPWORK'], var_name='current_week', value_name='value_min')

    elif button_id == 'workcenter-capacity-dropdown' :
        if selected_workcenter == "Hepsi":
          filtered_df_fig = f"SELECT CAPGRUP,{kolon_sum} FROM {table_name} WHERE CAPGRUP = '{selected_capgrp}' AND COSTCENTER = '{selected_costcenter}' GROUP BY CAPGRUP ORDER BY CAPGRUP"
          filtered_df_fig = ag.run_query(filtered_df_fig)
          sum_df = filtered_df_fig.round(0)
          if 'hours' in selected_units:
              filtered_df_fig.iloc[:, 1:] = filtered_df_fig.iloc[:, 1:] / 60
              sum_df = filtered_df_fig.round(1)

          elif 'shifts' in selected_units:
              filtered_df_fig.iloc[:, 1:] = filtered_df_fig.iloc[:, 1:] / 510
              sum_df = filtered_df_fig.round(1)
          sum_df = pd.melt(sum_df, id_vars=['CAPGRUP'], var_name='current_week', value_name='value_min')
        else:
          filtered_df_fig = f"SELECT CAPWORK,{kolon_sum} FROM {table_name} WHERE CAPWORK = '{selected_workcenter}' AND CAPGRUP = '{selected_capgrp}' AND COSTCENTER = '{selected_costcenter}' GROUP BY CAPWORK ORDER BY CAPWORK"
          filtered_df_fig = ag.run_query(filtered_df_fig)
          sum_df = filtered_df_fig.round(0)
          if 'hours' in selected_units:
              filtered_df_fig.iloc[:, 1:] = filtered_df_fig.iloc[:, 1:] / 60
              sum_df = filtered_df_fig.round(1)

          elif 'shifts' in selected_units:
              filtered_df_fig.iloc[:, 1:] = filtered_df_fig.iloc[:, 1:] / 510
              sum_df = filtered_df_fig.round(1)
          sum_df = pd.melt(sum_df, id_vars=['CAPWORK'], var_name='current_week', value_name='value_min')
    print(sum_df)
    print("bur3")
    if len(sum_df) == 0:
        figx = go.Figure()
    else:
        figx = px.bar(sum_df, x='current_week', y='value_min')
        figx.update_xaxes(type='category')


    if (button_id == 'workcenter-dropdown') | (isfirst == 0):
       if is_capasity == 1:
           if selected_workcenter == "Hepsi":
              sum_df_pivot = f"SELECT {kolon_sumb} FROM (SELECT COSTCENTER,CAPWORK FROM {table_name} GROUP BY CAPWORK,COSTCENTER) A LEFT JOIN VLFVARDIYASURE B ON A.CAPWORK = B.WORKCENTER WHERE A.COSTCENTER = '{selected_costcenter}' GROUP BY A.COSTCENTER"
              sum_df_pivot = ag.run_query(sum_df_pivot)
           else:
              sum_df_pivot = f"SELECT {kolon_sumb} FROM (SELECT COSTCENTER,CAPWORK FROM {table_name} GROUP BY CAPWORK,COSTCENTER) A LEFT JOIN VLFVARDIYASURE B ON A.CAPWORK = B.WORKCENTER WHERE A.COSTCENTER = '{selected_costcenter}' AND A.CAPWORK = '{selected_workcenter}' GROUP BY A.COSTCENTER,A.CAPWORK"
              sum_df_pivot = ag.run_query(sum_df_pivot)
       elif is_capasity == 2:
           if selected_workcenter == "Hepsi":
               sum_df_pivot = f"SELECT {kolon_sumb} FROM (SELECT COSTCENTER,CAPWORK,CAPGRUP FROM {table_name} GROUP BY CAPWORK,COSTCENTER,CAPGRUP) A LEFT JOIN VLFVARDIYASURE B ON A.CAPWORK = B.WORKCENTER WHERE A.COSTCENTER = '{selected_costcenter}' AND A.CAPGRUP = '{selected_capgrp}' GROUP BY A.COSTCENTER,A.CAPGRUP"
               sum_df_pivot = ag.run_query(sum_df_pivot)
           else:
               sum_df_pivot = f"SELECT {kolon_sumb} FROM (SELECT COSTCENTER,CAPWORK,CAPGRUP FROM {table_name} GROUP BY CAPWORK,COSTCENTER,CAPGRUP) A LEFT JOIN VLFVARDIYASURE B ON A.CAPWORK = B.WORKCENTER WHERE A.COSTCENTER = '{selected_costcenter}' AND A.CAPGRUP = '{selected_capgrp}' AND A.CAPWORK = '{selected_workcenter}' GROUP BY A.COSTCENTER,A.CAPGRUP"
               sum_df_pivot = ag.run_query(sum_df_pivot)
    elif button_id == 'workcenter-capacity-dropdown':
        if selected_workcenter == "Hepsi":
            sum_df_pivot = f"SELECT {kolon_sumb} FROM (SELECT COSTCENTER,CAPWORK,CAPGRUP FROM {table_name} GROUP BY CAPWORK,COSTCENTER,CAPGRUP) A LEFT JOIN VLFVARDIYASURE B ON A.CAPWORK = B.WORKCENTER WHERE A.COSTCENTER = '{selected_costcenter}' AND A.CAPGRUP = '{selected_capgrp}' GROUP BY A.COSTCENTER,A.CAPGRUP"
            sum_df_pivot = ag.run_query(sum_df_pivot)
        else:
            sum_df_pivot = f"SELECT {kolon_sumb} FROM (SELECT COSTCENTER,CAPWORK,CAPGRUP FROM {table_name} GROUP BY CAPWORK,COSTCENTER,CAPGRUP) A LEFT JOIN VLFVARDIYASURE B ON A.CAPWORK = B.WORKCENTER WHERE A.COSTCENTER = '{selected_costcenter}' AND A.CAPGRUP = '{selected_capgrp}' AND A.CAPWORK = '{selected_workcenter}' GROUP BY A.COSTCENTER,A.CAPGRUP"
            sum_df_pivot = ag.run_query(sum_df_pivot)

    sum_df_pivot.iloc[:, 1:] = sum_df_pivot.iloc[:, 1:] * selected_verimlilik
    sum_df_pivot.iloc[:, 1:] = sum_df_pivot.iloc[:, 1:] / 100

    data_for_new_row = {'STAT': 'Toplam Kapasite'}
    data_for_new_row.update(sum_df_pivot.iloc[0].to_dict())    # Yeni satırı DataFrame'e ekle
    new_row = pd.Series(data_for_new_row)
    cap_df = pd.concat([filtered_sum_df, new_row.to_frame().T], ignore_index=True)

    result_row = {'STAT': 'Kapasite Farkı'}
    result_row.update(cap_df[list(kolon_list.values())].iloc[1] - cap_df[list(kolon_list.values())].iloc[0])

    cap_df = pd.concat([cap_df, pd.DataFrame([result_row])], ignore_index=True)

    numeric_cols = cap_df.columns.difference(['STAT'])

    # 'result_row' satırının kümülatif toplamını hesaplayın
    cumulative_sum = cap_df.loc[cap_df['STAT'] == 'Kapasite Farkı', numeric_cols].cumsum(axis=1)

    # Kümülatif toplam sonuçlarını yeni bir satıra ekleyin
    new_cumulative_row = {'STAT': 'Kümülatif Toplam'}
    new_cumulative_row.update(cumulative_sum.iloc[0])

    # Yeni kümülatif toplam satırını cap_df DataFrame'ine ekleyin
    cap_df = cap_df.append(new_cumulative_row, ignore_index=True)

    # 'Kapasite İhtiyacı' ve 'Toplam Kapasite' satırlarını seçin
    uretim_ihtiyaci = cap_df[cap_df['STAT'] == 'Kapasite İhtiyacı'].iloc[0]
    toplam_kapasite = cap_df[cap_df['STAT'] == 'Toplam Kapasite'].iloc[0]

    # Doluluk oranını hesaplamak için bir boş liste oluşturun
    doluluk_orani = []

    # Her bir numeric kolon için doluluk oranını hesaplayın
    for col in kolon_list:
        # İlk kolon için özel durum: Eğer 'Toplam Kapasite' 0 ise, doluluk oranı da 0 olmalıdır
        if toplam_kapasite[col] == 0:
            doluluk_orani.append(0)
        else:
            # Doluluk oranını hesaplayın ve listeye ekleyin
            oran = (uretim_ihtiyaci[col] / toplam_kapasite[col]) * 100
            doluluk_orani.append(oran)

    # Doluluk oranlarını içeren yeni bir satır oluşturun
    doluluk_orani_satiri = pd.DataFrame([doluluk_orani], columns=kolon_list)
    doluluk_orani_satiri['STAT'] = 'Doluluk Oranı'

    # Yeni satırı DataFrame'e ekleyin
    cap_df_prepared = pd.concat([cap_df, doluluk_orani_satiri], ignore_index=True)

    #column_definitions = [{'headerName': col, 'field': col, 'sortable': True, 'filter': True} for col in
     #                     filtered_df_pivot.columns]

    column_definitions = [{'headerName': 'MATERIAL', 'field': 'MATERIAL', 'sortable': True, 'filter': True}] + \
                         [{'headerName': week, 'field': date, 'sortable': True, 'filter': True} for week, date in
                          kolon_list.items()]
    column_definitions_cap = [{'headerName': col, 'field': col, 'sortable': True, 'filter': True} for col in
                              cap_df_prepared.columns]
    cap_df_prepared = cap_df_prepared.round(0)
    if 'hours' in selected_units:
        cap_df_prepared.iloc[:, 1:] = cap_df_prepared.iloc[:, 1:] / 60
        cap_df_prepared = cap_df_prepared.round(1)

    elif 'shifts' in selected_units:
        cap_df_prepared.iloc[:, 1:] = cap_df_prepared.iloc[:, 1:] / 510
        cap_df_prepared = cap_df_prepared.round(1)
    return figx, filtered_df_pivot.to_dict('records'),column_definitions, cap_df_prepared.to_dict('records'),column_definitions_cap,isfirst + 1


@app.callback(
    Output('download-costcenter', 'data'),
    Input('btn-download-costcenter', 'n_clicks'),
    State('costcenter_table', 'rowData'),
    prevent_initial_call=True
)
def download_costcenter_data(n_clicks, table_data):

    filtered_df_pivot = pd.DataFrame(table_data)

    #filtered_df_pivot = filtered_df_pivot.round(1)
    # DataFrame'inizi oluşturun veya var olan bir DataFrame'i kullanın

    return dcc.send_data_frame(filtered_df_pivot.to_excel, "costcenter_data.xlsx", sheet_name="Costcenter")


@app.callback(
    Output('download-costcenter_kapasite', 'data'),
    Input('btn-download-costcenter_kapasite', 'n_clicks'),
    State('capasity_table_costcenter', 'rowData'),
    prevent_initial_call=True
)
def download_costcenter_capacity_data(n_clicks, table_data):
    filtered_df_pivot = pd.DataFrame(table_data)

    # filtered_df_pivot = filtered_df_pivot.round(1)
    # DataFrame'inizi oluşturun veya var olan bir DataFrame'i kullanın

    return dcc.send_data_frame(filtered_df_pivot.to_excel, "costcenter_capacity_data.xlsx", sheet_name="Costcenter Kapasite")


@app.callback(
    Output('download-workcenter', 'data'),
    Input('btn-download-workcenter', 'n_clicks'),
    State('workcenter_table', 'rowData'),
    prevent_initial_call=True
)
def download_workcenter_data(n_clicks, table_data):

    filtered_df_pivot = pd.DataFrame(table_data)

    #filtered_df_pivot = filtered_df_pivot.round(1)
    # DataFrame'inizi oluşturun veya var olan bir DataFrame'i kullanın

    return dcc.send_data_frame(filtered_df_pivot.to_excel, "workcenter_data.xlsx", sheet_name="Workcenter")

@app.callback(
    Output('download-workcenter_kapasite', 'data'),
    Input('btn-download-workcenter_kapasite', 'n_clicks'),
    State('capasity_table_workcenter', 'rowData'),
    prevent_initial_call=True
)
def download_workcenter_capacity_data(n_clicks, table_data):
    filtered_df_pivot = pd.DataFrame(table_data)

    # filtered_df_pivot = filtered_df_pivot.round(1)
    # DataFrame'inizi oluşturun veya var olan bir DataFrame'i kullanın

    return dcc.send_data_frame(filtered_df_pivot.to_excel, "workcenter_capacity_data.xlsx", sheet_name="Workcenter Kapasite")

@app.callback(
    Output('download-malzeme', 'data'),
    Input('btn-download-malzeme', 'n_clicks'),
    State('material_table', 'rowData'),
    prevent_initial_call=True
)
def download_malzeme_data(n_clicks, table_data):

    filtered_df_pivot = pd.DataFrame(table_data)

    #filtered_df_pivot = filtered_df_pivot.round(1)
    # DataFrame'inizi oluşturun veya var olan bir DataFrame'i kullanın

    return dcc.send_data_frame(filtered_df_pivot.to_excel, "malzeme_data.xlsx", sheet_name="Malzeme")
