from app.common import create_connection
import sqlite3


def dashboard_query(database, option, project_id=0, user_id=0):

    # create a database connection
    conn = create_connection(database)
    cur = conn.cursor()

    if option == 0:
        # get rows for each table
        cur.execute("SELECT projects_meta.employee_id FROM projects_meta WHERE projects_meta.project_id = ? AND projects_meta.user_allowed = ?", (project_id,user_id))
        rows = cur.fetchone()
    elif option == 1:
        # get rows for each table
        cur.execute("SELECT punchlist.status, COUNT(punchlist.status) FROM punchlist GROUP BY punchlist.status ORDER BY status ASC")
        rows = cur.fetchall()
    elif option == 2:
        # get rows for each table
        cur.execute("SELECT punchlist.status, COUNT(punchlist.status) FROM punchlist WHERE punchlist.closure_id=? GROUP BY punchlist.status ORDER BY status ASC", (user_id,))
        rows = cur.fetchall()
    elif option == 3:
        # get rows for each table
        cur.execute("SELECT systems.name, COUNT(systems.name) FROM punchlist INNER JOIN systems ON punchlist.system_id = systems.id WHERE punchlist.status = 0 GROUP BY systems.name")
        rows = cur.fetchall()

    return rows








