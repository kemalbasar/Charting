import warnings
from datetime import date, timedelta, datetime
import pandas as pd
from dash import Input, Output, State, callback_context, \
    no_update  # pip install dash (version 2.0.0 or higher)
from dash.exceptions import PreventUpdate
from run.agent import ag
from valfapp.app import app, prdconf
from valfapp.layouts import return_adr_layout, return_adr_callbacks, return_adr_timecallbacks
from config import kb

summary_color = 'black'

wc_usage = ag.run_query("SELECT STAND FROM IASROU009 WHERE STAND != '*'")


def apply_nat_replacer(x):
    x = str(x)
    if x == 'NaT':
        x = 'nat_replaced'
    else:
        x = x
    return x


new_line = '\n'
warnings.filterwarnings("ignore")
pd.set_option('display.float_format', lambda x: '%.2f' % x)
pd.set_option('display.width', 500)
pd.set_option('display.max_columns', None)


def calculate_interval_to_target_hour(target_hour):
    now = datetime.now()
    # Calculate the next occurrence of the target hour
    target = now.replace(hour=target_hour, minute=0, second=0, microsecond=0)
    if target < now:
        # If the target hour today is already past, move to the target hour tomorrow
        target += timedelta(days=1)
    # Calculate the interval in milliseconds
    interval_ms = (target - now).total_seconds() * 1000
    return interval_ms



layout = return_adr_layout('montaj',interval='week',position = '475px')

return_adr_timecallbacks('montaj',interval='week',position = '475px')

return_adr_callbacks('montaj',interval='week',position = '475px')

