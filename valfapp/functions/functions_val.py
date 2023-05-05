from config import project_directory
from run.agent import ag
import pandas as pd
import datetime as dt
import numpy as np
import warnings

warnings.filterwarnings("ignore")

pd.set_option('display.float_format', lambda x: '%.2f' % x)
pd.set_option('display.width', 500)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)

df_val = ag.run_query(project_directory + r"\Charting\queries\valuation.sql")
df_val["QUANTITY"] = df_val["QUANTITY"].astype(float)
df_val["PRICE"] =  df_val["PRICE"].astype(float)
df_histval = ag.run_query(r"SELECT * FROM VLFTOTALVALUE")

df_val["TOTVAL"] = [df_val["PRICE"][row] * df_val["QUANTITY"][row] * 0.7 if df_val["ACIKLAMA"][row] == "MAMÜL"
                    else df_val["PRICE"][row] * df_val["QUANTITY"][row] for row in range(len(df_val))]
total_value = df_val["TOTVAL"].sum()
materials = df_val["MATERIAL"].nunique()

df_raw_material = df_val.loc[df_val["ACIKLAMA"] == "HAMMADDE", ["ACIKLAMA", "PARCA", "TOTVAL"]]
df_raw_material.rename(columns={"PARCA": "GRUBU"}, inplace=True)
df_val = df_val.loc[df_val["ACIKLAMA"] != "HAMMADDE", ["ACIKLAMA", "GRUBU", "TOTVAL"]]
df_val = df_val.append(df_raw_material)
df_val = df_val.groupby(["ACIKLAMA", "GRUBU"]).agg({"TOTVAL": "sum"})
df_val.reset_index(inplace=True)
df_val = df_val.loc[((df_val["ACIKLAMA"] != '') & (df_val["GRUBU"] != '*') & (df_val["GRUBU"] != ''))]
df_val.to_excel(project_directory + r"\Charting\outputs(xlsx)\val2022.xlsx")
del df_raw_material

df_histstocks = ag.run_query(r"SELECT * FROM VLFHISTORICALSTOCKS WHERE ACIKLAMA = 'MAMÜL' AND SKUNIT = 'AD'")
