
from datetime import datetime, timedelta, date
import pandas as pd
from run.agent import ag
from valfapp.app import oee

if datetime.today().weekday() == 6:
    kb = 2
elif datetime.today().weekday() == 0:
    kb = 3
else:
    kb = 1

a = oee(((date.today() - timedelta(days=kb)).isoformat(), (date.today() - timedelta(days=kb - 1)).isoformat(), "week"))

ccenters = ['CNC', 'TASLAMA', 'CNCTORNA', 'MONTAJ', 'PRESHANE1', 'PRESHANE2']

for month in range(1, 13):  # Months 1 to 12
    for day in range(1, 32):  # Days 1 to 31
        try:
            # Attempt to create a datetime object
            date = datetime.datetime('2024', month, day)
            print(date.strftime("%Y-%m-%d"))  # Print the date in YYYY-MM-DD format

            a = oee(((date.today() - timedelta(days=kb)).isoformat(), (date.today() - timedelta(days=kb - 1)).isoformat(), "week"))# bizim tarihler
            for ccenter in ccenters:
                ag.run_query(f"INSERT INTO VLFOEE ({date},{day},{ccenter},None,None,None,{a[0][ccenter]['OEE'][0]}")

            except ValueError:
            # Handle the case when the day is out of range for the month (e.g., February 30)
            pass

for index, row in a[1].iterrows():