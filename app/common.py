import sqlite3


def create_connection(db_file):

    try:
        conn = sqlite3.connect(db_file)
        return conn
    except ConnectionError as e:
        print(e)

    return None


def create_task(conn, task, sql):

    # review sql query
    cur = conn.cursor()
    cur.execute(sql, task)
    return cur.lastrowid
