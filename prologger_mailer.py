import datetime
import smtplib
import schedule
import time
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import Config
from os.path import basename

config = Config()


def send_punchlist_email(destination, default_config, attachment=None):

    # arg0: company email(s)
    # arg1: default configuration
    # arg2: punchlist attachment

    # sending reset email
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Punchlist update ' + str(datetime.datetime.now())
    msg['From']= default_config.MAIL_USERNAME
    msg['To'] = destination

    text = "Attached punchlist with items in your scope"

    html = """\
    <html>
    <head></head>
    <body>
    <p>Attached punchlist with items in your scope
    </p>
    </body>
    </html>
    """

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    with open(attachment, "rb") as fil:
        part3 = MIMEApplication(
            fil.read(),
            Name=basename(attachment)
        )
    # After the file is closed
    part3['Content-Disposition'] = 'attachment; filename="%s"' % basename(attachment)

    msg.attach(part1)
    msg.attach(part2)
    msg.attach(part3)

    try:
        server = smtplib.SMTP_SSL(default_config.MAILSERVER, default_config.MAILPORT)
        server.ehlo()
        server.login(default_config.MAIL_USERNAME, default_config.MAIL_PASSWORD)
        server.sendmail(default_config.MAIL_USERNAME, destination, msg.as_string())
        server.close()

        print('Email sent!')
    except:
        print('Something went wrong...')


def task0(configuration):
    try:
         send_punchlist_email("mchrappan@gmail.com,", configuration, config.ATTACHMENT_FOLDER + "punchlist_attachment_0.xlsx")
         print("task0 running")
    except Exception as e:
         print(e)
         return 1



def task1(configuration):
    try:
         send_punchlist_email("magyar1886@gmail.com,", configuration, config.ATTACHMENT_FOLDER + "punchlist_attachment_1.xlsx")
         print("task1 running")
    except Exception as e:
         print(e)
         return 1




def mailer(configuration):
    print("mailer script is running")
    schedule.every().day.at("08:00").do(task0, configuration=configuration)
    schedule.every().hour.do(task1, configuration=configuration)

    while True:

        # Checks whether a scheduled task
        # is pending to run or not
        schedule.run_pending()
        time.sleep(1)

mailer(config)