import pandas as pd
from run.agent import  ag

df = ag.run_query(f"SELECT * FROM VLFPRDENERGYVİEW")
df["TOTWEIGHT"] = df["TOTWEIGHT"].fillna(0)
df["KWHPERTON"] = df.apply(lambda x : (x["TOTKWH"] / x["TOTWEIGHT"]) if x["TOTWEIGHT"] != 0 else 1.111,axis=1)
df["KWHPERTON"] = df["KWHPERTON"].round(3)
pivot_table = df.pivot_table(index="MATERIAL", columns='COSTCENTER', values='KWHPERTON', aggfunc='first')



print(pivot_table)
