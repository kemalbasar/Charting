# from lxml import etree
# from urllib.request import urlopen
# from bs4 import BeautifulSoup
# from config import url_dyn
# import datetime as dt
# from datetime import date
#
# # webservice names on canias
# #
# # SELECT * FROM IASWEBSERVICES WHERE SERVICENAME LIKE '%VLF%'
#
# # connection portal on liv mysql database :
# # WSCANIAS
#
# def get_work_hour(workcenter='DD-05',workstart = "05.12.2022 01:00:00",workend = "05.12.2022 09:00:00"):
#
#     workstart = workstart.strftime("%d.%m.%Y %H:%M:%S")
#     workend = workend.strftime("%d.%m.%Y %H:%M:%S")
#     workstart = str(workstart)
#     workend = str(workend)
#     workstart = workstart.replace(" ", "#")
#     workend = workend.replace(" ", "#")
#     url_dyn = "http://172.30.134.16:20000/services/btstarter.aspx?tran_code=WSCANIAS&tran_param=VLFPYPORTAL,"
#     url_dyn = url_dyn + workcenter + '#' + workstart  + '#' + workend + '#' + 'bla' + '#'
#     with urlopen(url_dyn) as response:
#         body = response.read()
#     soup = BeautifulSoup(body, 'html.parser')
#     a = soup.find('batch_process_started')
#     dom = etree.HTML(str(soup))
#     return dom.xpath('/html/body/form/text()')[2][9:14]

from os.path import basename
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import pendulum
from selenium.webdriver.firefox.options import Options
from selenium import webdriver

local_tz = pendulum.timezone("Asia/Istanbul")
sender_email = "canias@valfsan.com.tr"
server = "mail.valfsan.com.tr"  # Exchange SMTP server addressa
port = 587  # Typical port for SMTP with StartTLS
username = "kbbudak"  # Often the same as your email
password = "1212casecase.."  # Your email account password

dag = DAG(
    'sent_mail',
    schedule_interval=timedelta(days=7),  # Set your desired schedule interval
    start_date=datetime(2024, 1, 29, hour=3, minute=23, second=0, microsecond=0, tzinfo=local_tz)
    ,  # Set the start date
    catchup=False  # Set to True if you want to backfill historical runs
)


def create_report_file(adress):
    options = Options()
    options.add_argument("--headless")
    geckodriver_path = '/usr/local/bin/geckodriver'
    driver = webdriver.Firefox(executable_path=geckodriver_path, options=options)

    # Load the page
    driver.get(f"http://172.30.134.22:8050/{adress}")

    # Wait for a certain time or until a specific condition is met
    time.sleep(120)  # Wait for 10 seconds
    # Or use WebDriverWait for more precise waiting conditions

    # Save the page source to a file
    with open("adress.html", "w", encoding='utf-8') as f:
        f.write(driver.page_source)

    # Clean up
    driver.quit()


def send_email_via_exchange(recipient_email="kbbudak@valfsan.com.tr", subject="Test Email from Python",
                            body="This is a test email sent from Python through an Exchange server."):
    # Prepare email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    file_path = "cnc.html"  # Change this to your file's path

    # Attach the file
    with open(file_path, "rb") as file:
        part = MIMEApplication(
            file.read(),
            Name=basename(file_path)
        )
    # After the file is closed
    part['Content-Disposition'] = 'attachment; filename="%s"' % basename(file_path)
    msg.attach(part)

    # Connect to Exchange SMTP server and send email
    try:
        with smtplib.SMTP(server, port) as smtp:
            smtp.ehlo()  # Can be omitted
            smtp.starttls()  # Secure the connection
            smtp.login(username, password)
            smtp.send_message(msg)
            print("Email successfully sent!")
    except Exception as e:
        print(f"Failed to send email: {e}")


scrap_report_fromwep_cnc = PythonOperator(
    task_id='crf_cnc',
    python_callable=create_report_file,
    provide_context=True,  # Pass the task context to the function
    dag=dag,
    op_args=["adrcnc"]

)
scrap_report_fromwep_cnctorna = PythonOperator(
    task_id='crf_cnctorna',
    python_callable=create_report_file,
    provide_context=True,  # Pass the task context to the function
    dag=dag,
    op_args=["adrcnctorna"],
    retries=5,  # Görev için maksimum deneme sayısı
    retry_delay=timedelta(minutes=5)

)
scrap_report_fromwep_pres1 = PythonOperator(
    task_id='crf_pres1',
    python_callable=create_report_file,
    provide_context=True,  # Pass the task context to the function
    dag=dag,
    op_args=["adrpres1"],
    retries=5,  # Görev için maksimum deneme sayısı
    retry_delay=timedelta(minutes=5)

)
scrap_report_fromwep_pres2 = PythonOperator(
    task_id='crf_pres1',
    python_callable=create_report_file,
    provide_context=True,  # Pass the task context to the function
    dag=dag,
    op_args=["adrpres2"],
    retries=5,  # Görev için maksimum deneme sayısı
    retry_delay=timedelta(minutes=5)

)

    send_report_as_email_cnc = PythonOperator(
    task_id='send_report_as_email_cnc',
    python_callable=send_email_via_exchange,
    provide_context=True,
    dag=dag,
    retries=5,  # Görev için maksimum deneme sayısı
    retry_delay=timedelta(minutes=5)
)
send_report_as_email_cnctorna = PythonOperator(
    task_id='send_report_as_email_cnctorna',
    python_callable=send_email_via_exchange,
    provide_context=True,
    dag=dag,
    retries=5,  # Görev için maksimum deneme sayısı
    retry_delay=timedelta(minutes=5)
)
send_report_as_email_pres1 = PythonOperator(
    task_id='send_report_as_email_pres1',
    python_callable=send_email_via_exchange,
    provide_context=True,
    dag=dag,
    retries=5,  # Görev için maksimum deneme sayısı
    retry_delay=timedelta(minutes=5)
)
send_report_as_email_pres2 = PythonOperator(
    task_id='send_report_as_email_pres2',
    python_callable=send_email_via_exchange,
    provide_context=True,
    dag=dag,
    retries=5,  # Görev için maksimum deneme sayısı
    retry_delay=timedelta(minutes=5)
)

scrap_report_fromwep_cnc >> send_report_as_email_cnc >> scrap_report_fromwep_cnctorna >> send_report_as_email_cnctorna >> \
scrap_report_fromwep_pres1 >> send_report_as_email_pres1 >> scrap_report_fromwep_pres2 >> send_report_as_email_pres2
