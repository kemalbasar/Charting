import pandas as pd
from datetime import datetime

server = '172.30.134.12'
database = 'VALFSAN604'
database_iot = 'VALFAN_IOT_001'
username = 'Fatih'
password = '123456fO.'

reengen_username = "takgun@valfsan.com.tr"
reengen_password = '1234Ta1234'
reengen_company = 'valfsan'


project_directory = r"C:\Users\fozturk\Documents\GitHub"

directory = project_directory + r'\Charting\queries'
dirofquery = project_directory + r'\Charting\queries\query2.txt'
dirofnewline = project_directory + r'\Charting\queries\dateofstart.txt'
url_dyn = "http://172.30.134.16:20000/services/btstarter.aspx?tran_code=WSCANIAS&tran_param=VLFPYPORTAL,"

today = datetime.today()

if today.weekday() == 6:
    kb = 2
elif today.weekday() == 0:
    kb = 3
else:
    kb = 1

def set_df_size(maxrow, maxcolumn, maxwidth, maxcolwidth):
    pd.set_option('display.max_rows', maxrow)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 500)
    pd.set_option('display.max_colwidth', maxcolwidth)

valftoreeg = {"Bütün":{"Analizörler":"Analizörler","Bölümler":"Bölümler"},
              "CNC":{'CNC - Pano 1': 'CNC - Pano 1',
                    'CNC - Pano 2': 'CNC - Pano 2',
                    'CNC - Pano 3': 'CNC - Pano 3',
                    "CNC-07" : "valfsan_cncfreze_makina_cnc_07",
                    "CNC-04" : "valfsan_cncfreze_trident_cnc_04",
                    "CNC-20" : "valfsan_cncfreze_dmc_cnc_20",
                    "CNC-12"  : 'valfsan_cnctorna_starcnc_kayarotomat_cnc_12',
                    "CNC-24" : 'valfsan_cncfreze_johnford_cnc_24' ,
                    "CNC-03" :  'valfsan_cncfreze_haas_cnc_03',
                    "CNCTO-07" : 'valfsan_cnctorna_dmc_cnc_to_07',
                    "CNCTO-15" : 'valfsan_cnctorna_dmgmori_cnc_to_15' ,
                    "CNCTO-09" : 'valfsan_cnctorna_spinner_cnc_to_09' },
                "ISIL ISLEM " : {"F-01" : 'valfsan_isilislem_cinfirini',
                    "F-02" : "valfsan_isilislem_hintfirini",
                    "F-03" : "valfsan_isilislem_bakirkaynakfirini",
                    "MF-01" : "valfsan_isilislem_menevisfirini_mf_01",
                    "MF-04" : "valfsan_isilislem_menevisfirini_mf_04"},
              "DOGRULTMA": { "DM-02" : "valfsan_dogrultma_dm_02"},
              "TASLAMA": {  "DD-02":"valfsan_taslama_dd_02",
                    "DD-03": "valfsan_taslama_dd_03",
                    "DD-04": "valfsan_taslama_dd_04",
                    "DD-05": "valfsan_taslama_dd_05",
                    "DD-06": "valfsan_taslama_dd_06",
                    "DD-07": "valfsan_taslama_dd_07",
                    "DD-10": "valfsan_taslama_discus_dd_10",
                    "CT-03": "valfsan_taslama_ct_03",
                    "STAG-01": "valfsan_taslama_stag_01",
                    "STAG-02": "valfsan_taslama_stag_02",
                    "STAG-03": "valfsan_taslama_stag_03"},
              "PRESHANE": {'PRES - Pano 1': 'PRESHANE / PANO 1',
                    'PRES - Pano 2': 'PRESHANE / PANO 2',
                    'PRES - Pano 3': 'PRESH2hANE / PANO 3',
                    "P-17": "valfsan_pres17",
                    "P-20": "valfsan_pres20",
                    "P-21": "valfsan_pres21",
                    "P-29": "valfsan_pres29",
                    "P-36": "valfsan_pres36",
                    "P-69": "valfsan_pres_cinpresi",
                    "P-72": "valfsan_pres72"},
              "KALIPHANE ":{'KALIPHANE - Pano 1': 'valfsan_kaliphane_pano1',
                    "MF-02": "valfsan_kaliphane_mf-02"},
              "YÜZEY İŞLEM":{
                    'S-03,V-01,V-02': 'valfsan_yuzeyislem',
                    "T-19','T-20','T-21','T-22','T-23','T-24','T-25','T-26','T-27','T-34','T-37','T-43','T-44','T-45":'valfsan_yuzeyislem_2"',
                    'OTEC-03,OTEC-04': "valfsan_otecsantrifuj",
                    'S-01':'YÜZEY İŞLEM - Küçük Santrifüj S - 01',
                    'V-01':'YÜZEY İŞLEM - Büyük Vibratör V - 01'},
              "KURUTMA":{"K-25" : "KURUTMA - No 25",
                    "K-13','K-18','K-19','K-20','K-21','K-22','K-23','K-25','K-27','K-28": 'valfsan_pano1'},
              "YIKAMA": {'YKM-03': 'valfsan_yikama_protech_pano1'},
              "TEL EREZYON":{'(ER-03)': 'valfsan_telerezyon_pano1_er_03',
                    '(ER-04)': 'valfsan_telerezyon_pano2_er_04'},
              "KOMPRESÖR":{'KOMPRESÖR-ISIL': 'KOMPRESÖR / Isıl İşlem Yanı (9,5 bar - 22,5 kW)',
                    'KOM-04': 'valfsan_kompresor_04_mark',
                    'KOM-05': 'valfsan_kompresor_05_mark',
                    'KOM-06': 'valfsan_kompresor_06_mark',
                    'KOM-07': 'valfsan_kompresor_07_mark',
                    'KOM-08': 'valfsan_kompresor_08_mark',
                    'KOMPRESÖR-(3 adet)': 'valfsan_kompresor_yuksekbasinc'},
              "CHILLER SOGUTUCU":{'Chiller 1': 'valfsan_chillersogutucu1',
                    'Chiller 3': 'valfsan_chillersogutucu1',
                    'Chiller 4': 'valfsan_chillersogutucu1'},
              "KLIMA UNITELERI": {'KLİMA VRV': 'valfsan_klimavrvuniteleri_pano1',
                    'KLİMA T.ODA': 'valfsan_temizodaklimasantrali_pano1'},
              "HAVALANDIRMA - FAN": {'PRESHANE / EGZOST EMİŞ FANI (3 adet)': 'valfsan_preshaneemisfani_11kw'},
              "TRAFO":{'TRAFO - 1600 kVA': 'valfsan_trafo'}}




