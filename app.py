from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from __init__ import create_app, db
import sqlite3
import numpy as np
from dl_model import OCR
import os

conn = sqlite3.connect("user_data.db", check_same_thread=False)
c = conn.cursor()
BASE_PATH = os.getcwd()
UPLOAD_PATH = os.path.join(BASE_PATH, 'static/upload/')
main = Blueprint('main', __name__)


def get_approval(text, c):

    try:
        text = text.replace(" ", "")
        cmm = "SELECT * FROM license_plate_data WHERE license_plate=" + "'" + text + "'"
        c.execute(cmm)
        name, surname, _, _ = c.fetchall()[0]
        full_name = name + " " + surname
        return "Allowed", full_name, id
    except:
        return "Denied", "Unknown", None


def get_table(c):
    try:
        cmm = "SELECT * FROM license_plate_data"
        c.execute(cmm)
        appr_list = np.array(c.fetchall())
    except:
        appr_list = [["Failed", "Failed", "Failed", "Failed"]]
    return appr_list


def insert_data(c, data):
    try:
        cmm = "INSERT INTO license_plate_data VALUES('" + str(data[0]) + "','" + str(data[1]) + "','" + str(
            data[2]) + "','" + str(data[3]) + "')"
        c.execute(cmm)
        conn.commit()
        return True
    except:
        return False


def remove_data(c, pl):
    try:
        cmm = "DELETE FROM license_plate_data WHERE license_plate=='" + str(pl) + "'"
        c.execute(cmm)
        conn.commit()
        return True
    except:
        return False


@main.route('/')  # home page that return 'index'
def index():
    try:
        return render_template('index_login.html', name="("+current_user.name+")")
    except:
        return render_template('index_login.html',name="")


@main.route('/profile', methods=['POST', 'GET'])  # profile page that return 'profile'
@login_required
def profile_ocr():
    if request.method == 'POST':
        upload_file = request.files['image_name']
        filename = upload_file.filename
        path_save = os.path.join(UPLOAD_PATH, filename)
        upload_file.save(path_save)
        text = OCR(path_save, filename)
        approval, full_name, id = get_approval(text, c)

        return render_template('profile_ocr.html', upload=True, upload_image=filename, text=text,name="("+current_user.name+")",lname =full_name ,approval=approval)

    return render_template('profile_ocr.html', name="("+current_user.name+")")


@main.route('/database', methods=['POST', 'GET'])  # profile page that return 'profile'
@login_required
def database():
    status = "Do something"
    tb_head = ("First name", "Last name", "License plate", "Phone number")
    tbl = get_table(c)
    if request.method == 'POST':
        if request.form['submit_button'] == "Add vehicle":
            phone = request.form.get('phone', "None")
            plate_num = request.form.get('license_Plate', "None").replace(" ", "")
            last_name = request.form.get('last_name', "None")
            first_name = request.form.get('first_name', "None")
            if phone == "" or plate_num == "" or last_name == "" or first_name == "":
                status = "Please fill all values"
                return render_template('database.html', name="("+current_user.name+")", column_names=tb_head, row_data=tbl,
                                       zip=zip, status=status)
            inserted = insert_data(c, data=[first_name, last_name, plate_num, phone])
            if not inserted:
                status = "Adding data failed. Already existing?"
            else:
                status = "Done"
            tbl = get_table(c)

        elif request.form['submit_button'] == "Remove":

            if request.form.get('removeplate', "None") == "":
                status = "Which number plate do you want to remove?"
                return render_template('database.html', name="("+current_user.name+")", column_names=tb_head, row_data=tbl,
                                       zip=zip, status=status)
            deleted = remove_data(c, request.form.get('removeplate', "None"))
            if not deleted:
                status = "Error"
            tbl = get_table(c)
    return render_template('database.html',name="("+current_user.name+")", column_names=tb_head, row_data=tbl, zip=zip,
                           status=status)


app = create_app()  # we initialize our flask app using the __init__.py function
if __name__ == '__main__':
    db.create_all(app=create_app())  # create the SQLite database
    app.run(debug=True)  # run the flask app on debug mode
