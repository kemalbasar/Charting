from run.agent import ag


df = ag.run_query( r"SELECT DISTINCT WORKCENTER FROM IASWORKCENT WHERE ISDELETE = 0 "
                r"AND WORKCENTER LIKE 'T-%' AND WORKCENTER NOT IN "
                r"(SELECT DISTINCT STEXT FROM VLFENRGY001) "
                r"ORDER BY WORKCENTER ")

wc_list = list(df["WORKCENTER"])

with open('insert_energy.sql', 'a') as file:
    for item in wc_list:
        file.write(f"INSERT INTO VLFENRGY001 values('{item}','valfsan_yuzeyislem_2',None,1,0.071,0)")
        file.write("\n")


