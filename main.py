from agent import Agent
from config import set_df_size
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("")
set_df_size(None, None, None, None)

a = Agent()
query = "SELECT WORKCENTER,MATERIAL,BEGINDAY,FINISHDAY " \
        "FROM VLFPLANSOURCE WHERE PLANNEDDAY >'2022-04-01' AND PROCESS ='CFR'"

df = a.run_querry(query)


a.draw_gannchart(data_source=df, saveorshow="save", xx_start="BEGINDAY",
                 xx_end="FINISHDAY", xy="WORKCENTER", xcolor="MATERIAL", filename="bu.html")
