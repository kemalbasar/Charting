import dash
import dash_table
from dash import html
import pandas as pd

# Define the query to fetch data
query = """
SELECT CLIENT, COMPANY, MATERIAL, CONFDATE, QUANTITY, QTY, QUNIT, MATGRP2, MONTH, YEAR, CREATEDBY, CREATEDAT, CHANGEDBY, CHANGEDAT, COMPONENT, PPRICE, CURRENCY2, ROWBALANCE, CATEGORY, DOCNUM, DOCTYPE, SHCHANGEDATE, EURBALANCE
FROM VLFCOMPONENT
WHERE YEAR(CONFDATE) = YEAR(CURRENT_TIMESTAMP) AND MONTH(CONFDATE) = MONTH(CURRENT_TIMESTAMP)
"""

# Fetch the data using the provided method
data = ag.run_query(query)

# Load data into DataFrame
df = pd.DataFrame(data)

# Layout of the Dash app
layout = html.Div([
    html.H1("Costing Report"),
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        style_table={'height': '300px', 'overflowY': 'auto'},
        style_cell={'textAlign': 'left'},
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        page_size=20,  # we have pagination
        sort_action="native",  # enables data sorting
        filter_action="native",  # enables data filtering
        export_format="xlsx",  # export as Excel
        export_headers="display"
    )
])
