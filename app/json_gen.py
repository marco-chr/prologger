import json
import sqlite3


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = sqlite3.connect(db_file)
    return conn


def select_all_tasks(master_conn, project_conn, user, user_id, project_id, option, static_directory):
    """
    Query all rows in the punchlist table
    :param conn: the Connection object
    :return:
    """
    cur = project_conn.cursor()
    master_cur = master_conn.cursor()
    base_query = "SELECT punchlist.id, punchlist.status, punchlist.discipline, punchlist.description, punchlist.comments, punchlist.date_orig, punchlist.due_date, employees1.display AS author, employees2.display AS closure, companies.name AS supplier, systems.name AS system, floors.floor, phases.name AS phase,categories.name AS cat, buildings.name AS building FROM punchlist INNER JOIN employees AS employees1 ON punchlist.author_id = employees1.id INNER JOIN employees AS employees2 ON punchlist.closure_id = employees2.id INNER JOIN companies ON punchlist.supplier_id = companies.id INNER JOIN systems ON punchlist.system_id = systems.id INNER JOIN floors ON punchlist.floor_id = floors.id INNER JOIN phases ON punchlist.phase_id = phases.id INNER JOIN categories ON punchlist.cat_id = categories.id INNER JOIN buildings ON punchlist.building_id = buildings.id"

    # OPTION is an integer from 1 to 5
    # 1 all items
    # 2 open items
    # 3 closed items
    # 4 item assigned to user
    # 5 item assigned to company

    if option == 1:
        query = base_query
        cur.execute(query)

    elif option == 2:
        addon_query=" WHERE punchlist.status='0'"
        query = base_query + addon_query
        cur.execute(query)

    elif option == 3:
        addon_query=" WHERE punchlist.status='1'"
        query = base_query + addon_query
        cur.execute(query)

    elif option == 4:
        master_cur.execute("SELECT projects_meta.employee_id FROM projects_meta WHERE projects_meta.user_allowed=? AND projects_meta.project_id=?", (user_id, project_id))
        row = master_cur.fetchone()

        addon_query=" WHERE punchlist.closure_id=" + "'" + str(row[0]) + "'"
        query = base_query + addon_query
        cur.execute(query)

    elif option == 5:

        master_cur.execute("SELECT projects_meta.employee_id FROM projects_meta WHERE projects_meta.user_allowed=? AND projects_meta.project_id=?", (user_id, project_id))
        row = master_cur.fetchone()

        cur.execute("SELECT employees.companyid FROM employees WHERE employees.id=" + "'" + str(row[0]) + "'")
        row = cur.fetchone()

        base_query = "SELECT punchlist.id, punchlist.status, punchlist.discipline, punchlist.description, punchlist.comments, punchlist.date_orig, punchlist.due_date, employees1.display AS author, employees2.display AS closure, companies.name AS supplier, systems.name AS system, floors.floor, phases.name AS phase,categories.name AS cat, buildings.name AS building, employees3.companyid AS closure_company FROM punchlist INNER JOIN employees AS employees3 ON punchlist.closure_id = employees3.id INNER JOIN employees AS employees1 ON punchlist.author_id = employees1.id INNER JOIN employees AS employees2 ON punchlist.closure_id = employees2.id INNER JOIN companies ON punchlist.supplier_id = companies.id INNER JOIN systems ON punchlist.system_id = systems.id INNER JOIN floors ON punchlist.floor_id = floors.id INNER JOIN phases ON punchlist.phase_id = phases.id INNER JOIN categories ON punchlist.cat_id = categories.id INNER JOIN buildings ON punchlist.building_id = buildings.id"
        addon_query=" WHERE punchlist.supplier_id=" + "'" + str(row[0]) + "'"
        query = base_query + addon_query
        cur.execute(query)

    rows = cur.fetchall()

    records = []
    
    for row in rows:
        record = {}
        for i in range(0, len(row)):
                record.update({cur.description[i][0]: row[i]})
        records.append(record)

    json_data = json.dumps({'data': records})
    filename = static_directory + "datatable_" + user + ".ajax"
    file = open(filename, "w")
    file.write(json_data)
    file.close()


def select_task_by_priority(conn, priority):
    """
    Query tasks by priority
    :param conn: the Connection object
    :param priority:
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM punchlist WHERE cat_id=?", (priority,))
    rows = cur.fetchall()

    for row in rows:
        print(row)


def json_gen(master_db, project_db, view, user, user_id, project_id, static_dir):

    master_conn = create_connection(master_db)
    project_conn = create_connection(project_db)

    if view == 1:
        with project_conn:
            select_all_tasks(master_conn, project_conn, user, user_id, project_id, 1, static_dir)
    elif view == 2:
        with project_conn:
            select_all_tasks(master_conn, project_conn, user, user_id, project_id, 2, static_dir)
    elif view == 3:
        with project_conn:
            select_all_tasks(master_conn, project_conn, user, user_id, project_id, 3, static_dir)
    elif view == 4:
        with project_conn:
            select_all_tasks(master_conn, project_conn, user, user_id, project_id, 4, static_dir)
    elif view == 5:
        with project_conn:
            select_all_tasks(master_conn, project_conn, user, user_id, project_id, 5, static_dir)
