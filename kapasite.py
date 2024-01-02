from datetime import datetime,timedelta
import math
import os
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
from config import project_directory, kb
import plotly.express as px  # (version 4.7.0 or higher)


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







df = ag.run_query(r"SELECT * FROM VLFPLATECAP")


def pivotting_table():
    df_sade = df[formatted_weeks()]
    pivot_columns = df_sade.columns.difference(['MATERIAL'])

    # Pivot the data
    pivoted_df = df.melt(id_vars='MATERIAL', value_vars=pivot_columns, var_name='current_week', value_name='value')

    return pivoted_df




def formatted_weeks():
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
    return formatted_weeks

def calculate_maxtime(row):
    code = row['TUMACIKSIPARIS_SURE_HESAPLAMA_KODU']
    machine = row['TUMACIKSIPARIS_MACHINE']
    labour = row['TUMACIKSIPARIS_LABOUR']
    setup = row['TUMACIKSIPARIS_SETUP']
    total_need = row['TUMACIKSIPARIS_TOTALIHTIYAC']
    base_quan = row['TUMACIKSIPARIS_BASEQUAN']

    if code == 'A':
        return machine + labour + setup
    elif code == 'B':
        return (machine * total_need) + (labour * total_need) + setup
    elif code == 'C':
        return (machine * total_need) + labour + setup
    elif code == 'D':
        return machine + (labour * total_need) + setup
    elif code == 'E':
        return math.ceil(total_need / base_quan) * machine + labour + setup
    elif code == 'F':
        return machine + math.ceil(total_need / base_quan) * labour + setup
    elif code == 'G':
        return math.ceil(total_need / base_quan) * (machine + labour) + setup
    elif code == 'H':
        return math.ceil(total_need / base_quan) * machine + (labour * total_need) + setup
    elif code == 'I':
        return (machine * total_need) + (labour * (total_need / base_quan)) + setup
    elif code == 'J':
        return 0

# Apply the function to each row in the DataFrame
df['TUMACIKSIPARIS_MAXTIME'] = df.apply(lambda row: calculate_maxtime(row), axis=1)

app.layout = dbc.Container([



])