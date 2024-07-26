import pandas as pd

"""passwords"""
project_directory = r"F:\pycarhm projects"

directory = project_directory + r'\Charting\queries'
dirofquery = project_directory + r'\Charting\queries\query2.txt'
dirofnewline = project_directory + r'\Charting\queries\dateofstart.txt'
url_dyn = "http://172.30.134.16:20000/services/btstarter.aspx?tran_code=WSCANIAS&tran_param=VLFPYPORTAL,"

def set_df_size(maxrow, maxcolumn, maxwidth, maxcolwidth):
    pd.set_option('display.max_rows', maxrow)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 500)
    pd.set_option('display.max_colwidth', maxcolwidth)
