from run.agent import readtext
from run.agent import Agent
from config import set_df_size
from config import dirofquery

import argparse

set_df_size(None, None, None, None)

parser = argparse.ArgumentParser()
parser.add_argument("--charttype", help="Choose the chart type. g for gannchart "
                    " s fro scatter ", nargs="?", const="g")
parser.add_argument("--query", help="Please write query or give directory of text file of query.", nargs="?",
                    const=dirofquery)
parser.add_argument("--filename", help="Name of file which gonna be saved as html file.", nargs="?", const='chart1')
parser.add_argument('--columns', '--list', nargs='+', required=False,
                    help="Enter column names as parameters in charts in order"
                    "for gann chart (start time, finish time, axis y , timeblocks)"
                    "for scatter (xx, yy, widthofcirc, colorof, item)",
                    default=[])

args = parser.parse_args()
inputsofchart = args.columns
charttype = args.charttype

# checking if directory or string data entered correctly.

a = Agent(args.query)

listofcolumns = args.columns

readtext(args.query)

if args.filename:
    filename = args.filename + ".html"


if charttype == "g":
    a.draw_gannchart(saveorshow="save", xx_start=inputsofchart[0],
                     xx_end=inputsofchart[1], xy=inputsofchart[2], xcolor=inputsofchart[3], filename=filename)


elif charttype == "s":
    a.draw_bubblechart(saveorshow="save", xx=inputsofchart[0], yy=inputsofchart[1],
                       widthofcirc=inputsofchart[2], colorof=inputsofchart[3], item=inputsofchart[4], filename=filename)
