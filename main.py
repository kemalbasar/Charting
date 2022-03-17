from agent import Agent
from config import set_df_size
import argparse
import os

set_df_size(None, None, None, None)

parser = argparse.ArgumentParser()
parser.add_argument("query", help="Please write query or give directory of text file of query.")
parser.add_argument("filename", help="Name of file which gonna be saved as html file.")
parser.add_argument('--columns', '--list', nargs='+', required=False,
                    help="Enter column names for the GannChart in order"
                    " (start time, finish time, axis y , timeblocks)",
                    default=[])
args = parser.parse_args()

a = Agent()

#checking if directory or string data entered correctly.
query = args.query
if query[0:5] == 'SELECT':
    df = a.run_querry(query)
else:
    if os.path.exists(query):
        text = open(query, 'r')
        query = text.read()
        df = a.run_querry(query)
    else:
        raise Exception("Please enter correct directory or write SQL Query directly")

listofcolumns = args.columns
filename = args.filename + ".html"
a.draw_gannchart(data_source=df, saveorshow="save", xx_start="BEGINDAY",
                 xx_end="FINISHDAY", xy="WORKCENTER", xcolor="MATERIAL", filename=filename)

print(listofcolumns)
