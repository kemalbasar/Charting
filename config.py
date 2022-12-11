import pandas as pd

server = '******'
database = '*******'
username = '******'
password = '*******'

directory = r'C:\Users\kereviz\PycharmProjects\Charting\queries'
dirofquery = r'C:\Users\kereviz\PycharmProjects\Charting\queries\query2.txt'
dirofnewline = r'C:\Users\kereviz\PycharmProjects\Charting\queries\dateofstart.txt'
url_dyn = "**********************************************"

def set_df_size(maxrow, maxcolumn, maxwidth, maxcolwidth):
    pd.set_option('display.max_rows', maxrow)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 500)
    pd.set_option('display.max_colwidth', maxcolwidth)

