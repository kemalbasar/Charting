layout = []

import numpy as np
import pandas as pd
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
from mysql.connector import connection

from run.agent import agiot as ag
from valfapp.app import app
from datetime import date, timedelta, datetime
from config import kb, project_directory
from dash_table import DataTable
from valfapp.functions.functions_prd import indicator_for_tvs
import statistics
from dash.dependencies import Input, Output



def generate_styles(data): #rapor kısmını referans değerlere göre renklendirme
    styles = []
    for index, row in data.iterrows():
        val = row['SANIYE_DENETLENEN']
        ref_val = row['MACHINETIME']
        diff = val - ref_val
        absdif=abs(diff)/10
        if diff > 0:
            if absdif <= 0.10:
                color = f'rgba(0, 255, 0, 0.10)'
            else: color = f'rgba(0, 255, 0, {min(1, abs(diff) / 10)})'
        else:
            if absdif <= 0.10:
                color = f'rgba(255, 0, 0, 0.10)'
            else: color = f'rgba(255, 0, 0, {min(1, abs(diff) / 10)})'
        styles.append({
            'if': {'row_index': index, 'column_id': 'SANIYE_DENETLENEN'},
            'backgroundColor': color
        })

        ppm_val = row['PPM']
        diff = ppm_val - 6000
        absdif = abs(diff) / 10
        if diff > 0:
            if absdif <= 0.10:
                color = f'rgba(255, 0, 0, 0.10)'
            else:
                color = f'rgba(255, 0, 0, {min(1, absdif/1000)})'
        else:
            if absdif <= 0.10:
                color = f'rgba(0, 255, 0, 0.10)'
            else:
                color = f'rgba(0, 255, 0, {min(1, absdif/1000)})'
        styles.append({
            'if': {'row_index': index, 'column_id': 'PPM'},
            'backgroundColor': color
        })

        durus_val = row['DURUS']
        if durus_val >= 400:
            color = f'rgba(255, 0, 0, 1)'
        elif durus_val >= 250:
            color = f'rgba(255, 0, 0, {min(1, durus_val / 1000)})'
        else:
            color = f'rgba(255, 0, 0, {max(0.10, durus_val / 1000)})'
        styles.append({
            'if': {'row_index': index, 'column_id': 'DURUS'},
            'backgroundColor': color
        })



    return styles




layout = [
    dcc.Store(id='filtered-data'),

    dbc.Row([html.H1("Günlük Üretim Raporu",
                     style={'text-align': 'center', "fontFamily": 'Arial Black',
                            'backgroundColor': 'rgba(33, 73, 180, 1)', 'color':'white'})]),
    dbc.Row(html.Div(children=[
        dcc.DatePickerRange(id='date-picker-range',
                             start_date=date.today() + timedelta(days=-kb),
                             end_date = date.today(),
                             persistence=True,
                             persistence_type='memory'
                             ),
        dbc.Button("Raporu İndir", id="btn-download-excel", color="primary", className="mr-1")

    ], style={'display': 'flex', 'flexDirection': 'row'})),



    dbc.Row([
        html.H2("Saniye Başına Denetlenen Adet", style={"text-align": "center", "color":"white",
                                                        'fontWeight':'bold',
                                                        "background-color":"rgba(33, 73, 180, 1)",
                                                        'margin-top':8}),
        dbc.Col([
            html.Div(id='indicator-figures-container',
                     style={'width': '1500%',
                            #'height': '100vh',
                            'display':'flex',
                            'justifyContent': 'center',
                            #'align-item':'center',
                            "background-color":"rgba(255, 250, 209, 1)"})
        ], width=1)
    ], style={'margin':'10'}),

    dbc.Row([
        dbc.Col([
            html.Div(id='indicator-figures-container2',
                     style={'width': '1500%',
                            #'height':'100vh',
                            #'align-item':'center',
                            'display': 'flex',
                            'padding-right':0,
                            'justifyContent': 'center',
                            "color":"white","background-color":"rgba(255, 250, 209, 1)"})
        ], width=1)
    ], style={'margin':'10'}),

    dbc.Row([
        dbc.Col([
            html.H2("Gantt Chart", style={"text-align": "center", "margin-top": 10,"color":"white",
                                                        'fontWeight':'bold',"background-color":"rgba(33, 73, 180, 1)"}),
            dcc.Graph(id="gantt_chart"),
        ], width=12),

        ], style={'margin': '10'}),

    dbc.Row([
        dbc.Col([
            html.H2("Rapor",style={"text-align":"center",'fontWeight':'bold',
                                   "color":"white",'margin-top':'8px',"background-color":"rgba(33, 73, 180, 1)"}),
            DataTable(
                id='uretim_data',
                columns=[],

                style_table={
                    'height' : '800',
                    'overflowY': 'auto',
                    'border': 'thin lightgrey solid',
                    'fontFamily': 'Arial, sans-serif',
                    'minWidth': '85%',  # Adjust this value to set the minimum width
                    'width': '100%',  # Adjust this value to set the width
                    'textAlign': 'left',
                    'color':'black',
                    'background-color':'white'

                    ##'margin': 'auto'  # Center the table horizontally

                },
                style_header={
                    'backgroundColor': 'rgba(0, 0, 0, 0)',  # Semi-transparent background
                    'fontWeight': 'bold',  # Bold font
                    'color': '#2F4F4F',  # Cool text color
                    'fontFamily': 'Arial, sans-serif',  # Font family
                    'fontSize': '14px',
                    'border': '1px solid  brown',
                    'borderRadius': '2px'
                    # Font size
                },

                style_data_conditional=[]


            ),
        ],width=15),

    ]),
    dcc.Download(id="download-excel"),
             ]

@app.callback(
    Output('uretim_data', 'columns'),
    Output("uretim_data", 'data'),
    Output('indicator-figures-container', 'children'),
    Output('indicator-figures-container2', 'children'),
    Output('uretim_data', 'style_data_conditional'),
    Input("date-picker-range", 'start_date'),
    Input("date-picker-range", 'end_date')
)
def update_summary_table(start_date, end_date):
    result_data = []
    fig_container = []
    fig_container2 = []

    counter = 0

    query_path = project_directory + r"\Charting\queries\vlf_ayıklamakmr_uretim.sql"
    text_to_find = ['XYZ', 'XXXX-XX-XX', 'YYYY-YY-YY']

    query_path2 = project_directory + r"\Charting\queries\vlf_ayıklamakmr_times.sql"
    text_to_find2 = ['XYZ', 'XXXX-XX-XX', 'YYYY-YY-YY']

    for x in range(1, 7):
        text_to_put = [f'KMR-0{x}', start_date, end_date]
        data = ag.editandrun_query(query_path, text_to_find, text_to_put)

        text_to_put2 = [f'KMR-0{x}', start_date, end_date]
        data2 = ag.editandrun_query(query_path2, text_to_find2, text_to_put2)

        data2["MATERIAL"] = data2["MATERIAL"].apply(lambda x: x.split('\x00', 1)[0])
        print(f"DATAAAAAAAAA");
        print(data);


        print(f"DATA222222222");
        print(data2);

        merged_data = pd.merge(data, data2, left_on=['PRDORDER', 'AYKDATE', 'SHIFTURETIM'],
                               right_on=['CONFIRMATION', 'MACHINEDATE', 'SHIFTAYK'], how='inner')

        merged_data = merged_data.sort_values(by=['MACHINE', 'MIN_WORKSTART'])

        print(f"MERGED DATA ÖNCESİİİİİİ:");
        print(merged_data);

        merged_data["MIN_WORKSTART"] = pd.to_datetime(merged_data["MIN_WORKSTART"]).dt.strftime('%Y-%m-%d %H:%M:%S')
        merged_data["MAX_WORKEND"] = pd.to_datetime(merged_data["MAX_WORKEND"]).dt.strftime('%Y-%m-%d %H:%M:%S')

        result_data.append(merged_data)

        print(f"MERGED DATA SONRASIIIIII");
        print(merged_data);


    final_result = pd.concat(result_data, ignore_index=True)

    print(final_result)
    print(type(final_result))
    print('zzzzzzzzzz')


    table_data = final_result.groupby(['MACHINE', 'SHIFTAYK', 'NAME', 'PRDORDER', 'MATERIAL_x']).agg(
        {'MIN_WORKSTART': 'min', 'MAX_WORKEND': 'max' ,'QUANTITY': 'first', 'NOTOK': 'first',
         'CALISIYOR': 'sum',
         'DURUS': 'sum', 'SANIYE_DENETLENEN': 'first', 'MACHINETIME': 'first', 'PPM': 'first'})

    print(f"TABLEE DATA:AAAAAAAAAAA");
    print(table_data);

    styles = generate_styles(table_data)

    oee_data = final_result.groupby(['MACHINE' , 'MATERIAL_x', 'PRDORDER']).agg(
        {'QUANTITY': 'sum', 'MACHINETIME': 'first', 'CALISIYOR': 'sum', 'NOTOK': 'sum', 'PPM': 'first', 'SANIYE_DENETLENEN': 'first'})

    oee_data['OEE'] = '0'
    oee_data['PPM'] = '0'



    print(oee_data)

    print(oee_data.dtypes)

    oee_data['OEE'] = oee_data['OEE'].astype(int)
    oee_data['QUANTITY'] = oee_data['QUANTITY'].astype(int)
    oee_data['CALISIYOR'] = oee_data['CALISIYOR'].astype(int)
    oee_data['MACHINETIME'] = oee_data['MACHINETIME'].astype(float)
    oee_data['NOTOK'] = oee_data['NOTOK'].astype(int)
    oee_data['PPM'] = oee_data['PPM'].astype(int)

    print(oee_data.dtypes)

    oee_data['OEE'] = ((oee_data['QUANTITY'] / ((oee_data['CALISIYOR'] * 1000) / oee_data['MACHINETIME'])) * (
            oee_data['CALISIYOR'] / 1440)) * oee_data['QUANTITY']

    oee_data['PPM'] = ((oee_data['NOTOK'] * 1000000) / oee_data['QUANTITY'])

    print(oee_data)



    print(oee_data)
    print(f"OEE DATA")

    denominator = table_data['CALISIYOR']
    denominator_nonzero = denominator.replace(0, np.nan)
    table_data['SANIYE_DENETLENEN'] = np.where(denominator_nonzero.isna(), 0, (table_data['QUANTITY'] + table_data['NOTOK']) / denominator_nonzero / 60)

    ##table_data['SANIYE_DENETLENEN'] = (table_data['QUANTITY'] + table_data['NOTOK']) / (table_data['CALISIYOR']) / 60


    table_data['MACHINETIME'] = ((1000/ table_data['MACHINETIME'])/60)

    table_data = table_data.sort_values(by=['MACHINE', 'MIN_WORKSTART'])



    table_data['SANIYE_DENETLENEN'] = table_data['SANIYE_DENETLENEN'].astype(float)
    table_data['SANIYE_DENETLENEN'] = table_data['SANIYE_DENETLENEN'].round(3)
    table_data['MACHINETIME'] = table_data['MACHINETIME'].astype(float)
    table_data['MACHINETIME'] = table_data['MACHINETIME'].round(3)

    ##table_data['SANIYE_DENETLENEN'] = round(table_data['SANIYE_DENETLENEN'], 3)

    table_data = table_data.reset_index()

    table_data['MIN_WORKSTART'] = pd.to_datetime(table_data['MIN_WORKSTART']).dt.strftime('%Y-%m-%d %H:%M:%S')


    machine_data = oee_data.groupby(['MACHINE']).agg(
        {'QUANTITY': 'sum', 'OEE': 'sum', 'PPM': 'first'})

    avg_mtime=table_data.groupby(['MACHINE']).agg({'MACHINETIME':'mean'})
    print('+++++++++-----------------')
    print(avg_mtime)

    print('+++++++++-----------------')
    avg_sn=table_data.groupby(['MACHINE']).agg({'SANIYE_DENETLENEN':'mean'})
    print('+++++++++-----------------')
    print(avg_sn)
    print('+++++++++-----------------')

    merged_df2=pd.merge(avg_mtime, avg_sn, on='MACHINE')
    merged_df3=pd.merge(merged_df2, machine_data, on='MACHINE')
    print(merged_df2)
    print('xxxxxxxxxxxxxxxxxxxxxxx')
    print(merged_df3)
    print('xxxxxxxxxxxxxxxxxxxxxxx')


    merged_df3['SANIYE_DENETLENEN'] = merged_df3['SANIYE_DENETLENEN'].astype(float)
    merged_df3['SANIYE_DENETLENEN'] = merged_df3['SANIYE_DENETLENEN'].round(3)
    merged_df3['MACHINETIME'] = merged_df3['MACHINETIME'].astype(float)
    merged_df3['MACHINETIME'] = merged_df3['MACHINETIME'].round(3)






    print(f"MACHINE DATAM :BBBBBBBBBBBBB");
    print(machine_data);


    for machine_index, indicator_data in merged_df3.iterrows():
        print(indicator_data)
        print(machine_index)
        print('eeeeeeeeeeeee')
        print(machine_data)
        print('eeeeeeeeeeeee')
        print(type(machine_index))
        print(type(indicator_data))
        print(type(avg_sn))
        print('++++++++++++++++++++++++')
        print('xxxxxxxxxxxxxxxxxxxxxxx')
        print(merged_df3)
        print('xxxxxxxxxxxttttttxxxxxxxxxxxx')
        print(indicator_data['PPM'])
        print(indicator_data['OEE'])
        print((indicator_data['OEE'] / indicator_data['QUANTITY']) * 100)
        counter += 1

        if counter <=3:


            fig2 = go.Figure()
            fig2.add_trace(go.Indicator(
                value= (indicator_data['OEE'] / indicator_data['QUANTITY']) * 100,
                title={'text': f'{machine_index}','font': {'color': 'darkgreen', 'size': 20}},
                delta={'reference': 80},
                gauge={
                    'axis': {'visible': False},
                    'bordercolor': 'darkgreen',
                    'bar': {'thickness': 1, 'color': 'green'}
                },
                number={'font': {'color': 'darkgreen'}}
                ,)
                )

            fig2.add_trace(go.Indicator(
                value=indicator_data['PPM'],
                title={'text': "PPM",'font': {'color':'darkgreen','size': 20}},
                gauge={
                    'shape': "bullet",
                    'axis': {'visible': False},
                    'bar': {'thickness': 1, 'color':'green'},
                    'bordercolor':'darkgreen'
                },
                domain={'x': [0.10, 0.45], 'y': [0.39, 0.49]},

                number={'font': {'size': 20, 'color':'darkgreen'}})
            )
            print('ccccccccccccccccc')
            print(type(indicator_data['OEE']))
            print('ccccccccccccccccc')
            fig2.add_trace(go.Indicator(
                value=indicator_data['MACHINETIME'],
                mode="number",
                title={'text': "Tanımlı Süre", 'font': {'color': 'darkgreen', 'size': 18}},
                domain={'x': [0.50, 0.75], 'y': [0.39, 0.49]},
                number={'font': {'size': 18, 'color': 'darkgreen'}}

            ))

            fig2.add_trace(go.Indicator(
                value=indicator_data['SANIYE_DENETLENEN'],
                mode="number",
                title={'text': "Adet/Saniye", 'font': {'color': 'darkgreen', 'size': 18}},
                domain={'x': [0.50, 0.75], 'y': [0.39, 0.39]},
                number={'font': {'size': 18, 'color': 'darkgreen'}}
            ))


            fig2.update_layout(
                plot_bgcolor='rgba(255, 250, 209, 1)',
                grid={'rows': 2, 'columns': 2, 'pattern': "independent"},
                template={'data': {'indicator': [{
                    'mode': "number+delta+gauge",
                    'delta': {'reference': 5000}}]
                }}, height=300,
                #responsive=True,
                width=550,
                paper_bgcolor='rgba(255, 250, 209, 1)',
                margin=dict(l=5, r=10, t=55, b=15)
                ##margin=dict(l=55, r=75, t=55, b=15)  # Adjust margin values to decrease distance

            )

            fig_container.append(dcc.Graph(figure=fig2, id=f'indicator-figures-container',className='main-svg',
                                           style={'padding-right':'0%','margin-right':'0%','max-width':'1500%','padding':'30px',
                                                  'min-width':'20%'}
                                 ))



        else:

            fig3 = go.Figure()
            fig3.add_trace(go.Indicator(
                value= (indicator_data['OEE'] / indicator_data['QUANTITY']) * 100,
                title={'text': f'{machine_index}','font': {'color': 'darkgreen', 'size': 20}},
                delta={'reference': 80, 'font':{'color':'darkgreen'}},
                gauge={
                    'axis': {'visible': False},
                    'bar': {'thickness': 1, 'color':'green'},
                    'bordercolor':'darkgreen'
                },
                number={'font': {'color': 'darkgreen'}})
            )

            fig3.add_trace(go.Indicator(
                value=indicator_data['PPM'],
                title={'text': "PPM",'font': {'color':'darkgreen','size': 20}},
                gauge={
                    'shape': "bullet",
                    'axis': {'visible': False},
                    'bar': {'thickness': 1, 'color':'green'},
                    'bordercolor':'darkgreen'
                },
                domain={'x': [0.10, 0.45], 'y': [0.39, 0.49]},
                number={'font': {'size': 20, 'color':'darkgreen'}})
            )
            fig3.add_trace(go.Indicator(
                value=indicator_data['MACHINETIME'],
                mode="number",
                title={'text': "Tanımlı Süre", 'font': {'color': 'darkgreen', 'size': 18}},
                domain={'x': [0.50, 0.75], 'y': [0.39, 0.49]},
                number={'font': {'size': 18, 'color': 'darkgreen'}}
            ))

            fig3.add_trace(go.Indicator(
                value=indicator_data['SANIYE_DENETLENEN'],
                mode="number",
                title={'text': "Adet/Saniye", 'font': {'color': 'darkgreen', 'size': 18,}},
                domain={'x': [0.50, 0.75], 'y': [0.39, 0.39]},
                number={'font': {'size': 18, 'color': 'darkgreen'}}
            ))


            fig3.update_layout(
                grid={'rows': 2, 'columns': 2, 'pattern': "independent"},
                template={'data': {'indicator': [{
                    'mode': "number+delta+gauge",
                    'delta': {'reference': 5000}}]
                }}, height=300
                ,
                plot_bgcolor='rgba(255, 250, 209, 1)',
                paper_bgcolor='rgba(255, 250, 209, 1)',
                width=550,
                margin=dict(l=5, r=10, t=55, b=15)
                ##margin=dict(l=55, r=75, t=55, b=15)  # Adjust margin values to decrease distance

            )

            fig_container2.append(dcc.Graph(figure=fig3, id=f'indicator-figures-container2',
                                            style={'padding-right':'0%','margin-right':'0%','max-width':'60%','padding':'30px',
                                                   'min-width': '20%'
                                                   }))



    columns = [{"name": i, "id": i} for i in table_data.columns]
    styles = generate_styles(table_data)

    return columns, table_data.to_dict("records"), fig_container , fig_container2, styles

@app.callback(
    Output("download-excel", "data"),
    Input("btn-download-excel", "n_clicks"),
    State("uretim_data", "data"),
    prevent_initial_call=True,
)
def download_as_excel(n_clicks, table_data):

    df = pd.DataFrame(table_data)
    return dcc.send_data_frame(df.to_excel, "uretim_raporu.xlsx", sheet_name="Kamera Ayıklama Raporu", index=False)
  
@app.callback(
    Output("gantt_chart", "figure"),
    Input("uretim_data", 'data'),
    Input("date-picker-range", 'start_date'),
    Input("date-picker-range", 'end_date'),
    )

def draw_gann_chart(data, start_date, end_date):

    data3 = ag.editandrun_query(project_directory + r"\Charting\queries\vlf_ayıklamakmr_timesforgantt.sql",

                               texttofind = ['XXXX-XX-XX','YYYY-YY-YY'],texttoput = [start_date,end_date])

    data3["MIN_WORKSTART"] = pd.to_datetime(data3["MIN_WORKSTART"]).dt.strftime('%Y-%m-%d %H:%M:%S')

    data3["MAX_WORKEND"] = pd.to_datetime(data3["MAX_WORKEND"]).dt.strftime('%Y-%m-%d %H:%M:%S')

    fig = go.Figure()

    fig = px.timeline(data_frame=data3[["MIN_WORKSTART", "MAX_WORKEND", "MACHINEAYK","TYPE"]],
                   x_start="MIN_WORKSTART",
                   x_end="MAX_WORKEND",
                   y='MACHINEAYK', color="TYPE",
                   color_discrete_map={"CALISIYOR": "forestgreen" , "BEKLEME DURUSU" : "red" , "MALZEME DURUSU" : "brown"})





    return fig


