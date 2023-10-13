from run.agent import ag
import pandas as pd
df_ilk = pd.read_excel(r"C:\Users\kbbudak\Desktop\SAYIM.xlsx",sheet_name='ILK')
df_son = pd.read_excel(r"C:\Users\kbbudak\Desktop\SAYIM.xlsx",sheet_name='SON')

df_ilk = df_ilk.groupby("Malzeme").agg({"Stok Miktarı":"sum"})
df_son = df_son.groupby("Malzeme").agg({"Stok Miktarı":"sum"})

df_ilk.reset_index(inplace=True)
df_son.reset_index(inplace=True)

df_ilk["Stok Miktarı"].sum()
df_son["Stok Miktarı"].sum()

df_final = df_ilk.merge(df_son,how="outer",on= "Malzeme")

df_final["Stok Miktarı_x"] = df_final["Stok Miktarı_x"].fillna(0)
df_final["Stok Miktarı_y"] = df_final["Stok Miktarı_y"].fillna(0)


df_final.to_excel(r"C:\Users\kbbudak\Desktop\SAYIM_final.xlsx")