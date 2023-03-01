import pandas as pd

server = '172.30.134.12'
database = 'VALFSAN604'
username = 'kemal'
password = 'casewhen123..,,'

directory = r'C:\Users\kereviz\PycharmProjects\Charting\queries'
dirofquery = r'C:\Users\kereviz\PycharmProjects\Charting\queries\query2.txt'
dirofnewline = r'C:\Users\kereviz\PycharmProjects\Charting\queries\dateofstart.txt'
url_dyn = "http://172.30.134.16:20000/services/btstarter.aspx?tran_code=WSCANIAS&tran_param=VLFPYPORTAL,"

def set_df_size(maxrow, maxcolumn, maxwidth, maxcolwidth):
    pd.set_option('display.max_rows', maxrow)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 500)
    pd.set_option('display.max_colwidth', maxcolwidth)
