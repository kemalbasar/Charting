from decimal import Decimal

import numpy as np
from dash import html, dcc
from dash import Input, Output, State, callback_context, \
    no_update,Patch    # pip install dash (version 2.0.0 or higher)
from dash.exceptions import PreventUpdate
import pandas as pd
from dash_ag_grid import AgGrid
from config import project_directory
from valfapp.app import app
from datetime import datetime
from dateutil.relativedelta import relativedelta
from run.agent import ag
from matgrp2dic import matgrp2dic
# Layout of the Dash app


defaultColDef = {
    "filter": True,
    "floatingFilter": True,
    "resizable": True,
    "sortable": True,
    "editable": True,
    "minWidth": 125,
}
def fix_table(df_sales,df_costing,iscomponent = 0):
    dataframes = {
        'price': df_sales,
        'cost': df_costing
    }
    # Merging DataFrames

    current_date = datetime.now()
    # Last three months by number
    last_three_months = [(current_date - relativedelta(months=i)).month for i in range(0, 3)]
    last_three_months.reverse()

    for df in dataframes:
        for item in last_three_months:
            dataframes[df].rename(columns={str(item): f'{df}_{item}'}, inplace=True)

    merged_df = pd.merge(df_costing,df_sales,on="MATGRP2", how="left")

    # Creating MultiLevel columns for the merged DataFrame
    # List comprehension to create lists with formatted strings
    price_columns = [(item, f"price_{item}") for item in last_three_months]
    sales_columns = [(item, f"sales_{item}") for item in last_three_months]

    # Concatenating the two lists

    if iscomponent == 1:
        combined_columns = ([('MATGRP2', 'Dönem')] +[('COMPONENT', 'Dönem')] +[('CATEGORY', 'Dönem')]
                            +[('PRICE', 'Dönem')] +[('QTY', 'Dönem')] + price_columns + sales_columns)
    else:
        combined_columns = ([('MATGRP2', 'Dönem')] + price_columns + sales_columns)

    merged_df.columns = pd.MultiIndex.from_tuples(combined_columns)

    def decimal_to_float(df):
        for column in df.columns:
            # Apply a function to check if any element in the column is a Decimal
            if any(df[column].apply(lambda x: isinstance(x, Decimal))):
                # Convert all Decimal to float, safely ignoring None values
                df[column] = df[column].apply(lambda x: int(x) if isinstance(x, Decimal) else x)
            if df[column].dtype == 'object':
                if column not in [('MATGRP2', 'Dönem'),('COMPONENT', 'Dönem'),
                                  ('CATEGORY', 'Dönem'),('PRICE', 'Dönem') , ('QTY', 'Dönem')]:
                    try:
                        df[column] = df[column].fillna(0).astype(int)
                    except ValueError:
                        # Log or handle the exception if needed, here we pass if conversion fails
                        pass
        return df

    merged_df = decimal_to_float(merged_df)

    for item in last_three_months:
        merged_df[(item, f'pay_{item}')] = ((merged_df[(item, f'price_{item}')] / merged_df[
            (item, f'sales_{item}')]) * 100).replace([np.inf, -np.inf], np.nan).fillna(0).astype(int)

    merged_df.columns = pd.MultiIndex.from_tuples(
        [(str(col[0]), col[1]) if col[1] else (col[0],) for col in merged_df.columns])
    merged_df = merged_df.sort_index(axis=1)


    if iscomponent == 1:
        combined_columns = (["MATGRP2"] +["COMPONENT"] +["CATEGORY"] +["PRICE"]
                            +["QTY"] + [str(item) for item in last_three_months])
    else:
        combined_columns = ["MATGRP2"] + [str(item) for item in last_three_months]

    merged_df = merged_df[combined_columns]

    for item in last_three_months:
        merged_df = merged_df.rename(
            columns={f'pay_{item}': 'Pay', f'price_{item}': 'Maliyet', f'sales_{item}': 'Ciro'})
    # merged_df.reindex(columns=['Ciro', 'Maliyet', 'Pay'], level='Dönem')

    def create_combined_trend_data(df):
        # Prepare a new column for the combined trend data
        trend_data = []
        for index, row in df.iterrows():
            data_points = []
            # Collect data from specified 'Pay' columns
            for col in ['3', '4', '5']:  # Adjust the numbers based on your column indices
                pay_col = (col, 'Pay')
                if pay_col in df.columns:
                    data_points.append(row[pay_col])
            trend_data.append(data_points)
        # Correctly assign the list to a new MultiIndex column
        df['Trend'] = trend_data
        return df

    merged_df = create_combined_trend_data(merged_df)
    merged_df['Back'] = merged_df[('MATGRP2' , 'Dönem')]
    merged_df.insert(1, 'Detay', 'Detay')


    def flatten_columns(df):
        """
        Flattens MultiIndex DataFrame columns into single-level columns by joining
        tuple names with an underscore. Also handles NaN values by converting them to None.
        """
        # Flattening the column headers
        df.columns = ['_'.join(map(str, col)).strip() for col in df.columns.values]

        # Converting NaN to None for JSON serialization
        df = df.where(pd.notnull(df), None)
        return df

    merged_df = flatten_columns(merged_df)

    return merged_df
def transform_multilevel_columns_to_aggrid_defs(df,buttons=1):
    """
    Transforms flattened DataFrame columns into a list of column definitions
    suitable for AG Grid in a Dash application, capturing all subheaders correctly.
    """
    column_defs = []
    seen_headers = set()

    for col in df.columns:
        if col in ('Trend_','Button_','Back_', 'Detay_'):
            continue
        header, sub_header = col.split('_', 1)
        if header not in seen_headers:
            seen_headers.add(header)
            # Collect all subheaders for each unique header
            children = [{'field': f'{header}_{sh.split("_", 1)[1]}', 'headerName': sh.split("_", 1)[1]} for sh in
                        df.columns if sh.startswith(header + '_')]
            column_defs.append({'headerName': header, 'children': children})

    column_defs.append({
        "headerName": "Trend",
        "field": "Trend",
        "cellRenderer": "sparklineCellRenderer",  # Match this name to your JS function
    })

    if buttons == 1:
        column_defs.insert(1,{
        "headerName": "Detay",
        "field": "Detay",
        "cellRenderer": "Button",
        "cellRendererParams": {"className": "btn btn-info"},
        "valueGetter": "window.agGridCustomFunctions.customValueGetter"
        })


        column_defs.insert(1,{
        "headerName": "Back",
        "field": "Back",
        "cellRenderer": "Button",
        "cellRendererParams": {"className": "btn btn-danger"},
        })


    return column_defs

layout = [
        # Stores the timestamp of the initial trigger
        dcc.Store(id='df-store'),
        dcc.Store(id='position' , data=0),
        dcc.Interval(
            id=f'check-interval_costing',
            interval=60 * 1000,  # Check every minute
            n_intervals=0
        ),
        dcc.Interval(
            id=f'interval-trigger_costing',
            interval=1000,  # 1 second
            n_intervals=0,
            max_intervals=1  # Trigger once initially
        ),
        html.Div( id = "costing_table" ),
        html.Div( id = "component_table" )]



@app.callback(
    Output(f'interval-trigger_costing', 'max_intervals'),
    Input(f'check-interval_costing', 'n_intervals'),
)
def check_elapsed_time(trigger_timestamp):
    if trigger_timestamp is None:
        # If there's no timestamp, it means the initial trigger hasn't happened yet
        raise PreventUpdate

    current_time = datetime.now().timestamp()
    elapsed_time = current_time - trigger_timestamp

    if elapsed_time >= 600:  # 600 seconds = 10 minutes
        return no_update  # Or set to a specific number if you want to limit future triggers

    raise PreventUpdate


@app.callback(
    [
        Output(f'costing_table', 'children'),
        # Output('df-store', 'data')
    ],
    [Input(f'interval-trigger_costing', 'n_intervals')]
)
def update_data_on_page_load(pathname):
    # If there's no specific action tied to pathname, you could check for it here
    # For now, we assume every load/refresh should trigger the data update

    print(f"***************!!!!!!! Maliyetlendirme Rapor Verileri Çekiliyor.***************!!!!!!!")

    df_sales  = ag.run_query(f"{project_directory}/Charting/queries/costing_queries/costing_month.sql")
    df_costing = ag.run_query(f"{project_directory}/Charting/queries/costing_queries/sales_month.sql")

    print( f"***************!!!!!!!End.!!!!!!!***************")

    print(f"***************!!!!!!! Maliyetlendirme Data Yapısı Oluşturuluyor .***************!!!!!!!")

    merged_df = fix_table(df_costing,df_sales,0)

    print( f"***************!!!!!!!End.!!!!!!!***************")

    print(f"***************!!!!!!! Maliyetlendirme Tablo Yapısı Oluşturuluyor .***************!!!!!!!")


    print(merged_df)

    return [html.Div([
    AgGrid(
        id='costing_rtable',
        rowData=merged_df.to_dict('records'),
        columnDefs=transform_multilevel_columns_to_aggrid_defs(merged_df),
        defaultColDef=defaultColDef,
        className="ag-theme-alpine-dark",
        columnSize="sizeToFit",
        )
    ])]
# Connect the Plotly graphs with Dash Components

@app.callback(
    Output("costing_rtable", "rowData"),
    Output("position", "data"),
    Output("df-store", "data"),
    Output(f'component_table', 'children'),
    Input("costing_rtable", "cellRendererData"),
    State("position", "data"),
    State('df-store', 'data')
)
def showChange(n,position,json_data):
    if n:
        row_id_sold = int(n['rowId'])
        print(row_id_sold)
        if n['colId'] == 'Detay':
            if position == 0:

                matgrp2dic[row_id_sold]

                df_sales = ag.editandrun_query(f"{project_directory}/Charting/queries/costing_queries/costing_month_material.sql", ['XXX'], [matgrp2dic[row_id_sold]])
                df_costing = ag.editandrun_query(f"{project_directory}/Charting/queries/costing_queries/sales_month_material.sql", ['XXX'], [matgrp2dic[row_id_sold]])

                merged_df = fix_table(df_costing,df_sales,0)



            elif position >= 1:


                merged_df = pd.read_json(json_data, orient='split')  # Deserialize JSON to DataFrame

                df_costing = ag.editandrun_query(f"{project_directory}/Charting/queries/costing_queries/costing_month_component.sql", ['XXX'], [merged_df.iloc[row_id_sold][0]])
                df_sales = ag.editandrun_query(f"{project_directory}/Charting/queries/costing_queries/sales_month_component.sql", ['XXX'], [merged_df.iloc[row_id_sold][0]])

                merged_df = fix_table(df_sales,df_costing,1)

                print("donus yapıyoruz problem burda")
                return  (merged_df.to_dict('records'),
                        ((position + 1 if position + 1 < 3 else 2) if n['colId'] == 'Detay' else (position - 1 if position - 1 > 0 else 0)),
                        merged_df.to_json(date_format='iso', orient='split'),[html.Div([
                        AgGrid(
                            id='component_rtable',
                            rowData=merged_df.to_dict('records'),
                            columnDefs=transform_multilevel_columns_to_aggrid_defs(merged_df,buttons=0),
                            defaultColDef=defaultColDef,
                            className="ag-theme-alpine-dark",
                            columnSize="sizeToFit",
                        )
                        ])])

            else:
                no_update
        else:
            if position == 0:

                return no_update

            elif position >= 1:

                print(f"***************!!!!!!! Maliyetlendirme Rapor Verileri Çekiliyor.***************!!!!!!!")

                df_sales = ag.run_query(f"{project_directory}/Charting/queries/costing_queries/costing_month.sql")
                df_costing = ag.run_query(f"{project_directory}/Charting/queries/costing_queries/sales_month.sql")

                print(f"***************!!!!!!!End.!!!!!!!***************")

                print(f"***************!!!!!!! Maliyetlendirme Data Yapısı Oluşturuluyor .***************!!!!!!!")

                merged_df = fix_table(df_costing, df_sales, 0)

                print(merged_df)

                print(f"***************!!!!!!!End.!!!!!!!***************")

                print(f"***************!!!!!!! Maliyetlendirme Tablo Yapısı Oluşturuluyor .***************!!!!!!!")

            else:
                no_update

        return (merged_df.to_dict('records'), (position + 1 if position + 1 < 3 else 2 ) if n['colId'] == 'Detay' else (position - 1 if position -1 > 0 else 0),
                merged_df.to_json(date_format='iso', orient='split'),no_update)

    else:

        return no_update
