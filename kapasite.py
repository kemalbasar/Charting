from datetime import datetime,timedelta
import math
import dash
import dash_bootstrap_components as dbc
from dash import dcc
from run.agent import ag
import plotly.express as px



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
    print(df_sade)
    pivot_columns = df_sade.columns.difference(['MATERIAL','COSTCENTER','SURE_HESAPLAMA_KODU','MACHINE','LABOUR','SETUP','BASEQUAN'])

    # Pivot the data
    pivoted_df = df.melt(id_vars=['MATERIAL','COSTCENTER','SURE_HESAPLAMA_KODU','MACHINE','LABOUR','SETUP','BASEQUAN'], value_vars=pivot_columns, var_name='current_week', value_name='value')
    print(pivoted_df)
    pivoted_df["BASEQUAN"] = pivoted_df["BASEQUAN"].astype(int)
    pivoted_df["MACHINE"] = pivoted_df["MACHINE"].astype(float)
    pivoted_df["LABOUR"] = pivoted_df["LABOUR"].astype(float)
    pivoted_df["SETUP"] = pivoted_df["SETUP"].astype(float)
    pivoted_df["value"] = pivoted_df["value"].astype(float)
    pivoted_df['value_min'] = pivoted_df.apply(lambda row: calculate_maxtime(row), axis=1)
    pivoted_df['current_week'] = pivoted_df['current_week'].apply(
        lambda x: "1990-1" if x == 'IHT0' else x[4:].replace('_', '-'))
    pivoted_df['current_week'] = pivoted_df['current_week'].apply(
        lambda x: '-'.join([x.split('-')[0], x.split('-')[1].zfill(2)]) if len(x.split('-')) > 1 else x)

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
    formatted_weeks.insert(0, 'COSTCENTER')
    formatted_weeks.insert(0, 'SURE_HESAPLAMA_KODU')
    formatted_weeks.insert(0, 'MACHINE')
    formatted_weeks.insert(0, 'LABOUR')
    formatted_weeks.insert(0, 'SETUP')
    formatted_weeks.insert(0, 'BASEQUAN')

    return formatted_weeks

def calculate_maxtime(row):
    code = row['SURE_HESAPLAMA_KODU']
    machine = row['MACHINE']
    labour = row['LABOUR']
    setup = row['SETUP']
    total_need = row['value']
    base_quan = row['BASEQUAN']

    if total_need > 0:

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

    else:
        return 0

# Apply the function to each row in the DataFrame


a = pivotting_table()

sum_a = a.groupby('COSTCENTER').sum({'value_min'}).reset_index()

fig = px.bar(sum_a, x='COSTCENTER', y='value_min')

app.layout = dbc.Container([dcc.Graph(figure=fig)
])

if __name__ == '__main__':
    app.run_server(debug=True)
