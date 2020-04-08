import time
import threading
import os
import datetime
from shutil import copyfile

from app import db
from app.models import Projects_master
from app.xls_export import punchlist_export
from app.common import create_connection
import subprocess as sp
from config import Config

# generate an instance of configuration class
config = Config()

# VARS to contains email jobs
# job counter
job_list = []
job_counter = 0


# create punchlist attachment for recurrent company email
def create_punchlist_attachment(job , db_path, company_id):

    # assign query var
    sqlfile = open(config.QUERIES_FOLDER + 'punchlist.sql', "r")
    if sqlfile.mode == 'r':
        query = sqlfile.read()

    sql_query_addon = "WHERE punchlist.supplier_id = '" + str(company_id) + "';"
    query = query + " " + sql_query_addon

    # export punchlist for selected company
    punchlist_export(db_path, config.ATTACHMENT_FOLDER, config.IMAGES_FOLDER, query, 'punchlist_attachment_' + str(job))


def poll_projects():

    projects = []
    global job_counter
    global job_list

    # create a database connection
    database = os.path.join(config.BASEDIR, "prologger_master.db")
    conn = create_connection(database)
    cur = conn.cursor()

    cur.execute("SELECT * FROM PROJECTS_MASTER")
    rows = cur.fetchall()

    print("Appending project db filenames")
    for row in rows:
        projects.append(row[1])

    # open script file in append mode
    script_handle = open("./prologger_mailer.py", "a")

    # cycle through each project
    for project in projects:

        # poll companies
        poll_companies(project, script_handle)

    # append main loop
    script_handle.write("\r\n")
    script_handle.write("\r\n")
    script_handle.write("def mailer(configuration):\r\n")
    script_handle.write("    print(\"mailer script is running\")\r\n")

    print(job_list)

    for el in job_list:
        script_handle.write("    schedule.every().minute.do(task" + str(el[0]) + ", configuration=configuration)\r\n")

    # close script file
    script_handle.write("\r\n")
    script_handle.write("    while True:\r\n")
    script_handle.write("\r\n")
    script_handle.write("        # Checks whether a scheduled task\r\n")
    script_handle.write("        # is pending to run or not\r\n")
    script_handle.write("        schedule.run_pending()\r\n")
    script_handle.write("        time.sleep(1)\r\n")
    script_handle.write("\r\n")
    script_handle.write("mailer(config)")
    script_handle.close()


def poll_companies(db_filename, file_handle):

    # for each company check if flag is set to send email and check frequency
    # write corresponding code to script

    # create a database connection
    database = os.path.join(config.BASEDIR, str(db_filename) + ".db")
    conn = create_connection(database)
    cur = conn.cursor()

    print("Polling database " + str(db_filename))
    cur.execute("SELECT companies.id,companies.sendmail,companies.email1,companies.email2,companies.frequency FROM COMPANIES")
    rows = cur.fetchall()

    global job_counter
    global job_list

    for row in rows:
        if row[1] == 1:
            # append section to script file with proper email and frequency
            email_field = str(row[2] + "," + row[3])
            print("append new task " + str(job_counter) + " with freq " + str(row[4]))
            file_handle.write("def task" + str(job_counter) + "(configuration):\r\n")
            file_handle.write("    send_punchlist_email(\"" + email_field + "\", configuration, config.ATTACHMENT_FOLDER + \"punchlist_attachment_" + str(job_counter) + ".xlsx\"" + ")\r\n")
            file_handle.write("    print(\"task" + str(job_counter) + " running\")\r\n")
            job_list.append([job_counter, row[4]])

            # Create attachment
            create_punchlist_attachment(str(job_counter), database, row[0])
            job_counter += 1

#
# SCHEDULER
#


schedule.every().day.at("10:30").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)

def run_scheduler():
    while True:

        print("Starting new scheduler task at " + str(datetime.datetime.now()))

        # run mailer script sub process
        mailer_process = sp.Popen(['python', 'prologger_mailer.py'])

        # TO DO: kill process at 0.00AM
        time.sleep(180)

        # kill subprocess
        sp.Popen.terminate(mailer_process)
        print("Thread killed")

        # delete script
        os.remove('./prologger_mailer.py')
        copyfile('./prologger_mailer_default.py', './prologger_mailer.py')

        # reset vars
        global job_list
        global job_counter

        job_list = []
        job_counter = 0

        # poll_projects: write the new script
        print("Polling projects for change in configuration")
        poll_projects()
        print("Changes logged in new script file")

        time.sleep(5)


scheduler_thread = threading.Thread(target=run_scheduler())
scheduler_thread.start()

