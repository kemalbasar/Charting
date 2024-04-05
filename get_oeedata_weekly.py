from datetime import datetime,timedelta
from valfapp.app import oee


#a = oee(((date.today() - timedelta(days=kb)).isoformat(), (date.today() - timedelta(days=kb - 1)).isoformat(), "week"))

ccenters = ['CNC', 'TASLAMA', 'CNCTORNA', 'MONTAJ', 'PRESHANE1', 'PRESHANE2']


current_date = datetime.now().date()
current_date.weekday()
next_day = current_date - timedelta(days=current_date.weekday())
#günlük için aktif edilecek
#a = oee((next_day.isoformat(), current_date.isoformat(), "day"))
a = oee((current_date.isoformat(), next_day.isoformat(), "day"))

print('haft')
print(a)
for ccenter in ccenters:
    # SQL sorgusunu düzeltin
    with open('example2.txt', 'a') as file:
        success_rate = a[0][ccenter].loc[(a[0][ccenter].index == 'SESSIONTIME') & (a[0][ccenter]['OPR'] == 'SUCCES'), 'RATES'].sum()
        fail_rate = a[0][ccenter].loc[(a[0][ccenter].index == 'SESSIONTIME') & (a[0][ccenter]['OPR'] == 'FAIL'), 'RATES'].sum()

        if success_rate + fail_rate > 0:
            total_performance = success_rate / (success_rate + fail_rate)
            total_performance = round(total_performance, 2)
        else:
            total_performance = 0.0  # Toplam performans NaN ise, bunu 0.0 olarak ayarla


        if success_rate + fail_rate > 0:
            total_availability = (success_rate + fail_rate) / 100
            total_availability = round(total_availability, 2)
        else:
            total_availability = 0.0  # Toplam performans NaN ise, bunu 0.0 olarak ayarla


        if success_rate + fail_rate > 0:
            total_oee = a[0][ccenter]['OEE'][0]
            total_oee = round(total_oee, 2)
        else:
            total_oee = 0.0  # Toplam performans NaN ise, bunu 0.0 olarak ayarla


        sql = f"INSERT INTO VLFOEE (OEEDATE,PERIOD,COSTCENTER,WORKCENTER,PERSONAL,MATERIAL,OEE,PERFORMANCE,AVAILABILITY) VALUES ('{current_date.strftime('%Y-%m-%d')}', 'day', '{ccenter}', NULL, NULL, NULL, {total_oee},{total_performance},{total_availability})"
        file.write(sql)
        file.write("\n")


