import pandas as pd

server = '172.30.134.12'
database = 'VALFSAN604'
username = 'KEMAL'
password = '7412369kB'
directory = r'C:\Users\kbbudak\PycharmProjects\Charting\pictures'


def set_df_size(maxrow, maxcolumn, maxwidth, maxcolwidth):

    pd.set_option('display.max_rows', maxrow)
    pd.set_option('display.max_columns', maxcolumn)
    pd.set_option('display.width', maxwidth)
    pd.set_option('display.max_colwidth', maxcolwidth)
