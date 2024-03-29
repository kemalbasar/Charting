
from os.path import basename
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime,timedelta
from agent import ag

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import pendulum

local_tz = pendulum.timezone("Asia/Istanbul")
sender_email = "kbbudak@valfsan.com.tr"
recipient_email = "kbbudak@valfsan.com.tr"
subject = "Test Email from Python"
body = "This is a test email sent from Python through an Exchange server."
server = "mail.valfsan.com.tr"  # Exchange SMTP server addressa
port = 587  # Typical port for SMTP with StartTLS
username = "kbbudak"  # Often the same as your email
password = "1212casecase.."  # Your email account password


dag = DAG(
    'example_sql_task',
    schedule_interval=timedelta(days=7),  # Set your desired schedule interval
    start_date=datetime(2024, 1, 29, hour=3, minute=23, second=0, microsecond=0,tzinfo=local_tz)
,  # Set the start date
    catchup=False  # Set to True if you want to backfill historical runs
)



def send_email_via_exchange():
    # Prepare email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    file_path = "airflow-duties-center/airflow-env/dags/prod_eff.html"  # Change this to your file's path

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

# Example usage


sql_task = PythonOperator(
    task_id='execute_sql_query',
    python_callable=send_email_via_exchange,
    provide_context=True,  # Pass the task context to the function
    dag=dag
)