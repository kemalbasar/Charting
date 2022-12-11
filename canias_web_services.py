from lxml import etree
from urllib.request import urlopen
from bs4 import BeautifulSoup
from config import url_dyn
import datetime as dt
from datetime import date

# webservice names on canias
#
# SELECT * FROM IASWEBSERVICES WHERE SERVICENAME LIKE '%VLF%'

# connection portal on liv mysql database :
# WSCANIAS

def get_work_hour(workcenter='DD-05',workstart = "05.12.2022 01:00:00",workend = "05.12.2022 09:00:00"):

    workstart = workstart.strftime("%d.%m.%Y %H:%M:%S")
    workend = workend.strftime("%d.%m.%Y %H:%M:%S")
    workstart = str(workstart)
    workend = str(workend)
    workstart = workstart.replace(" ", "#")
    workend = workend.replace(" ", "#")
    url_dyn = "http://172.30.134.16:20000/services/btstarter.aspx?tran_code=WSCANIAS&tran_param=VLFPYPORTAL,"
    url_dyn = url_dyn + workcenter + '#' + workstart  + '#' + workend + '#' + 'bla' + '#'
    with urlopen(url_dyn) as response:
        body = response.read()
    soup = BeautifulSoup(body, 'html.parser')
    a = soup.find('batch_process_started')
    dom = etree.HTML(str(soup))
    return dom.xpath('/html/body/form/text()')[2][9:14]
