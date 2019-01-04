from flask import Flask, g, current_app, send_from_directory
from flask import request, session, render_template
import sqlite3
import time, hashlib
import datetime, os
import configparser
from flask import json, jsonify
import codecs
from finedb import DataFrame
from finepdf import TagPDFGenerator

from app_globals import *

bsnses = DataFrame("data/data_frame.json")

app = Flask(__name__)
app.secret_key = "6089372-Stupid#Enough"

# Read Configuration from app_config.ini
config = configparser.ConfigParser()  
config.read("app_config.ini", encoding="utf-8")

G_LANG = "ZH"
with app.app_context():  # To be visited in templates
    current_app.config["G_LANG"] = G_LANG
    current_app.config["G_AppName"] = config.get(G_LANG, "AppName")
    current_app.config["G_AppDiscription"] = config.get(G_LANG, "AppDiscription")
    current_app.config["G_ParentOrganizationName"] = config.get(
        G_LANG, "ParentOrganizationName"
    )
    current_app.config["G_ChildOrganizationName"] = config.get(
        G_LANG, "ChildOrganizationName"
    )

    current_app.config["G_bsnses_dict"] = bsnses.getFomatdDict()



# Database Auto Close
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


# [Request] Index
@app.route("/")
@app.route("/index")
def index():
    logined_person_id = session.get("logined_person_id")
    user_info_dict = get_user_info_dict(logined_person_id)
    return render_template("index.htm", user_info_dict=user_info_dict)


# [Request] Tag PDF Generator: Debugging
@app.route("/download/tag_pdf", methods=["POST", "GET"])
def gen_pdf_and_download():
    if request.method == "POST":  
        db = get_db()
        cur = db.cursor()
        input_list = request.form
        
        # cur.

        json_string = input_list['template']
        directory = os.getcwd()  # 假设在当前目录
        pdf_gen = TagPDFGenerator()
        pdf_gen.setTemplateFromJsonString(directory, json_string)
        pdf_gen.setDataFromList(
            directory,
            [
                ['Title','2','3','4','1','2','3','4'],
                ['Title','2','3','4','1','2','3','4'],
                ['Title','2','3','4','1','2','3','4'],
                ['Title','6','7','8','1','2','3','4']
            ]
        )

        # 需要知道2个参数, 第1个参数是本地目录的path, 第2个参数是文件名(带扩展名)
        t = time.time()
        nowTime = str((lambda:int(round(t * 1000)))())
        fn = nowTime+".pdf"
        pdf_gen.savePDF(fn)
        return send_from_directory(directory, fn, as_attachment=True)


# [Request] IOT Applications API
@app.route("/iot/json_api/active_tag_reader", methods=["POST"])
def iot_active_tag_reader():
    if request.method == "POST":  # Fetch Device Data
        return "Fetch Device Data"
    elif request.method == "GET":  # Nothing to do
        pass


# [Request] IOT Applications Pages
@app.route("/iot/pages/screen", methods=["GET"])
def iot_screen_page():
    if request.method == "POST":  # Nothing to do
        pass
    elif request.method == "GET":  # Show page
        return "Screen Display Page"


# [Request] Utility API
@app.route("/utility/json_api/datetime", methods=["GET"])
def utl_datetime():
    if request.method == "POST":  # Nothing to do
        pass
    elif request.method == "GET":  # Show date time timezone
        localtime = time.localtime(time.time())
        return jsonify(
            data="Server Time",
            timezone_str="UTC" + time.strftime("%z", localtime),
            time_str=time.strftime("%H:%M:%S", localtime),
            date_str=time.strftime("%Y-%m-%d", localtime),
            weekday_str=time.strftime("%A", localtime),
        )


@app.route("/utility/json_api/app_info", methods=["GET"])
def ult_app_info():
    if request.method == "POST":  # Nothing to do
        pass
    elif request.method == "GET":  # Show Application Information
        return "APP Info"





from bp_tmplt_based_ui import tmplt_based_ui
from bp_user_api import user_api
from bp_general_api import general_api

app.register_blueprint(tmplt_based_ui, url_prefix='/tmplt_based_ui') 
app.register_blueprint(user_api, url_prefix='/user/json_api')
app.register_blueprint(general_api, url_prefix='/general/json_api')


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
