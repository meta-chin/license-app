import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

conn = sqlite3.connect("user_data.db", check_same_thread=False)
c = conn.cursor()


def create_req_tables():
    sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS license_plate_data (
                                            first_name text,
                                            last_name text,
                                            license_plate text PRIMARY KEY,
                                            phone text
                                        ); """

    c.execute(sql_create_projects_table)
    sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS user (
                                                id integer PRIMARY KEY,
                                                email text,
                                                password text,
                                                name text
                                            ); """

    c.execute(sql_create_projects_table)
    conn.commit()


def show_tables():
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print(c.fetchall())


def show_table_names():
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print(c.fetchall())


def show_table(name):
    c.execute("SELECT * FROM " + str(name))
    print(c.fetchall())


def del_element(table, id):
    c.execute("DELETE FROM " + str(table) + " WHERE id = " + id)
    conn.commit()
    c.execute("SELECT * FROM " + str(table))
    print(c.fetchall())


def add_user(table, id, email, password, name):
    try:
        cmm = "INSERT INTO " + table + " VALUES('" + str(id) + "','" + str(email) + "','" + str(
            generate_password_hash(password, method='sha256')) + "','" + str(name) + "')"
        c.execute(cmm)
        conn.commit()
        show_table(table)
        return True
    except:
        show_table('user')
        return False


create_req_tables()
show_table_names()
show_table('user')
add_user(table='user', id=1, email="admin@admin.com", password='admin', name='admin')
