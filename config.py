import pandas as pd

server = '172.30.134.12'
database = 'VALFSAN604'
username = 'kemal'
password = 'casecase12..'

reengen_username = "takgun@valfsan.com.tr"
reengen_password = '1234Ta1234'
reengen_company = 'valfsan'


project_directory = r"F:\pycarhm projects"

directory = project_directory + r'\Charting\queries'
dirofquery = project_directory + r'\Charting\queries\query2.txt'
dirofnewline = project_directory + r'\Charting\queries\dateofstart.txt'
url_dyn = "http://172.30.134.16:20000/services/btstarter.aspx?tran_code=WSCANIAS&tran_param=VLFPYPORTAL,"

def set_df_size(maxrow, maxcolumn, maxwidth, maxcolwidth):
    pd.set_option('display.max_rows', maxrow)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 500)
    pd.set_option('display.max_colwidth', maxcolwidth)

valftoreeg = {"CNC-07" : "valfsan_cncfreze_makina_cnc_07",
            "CNC-04" : "valfsan_cncfreze_trident_cnc_04",
            "CNC-20" : "valfsan_cncfreze_dmc_cnc_20",
            "CNC-12"  : 'valfsan_cnctorna_starcnc_kayarotomat_cnc_12',
            "CNCTO-07" : 'valfsan_cnctorna_dmc_cnc_to_07',
            "CNCTO-15" : 'valfsan_cnctorna_dmgmori_cnc_to_15' ,
            "CNCTO-09" : 'valfsan_cnctorna_spinner_cnc_to_09' ,
            "CNC-07 " : 'valfsan_cncfreze_makina_cnc_07' ,
            "CNC-24" : 'valfsan_cncfreze_johnford_cnc_24' ,
            "CNC-03" :  'valfsan_cncfreze_haas_cnc_03' ,
            "MF-02" : "valfsan_kaliphane_mf-02",
            "F-01" : 'valfsan_isilislem_cinfirini',
            "F-02" : "valfsan_isilislem_hintfirini",
            "F-03" : "valfsan_isilislem_bakirkaynakfirini",
            "MF-01" : "valfsan_isilislem_menevisfirini_mf_01",
            "MF-04" : "valfsan_isilislem_menevisfirini_mf_04",
            "DM-02" : "valfsan_dogrultma_dm_02",
            "DD-02":"valfsan_taslama_dd_02",
            "DD-03": "valfsan_taslama_dd_03",
            "DD-04": "valfsan_taslama_dd_04",
            "DD-05": "valfsan_taslama_dd_05",
            "DD-06": "valfsan_taslama_dd_06",
            "DD-07": "valfsan_taslama_dd_07",
            "DD-10": "valfsan_taslama_discus_dd_10",
            "CT-03": "valfsan_taslama_ct_03",
            "STAG-01": "valfsan_taslama_stag_01",
            "STAG-02": "valfsan_taslama_stag_02",
            "STAG-3": "valfsan_taslama_stag_03",
            "P-17": "valfsan_pres17",
            "P-20": "valfsan_pres20",
            "P-21": "valfsan_pres21",
            "P-29": "valfsan_pres29",
            "P-36": "valfsan_pres36",
            "P-69": "valfsan_pres_cinpresi",
            "P-72": "valfsan_pres72"
}


