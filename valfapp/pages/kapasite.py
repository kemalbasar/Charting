from datetime import datetime, timedelta
from dash import html
import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, Input, Output, State, ctx , no_update
from dash_ag_grid import AgGrid

from run.agent import ag
import plotly.express as px
from valfapp.app import app, cache, TIMEOUT

#@cache.memoize(timeout=TIMEOUT)
def create_weeks_for_query():
    start_date = datetime.now() - timedelta(weeks=1)
    weeks_list = []
    for i in range(19):  # Bu hafta dahil olmak üzere toplamda 19 hafta
        week_start = start_date + timedelta(weeks=i)
        year, week_num, _ = week_start.isocalendar()
        week_label = f"SUM([{year}-{str(week_num).zfill(2)}]) AS [{year}-{str(week_num).zfill(2)}]"
        weeks_list.append(week_label)

    return ", ".join(weeks_list)

#@cache.memoize(timeout=TIMEOUT)
def create_weeks_dict():

    start_date = datetime.now() - timedelta(weeks=1)

    # Önümüzdeki 18 hafta için yıl ve hafta numarasını içeren bir sözlük oluştur, hafta numarası iki basamaklı olacak şekilde
    weeks_dict = {}
    for i in range(19):  # Bu hafta dahil olmak üzere toplamda 19 hafta
        week_start = start_date + timedelta(weeks=i)
        year, week_num, _ = week_start.isocalendar()
        weeks_dict[f"{year}-{str(week_num).zfill(2)}"] = f"{year}-{str(week_num).zfill(2)}"

    return weeks_dict


#@cache.memoize(timeout=TIMEOUT)
def formatted_weeks_first():

    # Current date
    current_date = datetime.now()

    # Calculate the start of the current week (assuming weeks start on Monday)
    current_week_start = current_date - timedelta(days=current_date.weekday())

    # Generate the current week and the next 17 weeks
    weeks = [current_week_start + timedelta(weeks=i) for i in range(18)]  # Generating the weeks

    # Formatting weeks as 'Year_WeekNumber' using ISO week date
    # Adjusting to remove leading zeros and ensuring no week "00"
    formatted_weeks = [f"{week.strftime('%G')}_{int(week.strftime('%V'))}" for week in weeks]

    # Removing the first week if it is week 00 and prefixing with "IHT_"
    formatted_weeks = ["IHT_" + week for week in formatted_weeks if not week.endswith("_0")]

    formatted_weeks.insert(0, 'IHT0')
    formatted_weeks.insert(0, 'MATERIAL')
    formatted_weeks.insert(0, 'ANAMAMUL')
    formatted_weeks.insert(0, 'COSTCENTER')
    formatted_weeks.insert(0, 'CAPWORK')
    formatted_weeks.insert(0, 'WORKCUNT')
    formatted_weeks.insert(0, 'CAPGRUP')
    formatted_weeks.insert(0, 'STAND')

    formatted_weeks.insert(0, 'SURE_HESAPLAMA_KODU')
    formatted_weeks.insert(0, 'MACHINE')
    formatted_weeks.insert(0, 'LABOUR')
    formatted_weeks.insert(0, 'SETUP')
    formatted_weeks.insert(0, 'BASEQUAN')

    return formatted_weeks


layout = dbc.Container([
    dcc.Store(id='isfirst_trigger', data = 0),
    dcc.Store(id='iscapacity_trigger', data = 0),
    dbc.Row([
        dbc.Col(html.Div([html.Button("Cache Temizle", id="clear-cache-button"),
        html.Div(id="clear-cache-output")]
    ), width={"size": 3, "offset": 1}),
        dbc.Col(html.Div(dcc.Dropdown(
        id='section-dropdown',
        options=[{'label': i, 'value': i} for i in
                 ["Hepsi", "Plaka", "Checkvalf", "Pres"]],
        value='Hepsi'
    )
    ), width={"size": 3, "offset": 1})
    ]),

    dbc.Row([
        dbc.Col(html.Div([dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0, max_intervals=1),
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
     Output("costcenter-dropdown", "options"),
     Output("costcenter-dropdown", "value"),
     Output('costcenter_table', 'rowData'),
     Output('costcenter_table', 'columnDefs'),
     Input("interval-component", "n_intervals")
)
def update_graph(n):

    df = ag.run_query(r"SELECT DISTINCT COSTCENTER FROM VLFCAPFINALPIVOT GROUP BY COSTCENTER ORDER BY COSTCENTER")

    sorted_costcenters = df['COSTCENTER'].tolist()
    sorted_costcenters = sorted(sorted_costcenters)
    options_list = [{'label': wc, 'value': wc} for wc in sorted_costcenters]
    first_option = options_list[0]['value'] if options_list else None
    weeks_dict = create_weeks_for_query()
    sql_query = f"SELECT COSTCENTER,{weeks_dict} FROM VLFCAPFINALPIVOT GROUP BY COSTCENTER ORDER BY COSTCENTER"
    df_pivot = ag.run_query(sql_query)
    print(df_pivot)
    print("here")
    data = df_pivot.to_dict('records')  # rowData için uygun format
    column_definitions = [{'headerName': col, 'field': col, 'sortable': True, 'filter': True} for col in
                          df_pivot.columns]
    return options_list, first_option, data, column_definitions


@app.callback(Output('workcenter-capacity-dropdown', 'options'),
              Output('fig', 'figure'),
              Input('costcenter-dropdown', 'value')
)
def update_capacity_dropdown(selected_costcenter):
    weeks_dict_for_query = create_weeks_for_query()
    sum_df_wc_cap_query = f"SELECT DISTINCT CAPGRUP FROM VLFCAPFINALPIVOT WHERE COSTCENTER = '{selected_costcenter}' ORDER BY CAPGRUP"
    sum_df_wc_cap = ag.run_query(sum_df_wc_cap_query)
    unique_workcenters_cap = sum_df_wc_cap["CAPGRUP"].unique().tolist()
    sorted_workcenters_cap = sorted(unique_workcenters_cap)
    sorted_workcenters_cap.insert(0, "Kapasite Grubu")
    # sorted_workcenters_cap.append("Hepsi")
    options_list_cap = [{'label': wc, 'value': wc} for wc in sorted_workcenters_cap]

    sum_b = f"SELECT current_week,COSTCENTER,SUM(value_min) AS value_min FROM VLFCAPFINAL WHERE COSTCENTER = '{selected_costcenter}' GROUP BY COSTCENTER,current_week ORDER BY current_week,COSTCENTER"
    sum_b = ag.run_query(sum_b)
    fig = px.bar(sum_b, x='current_week', y='value_min')
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
     Input('workcenter-capacity-dropdown', 'value')]
)
def update_costcenter_table(selected_costcenter, selected_capgrp):#,df_json_pivot
    weeks_dict = create_weeks_dict()
    weeks_dict_for_query = create_weeks_for_query()
    # Default case
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'costcenter-dropdown':
        df_pivot = f"SELECT COSTCENTER,{weeks_dict_for_query} FROM VLFCAPFINALPIVOT WHERE COSTCENTER = '{selected_costcenter}' GROUP BY COSTCENTER ORDER BY COSTCENTER"
        sum_df = ag.run_query(df_pivot)
        sum_df_wc_cap_query = f"SELECT CAPWORK,{weeks_dict_for_query} FROM VLFCAPFINALPIVOT WHERE COSTCENTER = '{selected_costcenter}' GROUP BY CAPWORK ORDER BY CAPWORK"
        sum_df_wc_cap = ag.run_query(sum_df_wc_cap_query)
        sum_df_wc = ag.run_query(sum_df_wc_cap_query)
        iscapacity_control = 1

    elif button_id == 'workcenter-capacity-dropdown':
        df_pivot = f"SELECT COSTCENTER,{weeks_dict_for_query} FROM VLFCAPFINALPIVOT WHERE COSTCENTER = '{selected_costcenter}' GROUP BY COSTCENTER ORDER BY COSTCENTER"
        sum_df = ag.run_query(df_pivot)
        sum_df_wc_cap_query = f"SELECT CAPWORK,{weeks_dict_for_query} FROM VLFCAPFINALPIVOT WHERE CAPGRUP = '{selected_capgrp}' GROUP BY CAPWORK ORDER BY CAPWORK"
        sum_df_wc_cap = ag.run_query(sum_df_wc_cap_query)

        filtered_df_cap = f"SELECT CAPWORK,{weeks_dict_for_query} FROM VLFCAPFINALPIVOT WHERE CAPGRUP = '{selected_capgrp}' GROUP BY CAPWORK ORDER BY CAPWORK"
        sum_df_wc = ag.run_query(filtered_df_cap)
        iscapacity_control = 2

    sum_df['STAT'] = 'Kapasite İhtiyacı'
    weeks = list(weeks_dict.values())
    filtered_sum_df = sum_df[['STAT'] + weeks]
    work_center_sayisi = sum_df_wc_cap.shape[0]

    total_capacity = 5100 * work_center_sayisi
    first_week = list(weeks_dict.values())[0]

    data_for_new_row = {'STAT': 'Toplam Kapasite'}
    data_for_new_row.update({week: 0 if week == first_week else total_capacity for week in weeks_dict.values()})
    # Yeni satırı DataFrame'e ekle
    new_row = pd.DataFrame([data_for_new_row])

    cap_df = pd.concat([filtered_sum_df, new_row], ignore_index=True)

    result_row = {'STAT': 'Kapasite Farkı'}
    result_row.update(cap_df[list(weeks_dict.values())].iloc[1] - cap_df[list(weeks_dict.values())].iloc[0])

    # Append the result as a new row in the DataFrame
    cap_df = cap_df.append(result_row, ignore_index=True)

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
    for col in weeks_dict:
        # İlk kolon için özel durum: Eğer 'Toplam Kapasite' 0 ise, doluluk oranı da 0 olmalıdır
        if toplam_kapasite[col] == 0:
            doluluk_orani.append(0)
        else:
            # Doluluk oranını hesaplayın ve listeye ekleyin
            oran = (uretim_ihtiyaci[col] / toplam_kapasite[col]) * 100
            doluluk_orani.append(oran)

    # Doluluk oranlarını içeren yeni bir satır oluşturun
    doluluk_orani_satiri = pd.DataFrame([doluluk_orani], columns=weeks_dict)
    doluluk_orani_satiri['STAT'] = 'Doluluk Oranı'

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
    State('iscapacity_trigger', 'data')
)
def update_workcenter_table(selected_workcenter,selected_capgrp,selected_costcenter,isfirst,is_capasity,
                            table_name):
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    print(button_id)
    print("here5")
    weeks_dict_for_query = create_weeks_for_query()
    weeks_dict = create_weeks_dict()
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
             elif is_capasity == 2:
                 filtered_df_pivot_cap_list = f"SELECT * FROM {table_name}PIVOT WHERE CAPGRUP = '{selected_capgrp}'"
                 filtered_df_pivot_cap_list = ag.run_query(filtered_df_pivot_cap_list)
             print(filtered_df_pivot_cap_list)
             print("workhere2")
             unique_workcenters = filtered_df_pivot_cap_list["CAPWORK"].unique().tolist()
             print(unique_workcenters)
             print("workhere3")
             sorted_workcenters = sorted(unique_workcenters)
             first_element = sorted_workcenters[0] if sorted_workcenters else None
             filtered_df_pivot_cap = filtered_df_pivot_cap_list[filtered_df_pivot_cap_list['CAPWORK'] == first_element]
             filtered_df_pivot = filtered_df_pivot_cap_list.groupby(['MATERIAL'], as_index=False).sum()
             print(filtered_df_pivot)
             print("workhere4")
             sum_df_pivot = filtered_df_pivot_cap.groupby(['CAPWORK'], as_index=False).sum()

        elif button_id == 'workcenter-capacity-dropdown':
             filtered_df_pivot_cap_list = f"SELECT * FROM VLFCAPFINALPIVOT WHERE CAPGRUP = '{selected_capgrp}'"
             filtered_df_pivot_cap_list = ag.run_query(filtered_df_pivot_cap_list)
             print(filtered_df_pivot_cap_list)
             print("here2")
             unique_workcenters = filtered_df_pivot_cap_list["CAPWORK"].unique().tolist()
             print(unique_workcenters)
             print("here3")
             sorted_workcenters = sorted(unique_workcenters)
             first_element = sorted_workcenters[0] if sorted_workcenters else None
             filtered_df_pivot_cap = filtered_df_pivot_cap_list[filtered_df_pivot_cap_list['CAPWORK'] == first_element]
             filtered_df_pivot = filtered_df_pivot_cap_list.groupby(['MATERIAL'], as_index=False).sum()
             print(filtered_df_pivot)
             print("here4")
             sum_df_pivot = filtered_df_pivot_cap.groupby(['CAPGRUP'], as_index=False).sum()

    else:
        if button_id == 'workcenter-dropdown':
             filtered_df_pivot_cap = f"SELECT * FROM VLFCAPFINALPIVOT WHERE COSTCENTER = '{selected_costcenter}'"
             filtered_df_pivot_cap = ag.run_query(filtered_df_pivot_cap)
             filtered_df_pivot_cap = filtered_df_pivot_cap[filtered_df_pivot_cap['CAPWORK'] == selected_workcenter]
             filtered_df_pivot = filtered_df_pivot_cap[filtered_df_pivot_cap['CAPWORK'] == selected_workcenter]
             filtered_df_pivot = filtered_df_pivot.groupby(['MATERIAL'], as_index=False).sum()
             sum_df_pivot = filtered_df_pivot_cap.groupby(['CAPWORK'], as_index=False).sum()

        elif button_id == 'workcenter-capacity-dropdown':
             filtered_df_pivot_cap = f"SELECT * FROM VLFCAPFINALPIVOT WHERE CAPGRUP = '{selected_capgrp}'"
             filtered_df_pivot_cap = ag.run_query(filtered_df_pivot_cap)
             filtered_df_pivot = filtered_df_pivot_cap[filtered_df_pivot_cap['CAPGRUP'] == selected_capgrp]
             filtered_df_pivot = filtered_df_pivot.groupby(['MATERIAL'], as_index=False).sum()
             sum_df_pivot = filtered_df_pivot_cap.groupby(['CAPGRUP'], as_index=False).sum()


    sum_df_pivot['STAT'] = 'Kapasite İhtiyacı'
    weeks = list(weeks_dict.values())
    filtered_sum_df = sum_df_pivot[['STAT'] + weeks]

    if selected_workcenter == "Hepsi":
        if is_capasity == 1:
            filtered_df = f"SELECT * FROM VLFCAPFINAL WHERE COSTCENTER = '{selected_costcenter}'"
            filtered_df = ag.run_query(filtered_df)
            print(filtered_df)
            print("bur")
        elif is_capasity == 2:
            filtered_df = f"SELECT * FROM VLFCAPFINAL WHERE CAPGRUP = '{selected_capgrp}'"
            filtered_df = ag.run_query(filtered_df)
            print(filtered_df)
            print("bur2")

        unique_workcenters_df = filtered_df["CAPWORK"].unique().tolist()
        sorted_workcenters_df = sorted(unique_workcenters_df)
        first_element_df = sorted_workcenters_df[0] if sorted_workcenters_df else None
        filtered_df = filtered_df[filtered_df['CAPWORK'] == first_element_df]
    else:
        filtered_df = f"SELECT * FROM VLFCAPFINAL WHERE COSTCENTER = '{selected_costcenter}'"
        filtered_df = ag.run_query(filtered_df)
        filtered_df = filtered_df[filtered_df['CAPWORK'] == selected_workcenter]
    print(filtered_df)
    print(button_id)
    print(isfirst)
    print("but")
    if (button_id == 'workcenter-dropdown') | (isfirst == 0):
       print("den")
       sum_df = filtered_df.groupby(['CAPWORK', 'current_week']).sum({'value_min'}).reset_index()
       print(sum_df)
       print("bur4")
    elif button_id == 'workcenter-capacity-dropdown' :
       filtered_df = f"SELECT * FROM VLFCAPFINAL WHERE CAPGRUP = '{selected_capgrp}'"
       filtered_df = ag.run_query(filtered_df)
       sum_df = filtered_df.groupby(['CAPWORK', 'current_week']).sum({'value_min'}).reset_index()
    print(sum_df)
    print("bur3")
    figx = px.bar(sum_df, x='current_week', y='value_min')
    figx.update_xaxes(type='category')


    if (button_id == 'workcenter-dropdown') | (isfirst == 0):
       total_capacity = 5100
    elif button_id == 'workcenter-capacity-dropdown':
       sum_df_pivot = filtered_df_pivot_cap.groupby(['CAPWORK'], as_index=False).sum()
       work_center_sayisi = sum_df_pivot.shape[0]
       total_capacity = 5100 * work_center_sayisi

    first_week = list(weeks_dict.values())[0]
    data_for_new_row = {'STAT': 'Toplam Kapasite'}
    data_for_new_row.update({week: 0 if week == first_week else total_capacity for week in weeks_dict.values()})
    # Yeni satırı DataFrame'e ekle
    new_row = pd.DataFrame([data_for_new_row])
    cap_df = pd.concat([filtered_sum_df, new_row], ignore_index=True)
    result_row = {'STAT': 'Kapasite Farkı'}
    result_row.update(cap_df[list(weeks_dict.values())].iloc[1] - cap_df[list(weeks_dict.values())].iloc[0])

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
    for col in weeks_dict:
        # İlk kolon için özel durum: Eğer 'Toplam Kapasite' 0 ise, doluluk oranı da 0 olmalıdır
        if toplam_kapasite[col] == 0:
            doluluk_orani.append(0)
        else:
            # Doluluk oranını hesaplayın ve listeye ekleyin
            oran = (uretim_ihtiyaci[col] / toplam_kapasite[col]) * 100
            doluluk_orani.append(oran)

    # Doluluk oranlarını içeren yeni bir satır oluşturun
    doluluk_orani_satiri = pd.DataFrame([doluluk_orani], columns=weeks_dict)
    doluluk_orani_satiri['STAT'] = 'Doluluk Oranı'

    # Yeni satırı DataFrame'e ekleyin
    cap_df_prepared = pd.concat([cap_df, doluluk_orani_satiri], ignore_index=True)

    #column_definitions = [{'headerName': col, 'field': col, 'sortable': True, 'filter': True} for col in
     #                     filtered_df_pivot.columns]

    column_definitions = [{'headerName': 'MATERIAL', 'field': 'MATERIAL', 'sortable': True, 'filter': True}] + \
                         [{'headerName': week, 'field': date, 'sortable': True, 'filter': True} for week, date in
                          weeks_dict.items()]
    column_definitions_cap = [{'headerName': col, 'field': col, 'sortable': True, 'filter': True} for col in
                              cap_df_prepared.columns]
    return figx, filtered_df_pivot.to_dict('records'),column_definitions, cap_df_prepared.to_dict('records'),column_definitions_cap,isfirst + 1