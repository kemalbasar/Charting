from agent import Agent
from config import set_df_size

set_df_size(None, None, None, None)

a = Agent()
query = "SELECT WORKCENTER,MATERIAL,BEGINDAY,FINISHDAY FROM VLFPLANSOURCE WHERE PLANNEDDAY >'2022-04-01' AND PROCESS ='CFR'"
df = a.run_querry(query)
a.draw_gannchart(df,"BEGINDAY","FINISHDAY","WORKCENTER","MATERIAL")
