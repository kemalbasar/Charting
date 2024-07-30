from config import project_directory
from run.agent import ag
from datetime import datetime, timedelta
import math
from dash_table.Format import Format, Scheme
import pandas as pd
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import pendulum

local_tz = pendulum.timezone("Asia/Istanbul")


dag = DAG(
    'sent_mail',
    schedule_interval='0 9 * * 2-6',  # Set your desired schedule interval
    start_date=datetime(2024, 4, 16, tzinfo=local_tz)
    ,  # Set the start date
    catchup=False  # Set to True if you want to backfill historical runs
)


def create_weeks_dict():

    start_date = datetime.now() - timedelta(weeks=1)

    # Önümüzdeki 18 hafta için yıl ve hafta numarasını içeren bir sözlük oluştur, hafta numarası iki basamaklı olacak şekilde
    weeks_dict = {}
    for i in range(19):  # Bu hafta dahil olmak üzere toplamda 19 hafta
        week_start = start_date + timedelta(weeks=i)
        year, week_num, _ = week_start.isocalendar()
        weeks_dict[f"{year}-{str(week_num).zfill(2)}"] = f"{year}-{str(week_num).zfill(2)}"

    return weeks_dict
def formatted_weeks_first():

    # Current date
    current_date = datetime.now()

    # Calculate the start of the current week (assuming weeks start on Monday)
    current_week_start = current_date - timedelta(days=current_date.weekday())

    # Generate the current week and the next 17 weeks
    weeks = [current_week_start + timedelta(weeks=i) for i in range(18)]  # Generating the weeks

    # Formatting weeks as 'Year_WeekNumber' using ISO week date
    # Adjusting to remove leading zeros and ensuring no week "00"
    formatted_weeks = [f"{week.strftime('%G')}_{int(week.strftime('%V'))}" for week in weeks]

    # Removing the first week if it is week 00 and prefixing with "IHT_"
    formatted_weeks = ["IHT_" + week for week in formatted_weeks if not week.endswith("_0")]

    formatted_weeks.insert(0, 'IHT0')
    formatted_weeks.insert(0, 'MATERIAL')
    formatted_weeks.insert(0, 'ANAMAMUL')
    formatted_weeks.insert(0, 'COSTCENTER')
    formatted_weeks.insert(0, 'CAPWORK')
    formatted_weeks.insert(0, 'WORKCUNT')
    formatted_weeks.insert(0, 'CAPGRUP')
    formatted_weeks.insert(0, 'STAND')

    formatted_weeks.insert(0, 'SURE_HESAPLAMA_KODU')
    formatted_weeks.insert(0, 'MACHINE')
    formatted_weeks.insert(0, 'LABOUR')
    formatted_weeks.insert(0, 'SETUP')
    formatted_weeks.insert(0, 'BASEQUAN')

    return formatted_weeks
def update_graph_method():
    print("first metod begin")
    print(datetime.now())
    weeks_first = formatted_weeks_first()

    # gerekli section değişikliği

    df1 = ag.run_query(
        r"SELECT ISNULL(W.CAPWORK,A.WORKCENTER) AS CAPWORK,ISNULL(T.WORKCUNT,1) AS WORKCUNT,A.CAPGRP AS CAPGRUP,C.STAND,A.* "
        r"FROM VLFPLATECAP A "
        r"LEFT JOIN (SELECT MAX(STAND) AS STAND,WORKCENTER FROM IASWORKCENT "
        r"WHERE COMPANY = '01' GROUP BY WORKCENTER) C ON A.WORKCENTER = C.WORKCENTER "
        r"LEFT JOIN (SELECT WORKCENTER AS CAPWORK,CAPGRP FROM IASCAPWRKCTR GROUP BY WORKCENTER,CAPGRP) W ON W.CAPGRP = A.CAPGRP "
        r"LEFT JOIN (SELECT COUNT(WORKCENTER) AS WORKCUNT,CAPGRP FROM (SELECT WORKCENTER,CAPGRP "
        r"FROM IASCAPWRKCTR GROUP BY WORKCENTER,CAPGRP) Q GROUP BY CAPGRP) T ON T.CAPGRP = A.CAPGRP "
        r"WHERE A.COSTCENTER != ''")
    df1 = df1[weeks_first]

    df2 = ag.run_query(
        r"SELECT ISNULL(W.CAPWORK,A.WORKCENTER) AS CAPWORK,ISNULL(T.WORKCUNT,1) AS WORKCUNT,A.CAPGRP AS CAPGRUP,"
        r"C.STAND,A.*"
        r"FROM VLFCHECKVALFCAP A "
        r"LEFT JOIN (SELECT MAX(STAND) AS STAND,WORKCENTER FROM IASWORKCENT "
        r"WHERE COMPANY = '01' GROUP BY WORKCENTER) C ON A.WORKCENTER = C.WORKCENTER "
        r"LEFT JOIN (	SELECT WORKCENTER AS CAPWORK,CAPGRP FROM IASCAPWRKCTR GROUP BY WORKCENTER,CAPGRP) W ON W.CAPGRP = A.CAPGRP "
        r"LEFT JOIN (SELECT COUNT(WORKCENTER) AS WORKCUNT,CAPGRP FROM (SELECT WORKCENTER,CAPGRP FROM IASCAPWRKCTR GROUP BY WORKCENTER,CAPGRP) Q "
        r"GROUP BY CAPGRP) T ON T.CAPGRP = A.CAPGRP WHERE A.WORKCENTER != 'SA' AND COSTCENTER != 'N/A'")
    df2 = df2[weeks_first]


    df3 = ag.run_query(f"{project_directory}\queries\prescapacity.sql")

    df3 = df3[weeks_first]
    df3.loc[df3['MATERIAL'] == 'YUZEY ISLEM-OTEC', 'COSTCENTER'] = 'YUZEY ISLEM-OTEC'
    df3.loc[df3['MATERIAL'] == 'YUZEY ISLEM-SANTRIFUJ', 'COSTCENTER'] = 'YUZEY ISLEM-SANTRIFUJ'
    df3.loc[df3['MATERIAL'] == 'YUZEY ISLEM-TAMBUR', 'COSTCENTER'] = 'YUZEY ISLEM-TAMBUR'
    df3.loc[df3['MATERIAL'] == 'YUZEY ISLEM-VIBRATOR', 'COSTCENTER'] = 'YUZEY ISLEM-VIBRATOR'
    df3['MATERIAL'] = df3['ANAMAMUL']

    df = pd.concat([df1, df2, df3], ignore_index=True)



    df['COSTCENTER'] = df['COSTCENTER'].replace({'CNCTORN2': 'CNCTORNA', 'CNCTORN3': 'CNCTORNA'})
    df['COSTCENTER'] = df['COSTCENTER'].replace('ELISI2', 'ELISI')
    df['COSTCENTER'] = df['COSTCENTER'].replace(
        {'ISOFINI2': 'ISOFINIS', 'ISOFINI3': 'ISOFINIS', 'ISOFINI4': 'ISOFINIS'})
    df['COSTCENTER'] = df['COSTCENTER'].replace('KALITEF2', 'KALITEF')
    df['COSTCENTER'] = df['COSTCENTER'].replace({'KURUTMA2': 'KURUTMA', 'KURUTMA3': 'KURUTMA', 'KURUTMA4': 'KURUTMA'})
    df.loc[df['CAPGRUP'] == 'FINAL TASLAMA', 'COSTCENTER'] = 'FINAL TASLAMA'
    df.loc[df['CAPGRUP'] == 'KABA TASLAMA', 'COSTCENTER'] = 'KABA TASLAMA'
    df.loc[df['STAND'] == 'PRESHANE1', 'COSTCENTER'] = 'PRESHANE1'
    df.loc[df['STAND'] == 'PRESHANE2', 'COSTCENTER'] = 'PRESHANE2'
    df.loc[df['MATERIAL'] == 'YUZEY ISLEM-OTEC', 'COSTCENTER'] = 'YUZEY ISLEM-OTEC'
    df.loc[df['MATERIAL'] == 'YUZEY ISLEM-SANTRIFUJ', 'COSTCENTER'] = 'YUZEY ISLEM-SANTRIFUJ'
    df.loc[df['MATERIAL'] == 'YUZEY ISLEM-TAMBUR', 'COSTCENTER'] = 'YUZEY ISLEM-TAMBUR'
    df.loc[df['MATERIAL'] == 'YUZEY ISLEM-VIBRATOR', 'COSTCENTER'] = 'YUZEY ISLEM-VIBRATOR'
    df.loc[df['MATERIAL'].str[:3] == 'DGR', 'COSTCENTER'] = 'DOGRULTMA'
    df.loc[df['MATERIAL'].str[:3] == 'STR', 'COSTCENTER'] = 'YUZEY ISLEM-SANTRIFUJ'
    df.loc[df['MATERIAL'].str[:3] == 'VBR', 'COSTCENTER'] = 'YUZEY ISLEM-VIBRATOR'
    df.loc[df['MATERIAL'].str[:3] == 'KTS', 'COSTCENTER'] = 'KABA TASLAMA'
    df.loc[df['MATERIAL'].str[:3] == 'FTS', 'COSTCENTER'] = 'FINAL TASLAMA'
    df.loc[df['CAPWORK'] == 'GKK', 'COSTCENTER'] = 'GKK'
    df.loc[df['COSTCENTER'] == 'KALITEF', 'COSTCENTER'] = 'FINAL-KONTROL'
    df.loc[df['COSTCENTER'] == 'PLKYZYIS', 'COSTCENTER'] = 'FLADDER'



    # def pivotting_table():
    #     today = datetime.today()
    #     one_week_ago = today - timedelta(days=7)
    #     year_ago, week_num_ago, week_day_ago = one_week_ago.isocalendar()
    #     formatted_date_one_week_ago = f"{year_ago}-{week_num_ago}"
    #
    #     df_sade = df[formatted_weeks()]
    #
    #     pivot_columns = df_sade.columns.difference(
    #         ['ANAMAMUL', 'MATERIAL', 'COSTCENTER', 'CAPWORK', 'SURE_HESAPLAMA_KODU', 'MACHINE', 'LABOUR', 'SETUP',
    #          'BASEQUAN', 'WORKCUNT', 'CAPGRUP'])
    #
    #     # Pivot the data
    #     pivoted_df = df.melt(
    #         id_vars=['ANAMAMUL', 'MATERIAL', 'COSTCENTER', 'CAPWORK', 'WORKCUNT', 'CAPGRUP', 'SURE_HESAPLAMA_KODU',
    #                  'MACHINE', 'LABOUR', 'SETUP',
    #                  'BASEQUAN'], value_vars=pivot_columns, var_name='current_week', value_name='value')
    #
    #     pivoted_df["BASEQUAN"] = pivoted_df["BASEQUAN"].astype(int)
    #     pivoted_df["MACHINE"] = pivoted_df["MACHINE"].astype(float)
    #     pivoted_df["LABOUR"] = pivoted_df["LABOUR"].astype(float)
    #     pivoted_df["SETUP"] = pivoted_df["SETUP"].astype(float)
    #     pivoted_df["value"] = pivoted_df["value"].astype(float)
    #     pivoted_df['value_min'] = pivoted_df.apply(lambda row: calculate_maxtime(row, row['WORKCUNT']), axis=1)
    #     pivoted_df['current_week'] = pivoted_df['current_week'].apply(
    #         lambda x: formatted_date_one_week_ago if x == 'IHT0' else x[4:].replace('_', '-'))
    #     pivoted_df['current_week'] = pivoted_df['current_week'].apply(
    #         lambda x: '-'.join([x.split('-')[0], x.split('-')[1].zfill(2)]) if len(x.split('-')) > 1 else x)
    #
    #     return pivoted_df

    # def formatted_weeks():
    #     # Current date
    #     current_date = datetime.now()
    #
    #     # Calculate the start of the current week (assuming weeks start on Monday)
    #     current_week_start = current_date - timedelta(days=current_date.weekday())
    #
    #     # Generate the current week and the next 17 weeks
    #     weeks = [current_week_start + timedelta(weeks=i) for i in range(18)]  # Generating the weeks
    #
    #     # Formatting weeks as 'Year_WeekNumber' using ISO week date
    #     # Adjusting to remove leading zeros and ensuring no week "00"
    #     formatted_weeks = [f"{week.strftime('%G')}_{int(week.strftime('%V'))}" for week in weeks]
    #
    #     # Removing the first week if it is week 00 and prefixing with "IHT_"
    #     formatted_weeks = ["IHT_" + week for week in formatted_weeks if not week.endswith("_0")]
    #
    #     formatted_weeks.insert(0, 'IHT0')
    #     formatted_weeks.insert(0, 'MATERIAL')
    #     formatted_weeks.insert(0, 'ANAMAMUL')
    #     formatted_weeks.insert(0, 'COSTCENTER')
    #     formatted_weeks.insert(0, 'CAPWORK')
    #     formatted_weeks.insert(0, 'CAPGRUP')
    #     formatted_weeks.insert(0, 'WORKCUNT')
    #     formatted_weeks.insert(0, 'SURE_HESAPLAMA_KODU')
    #     formatted_weeks.insert(0, 'MACHINE')
    #     formatted_weeks.insert(0, 'LABOUR')
    #     formatted_weeks.insert(0, 'SETUP')
    #     formatted_weeks.insert(0, 'BASEQUAN')
    #
    #     return formatted_weeks
    #
    # def calculate_maxtime(row, work_count):
    #     code = row['SURE_HESAPLAMA_KODU']
    #     machine = row['MACHINE']
    #     labour = row['LABOUR']
    #     setup = row['SETUP']
    #     total_need = row['value']
    #     base_quan = row['BASEQUAN']
    #
    #     if total_need > 0 and work_count > 0:  # work_count sıfır olmamalıdır, bölen sıfır olursa hata verir
    #         calculated_value = 0
    #         if code == 'A':
    #             calculated_value = machine + labour + setup
    #         elif code == 'B':
    #             calculated_value = (machine * total_need) + (labour * total_need) + setup
    #         elif code == 'C':
    #             calculated_value = (machine * total_need) + labour + setup
    #         elif code == 'D':
    #             calculated_value = machine + (labour * total_need) + setup
    #         elif code == 'E':
    #             calculated_value = math.ceil(total_need / base_quan) * machine + labour + setup
    #         elif code == 'F':
    #             calculated_value = machine + math.ceil(total_need / base_quan) * labour + setup
    #         elif code == 'G':
    #             calculated_value = math.ceil(total_need / base_quan) * (machine + labour) + setup
    #         elif code == 'H':
    #             calculated_value = math.ceil(total_need / base_quan) * machine + (labour * total_need) + setup
    #         elif code == 'I':
    #             calculated_value = (machine * total_need) + (labour * (total_need / base_quan)) + setup
    #         elif code == 'J':
    #             calculated_value = 0
    #
    #         return calculated_value / work_count  # Bölme işlemi burada yapılır
    #     else:
    #         return 0


    print(datetime.now())


    # Sonra, 'current_week' ve diğer tüm sütunlar için gruplandırma yaparak 'value_min' toplamını hesaplayın
    # df_grouped = df_prepared.groupby(
    #     ['MATERIAL', 'COSTCENTER', 'CAPWORK', 'SURE_HESAPLAMA_KODU', 'MACHINE', 'LABOUR', 'SETUP', 'BASEQUAN',
    #      'WORKCUNT', 'CAPGRUP',
    #      'current_week']).agg({'value_min': 'sum', 'ANAMAMUL': 'max'}).reset_index()



    # Son olarak, pivot işlemini gerçekleştirin
    # pivot_result = df_grouped.pivot(
    #     index=['ANAMAMUL', 'MATERIAL', 'COSTCENTER', 'CAPWORK', 'SURE_HESAPLAMA_KODU', 'MACHINE', 'LABOUR', 'SETUP',
    #            'BASEQUAN', 'WORKCUNT', 'CAPGRUP'],
    #     columns='current_week', values='value_min').reset_index()
    #

    def create_weeks_dict():
        start_date = datetime.now() - timedelta(weeks=1)

        # Önümüzdeki 18 hafta için yıl ve hafta numarasını içeren bir sözlük oluştur, hafta numarası iki basamaklı olacak şekilde
        weeks_dict = {}
        for i in range(19):  # Bu hafta dahil olmak üzere toplamda 19 hafta
            week_start = start_date + timedelta(weeks=i)
            year, week_num, _ = week_start.isocalendar()
            weeks_dict[f"{year}-{str(week_num).zfill(2)}"] = f"{year}-{str(week_num).zfill(2)}"

        return weeks_dict

    weeks_dict = create_weeks_dict()
    weeks_dict_cap = [{"name": key, "id": key} for key in weeks_dict.keys()]
    weeks_dict_cap.insert(0, {"name": "STAT", "id": "STAT"})

    formatted_columns_capcostcenter = []
    for column in weeks_dict_cap:
        if column["id"] == "STAT":
            formatted_columns_capcostcenter.append(column)
        else:
            formatted_columns_capcostcenter.append({
                **column,
                "type": "numeric",
                "format": Format(precision=0, scheme=Scheme.fixed)
            })

    columns_costcenter = [{"name": key, "id": key} for key in weeks_dict.keys()]
    columns_costcenter.insert(0, {"name": "COSTCENTER", "id": "COSTCENTER"})

    formatted_columns = []
    for column in columns_costcenter:
        if column["id"] == "COSTCENTER":  # COSTCENTER sütunu metinsel olabilir, formatlama uygulanmaz
            formatted_columns.append(column)
        else:
            formatted_columns.append({
                **column,
                "type": "numeric",
                "format": Format(precision=0, scheme=Scheme.fixed)
            })

    columns_workcenter = [{"name": key, "id": key} for key in weeks_dict.keys()]
    columns_workcenter.insert(0, {"name": "CAPWORK", "id": "CAPWORK"})

    formatted_columns_workcenter = []
    for column in columns_workcenter:
        if column["id"] == "CAPWORK":
            formatted_columns_workcenter.append(column)
        else:
            formatted_columns_workcenter.append({
                **column,
                "type": "numeric",
                "format": Format(precision=0, scheme=Scheme.fixed)
            })

    columns_material = [{"name": key, "id": key} for key in weeks_dict.keys()]
    columns_material.insert(0, {"name": "MATERIAL", "id": "MATERIAL"})

    formatted_columns_material = []
    for column in columns_material:
        if column["id"] == "MATERIAL":
            formatted_columns_material.append(column)
        else:
            formatted_columns_material.append({
                **column,
                "type": "numeric",
                "format": Format(precision=0, scheme=Scheme.fixed)
            })


    print("first metod end")
    print(datetime.now())
    return pivot_result


df,pivot_result = update_graph_method()




# ag.drop_table_if_exists("VLFCAPFINAL")
#
# ag.create_table_from_df(df, "VLFCAPFINAL")
#
# ag.insert_data_from_df(df, 'VLFCAPFINAL')



ag.drop_table_if_exists("VLFCAPFINALPIVOT")

ag.create_table_from_df(pivot_result, "VLFCAPFINALPIVOT")

ag.insert_data_from_df(pivot_result, 'VLFCAPFINALPIVOT')

#
#
# send_report_as_email_montaj = PythonOperator(
#     task_id='send_report_as_email_montaj',
#     python_callable=send_email_via_exchange,
#     provide_context=True,
#     dag=dag,
#     retries=5,  # Görev için maksimum deneme sayısı
#     retry_delay=timedelta(minutes=5),
#     op_args = ["kbbudak@valfsan.com.tr;tturali@valfsan.com.tr;montajhatti@valfsan.com.tr;odurmaz@valfsan.com.tr",'MONTAJ']
# )