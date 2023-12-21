from run.agent import ag
import pandas as pd

from run.agent import   ag

df = ag.run_query(r"SELECT TOP 5 MATERIAL,QUANTITY,INVDOCTYPE,CONFIRMATION FROM IASINVITEM")

df = df.groupby("MATERIAL").agg({"QUANTITY":"sum",
                                 "INVDOCTYPE":"max",
                                  "CONFIRMATION": lambda x : x*5 +3})

df.reset_index(inplace=True)


df["QUANTITY"] = df["QUANTITY"] * 10
