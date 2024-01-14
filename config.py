import pandas as pd


directory = r'C:\Users\kbbudak\PycharmProjects\Charting\pictures'
dirofquery = r'C:\Users\kbbudak\PycharmProjects\Charting\queries\query2.txt'
dirofnewline = r'C:\Users\kbbudak\PycharmProjects\Charting\queries\dateofstart.txt'


def set_df_size(maxrow, maxcolumn, maxwidth, maxcolwidth):

    pd.set_option('display.max_rows', maxrow)
    pd.set_option('display.max_columns', maxcolumn)
    pd.set_option('display.width', maxwidth)
    pd.set_option('display.max_colwidth', maxcolwidth)
