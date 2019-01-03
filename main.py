from flask import Flask, g, current_app, send_from_directory
from flask import request, session, render_template
import sqlite3
import time, hashlib
import datetime, os
import configparser
from flask import json, jsonify
import codecs
from finedb.data_stru import Business
from finepdf import TagPDFGenerator

bsnses = Business("data/data_stru.json")

app = Flask(__name__)
app.secret_key = "6089372-Stupid#Enough"

# Read Configuration from app_config.ini
config = configparser.ConfigParser()  # 注意大小写
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

# Database Settings
DATABASE = "data/finelab.sqlite3.db"


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)

        def make_dicts(cursor, row):
            return dict(
                (cursor.description[idx][0], value) for idx, value in enumerate(row)
            )

        db.row_factory = make_dicts
    return db


def pass_hash(in_string):
    md5 = hashlib.md5()
    md5.update((in_string + "nice_day").encode("utf-8"))
    return md5.hexdigest()


def get_user_info_dict(person_id):
    if person_id == 0:
        return {"logined": False}
    else:
        db = get_db()
        cur = db.cursor()
        query_sql_str = bsnses.createQuerySQL(
            "o_persons", read_auth_role="admin", filters_list=[], id=person_id
        )
        query_result = cur.execute(query_sql_str).fetchall()
        cur.close()
        query_result[0]["logined"] = True
        return query_result[0]


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


# [Request] User System API
@app.route("/user/json_api/login", methods=["POST", "GET"])
def user_login():
    if request.method == "POST":  # Log in, Return Status
        db = get_db()
        cur = db.cursor()
        input_list = request.form

        success = 0
        return_text = "Failed"
        try:
            # print(type(input_list['password']))
            query_result = cur.execute(
                "SELECT * FROM o_persons " + "WHERE username = ?",
                (input_list["username"],),
            ).fetchall()

            print(
                "USERNSME: ", input_list["username"], " PASS:", input_list["password"]
            )
            # print(query_result[0])
            print(type(query_result))
            if len(query_result) == 0:
                return_text = "No Such User"
            else:
                if query_result[0]["password"] == pass_hash(input_list.get("password")):
                    success = 1
                    return_text = "Login Succeed!"
                    session["logined_person_id"] = query_result[0]["person_id"]
                else:
                    return_text = "Wrong Pass"
        except Exception as e:
            success = 0
            raise e
        cur.close()
        if success:
            return json.dumps({"status": "succeeded", "text": return_text})
        else:
            return json.dumps({"status": "failed", "text": return_text})
    elif request.method == "GET":  # Get User Status
        print("get login ", request.args)
        return "Get Login"


@app.route("/user/json_api/logout", methods=["POST", "GET"])
def user_logout():
    if request.method == "POST":  # Nothing to do
        pass
    elif request.method == "GET":  # Log Out
        session["logined_person_id"] = False
        return "Get Logout"


@app.route("/user/json_api/register", methods=["POST", "GET"])
def user_register():
    if request.method == "POST":  # User register, Return Status
        db = get_db()
        cur = db.cursor()
        input_list = request.form

        success = 1

        try:
            print(type(input_list["password"]))
            cur.execute(
                "INSERT INTO o_persons "
                + "( username,    password       ) VALUES "
                + "( ?,    ?       )",
                (input_list["username"], pass_hash(input_list["password"])),
            )
            db.commit()
        except Exception as e:
            success = 0
            raise e
        cur.close()
        if success:
            return json.dumps({"status": "succeeded", "text": "Register Succeed!"})
        else:
            return json.dumps({"status": "failed", "text": "Register Failed!"})
    elif request.method == "GET":  # Nothing to do
        pass


@app.route("/user/json_api/info", methods=["POST", "GET"])
def user_info():
    if request.method == "POST":  # Change user info
        return "Change user info"
    elif request.method == "GET":  # Get User info
        return "Get user info"

# Debugging
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


# [Request] General API
@app.route("/general/json_api/target_insert", methods=["POST"])
def gen_target_insert():

    logined_person_id = session.get("logined_person_id")
    user_info_dict = get_user_info_dict(logined_person_id)
    if request.method == "POST":
        db = get_db()
        cur = db.cursor()
        input_list = request.form
        values_dict = {}
        b_name = input_list.get("HIDDEN_b_name")
        bsns_table_dict = bsnses.getFomatdDict(b_name)
        if bsns_table_dict is None:
            return json.dumps(
                {"status": "failed", "text": "No such business: !" + b_name}
            )
        for in_key, in_val in input_list.items():
            if in_key in bsns_table_dict["$COLU"]:
                values_dict[in_key] = in_val
        values_dicts_list = [values_dict]  # Dangerous, debug only!
        query_sql_str = bsnses.createInsertSQL(
            b_name, values_dicts_list, write_auth_role=user_info_dict.get("auth_role")
        )
        success = 1

        try:
            print("Insert SQL String:")
            print(query_sql_str)
            cur.execute(query_sql_str)
            db.commit()
        except Exception as e:
            success = 0
            raise e
        cur.close()
        if success:
            return json.dumps({"status": "succeeded", "text": "Insert Succeed!"})
        else:
            return json.dumps({"status": "failed", "text": "Insert Failed!"})
    elif request.method == "GET":
        pass


@app.route("/general/json_api/target_update", methods=["POST"])
def gen_target_update():
    logined_person_id = session.get("logined_person_id")
    user_info_dict = get_user_info_dict(logined_person_id)

    if request.method == "POST":
        db = get_db()
        cur = db.cursor()
        input_list = request.form
        values_dict = {}
        b_name = input_list.get("HIDDEN_b_name")
        tar_id = input_list.get("HIDDEN_tar_id")
        bsns_table_dict = bsnses.getFomatdDict(b_name)
        if bsns_table_dict is None:
            return json.dumps(
                {"status": "failed", "text": "No such business: !" + b_name}
            )
        for in_key, in_val in input_list.items():
            if in_key in bsns_table_dict["$COLU"]:
                values_dict[in_key] = in_val
        # values_dicts_list = [values_dict]     # Dangerous, debug only!
        # query_sql_str = bsnses.createInsertSQL(b_name,values_dicts_list,write_auth_role='admin')
        query_sql_str = bsnses.createUpdateSQL(
            b_name,
            values_dict,
            filters_list=[],
            write_auth_role=user_info_dict.get("auth_role"),
            id=tar_id,
        )
        success = 1

        try:
            print("Update SQL String:")
            print(query_sql_str)
            cur.execute(query_sql_str)
            db.commit()
        except Exception as e:
            success = 0
            raise e
        cur.close()
        if success:
            return json.dumps({"status": "succeeded", "text": "Update Succeed!"})
        else:
            return json.dumps({"status": "failed", "text": "Update Failed!"})
    elif request.method == "GET":
        pass


@app.route("/general/json_api/target_delete", methods=["POST"])
def gen_target_delete():
    logined_person_id = session.get("logined_person_id")
    user_info_dict = get_user_info_dict(logined_person_id)
    if request.method == "POST":
        db = get_db()
        cur = db.cursor()
        input_list = request.form

        b_name = input_list.get("VAR_b_name")
        tar_id = input_list.get("VAR_tar_id")
        bsns_table_dict = bsnses.getFomatdDict(b_name)
        if bsns_table_dict is None:
            return json.dumps(
                {"status": "failed", "text": "No such business: !" + b_name}
            )

        query_sql_str = bsnses.createDeleteSQL(
            b_name,
            filters_list=[],
            write_auth_role=user_info_dict.get("auth_role"),
            id=tar_id,
        )

        success = 1

        try:
            print("Update SQL String:")
            print(query_sql_str)
            cur.execute(query_sql_str)
            db.commit()
        except Exception as e:
            success = 0
            raise e
        cur.close()
        if success:
            return json.dumps({"status": "succeeded", "text": "Delete Succeed!"})
        else:
            return json.dumps({"status": "failed", "text": "Delete Failed!"})
        # return json.dumps({"status":"failed","text":b_name + tar_id})
    elif request.method == "GET":
        pass


# [Request] Template Based UI
@app.route("/tmplt_based_ui/", methods=["GET"])
@app.route("/tmplt_based_ui/index", methods=["GET"])
def t_base_index():
    if request.method == "POST":  # Nothing to do
        pass
    elif request.method == "GET":  # Show page
        return "Template Based UI"


@app.route("/tmplt_based_ui/user_register_form", methods=["GET"])
def t_base_register_form():
    logined_person_id = session.get("logined_person_id")
    user_info_dict = get_user_info_dict(logined_person_id)
    return render_template("user_register_form.htm", user_info_dict=user_info_dict)


@app.route("/tmplt_based_ui/user_login_form", methods=["GET"])
def t_base_login_form():
    logined_person_id = session.get("logined_person_id")
    user_info_dict = get_user_info_dict(logined_person_id)
    return render_template("user_login_form.htm", user_info_dict=user_info_dict)


@app.route("/tmplt_based_ui/user_logout", methods=["GET"])
def t_base_logout():
    session["logined_person_id"] = False
    logined_person_id = session.get("logined_person_id")
    user_info_dict = get_user_info_dict(logined_person_id)
    return render_template("user_logout.htm", user_info_dict=user_info_dict)


@app.route("/tmplt_based_ui/search", methods=["GET"])
def t_base_search():
    logined_person_id = session.get("logined_person_id")
    user_info_dict = get_user_info_dict(logined_person_id)

    db = get_db()
    cur = db.cursor()
    b_name = request.args.get("b_name")
    bsns_table_dict = bsnses.getFomatdDict(b_name)
    query_sql_str = bsnses.createQuerySQL(
        b_name, read_auth_role=user_info_dict.get("auth_role"), filters_list=[], id=None
    )

    query_result = cur.execute(query_sql_str).fetchall()

    # Delete Columns which should not be displayed in brief view
    for row_index in range(len(query_result)):
        for key in list(query_result[row_index].keys()):
            if bsns_table_dict["$COLU"][key].get("$DISP_show_in_brief_view") == False:
                query_result[row_index].pop(key)

    # Displacing Table Row Contents
    for row_index in range(len(query_result)):
        for key, val in query_result[row_index].items():
            content_displacer = bsns_table_dict["$COLU"][key]["$DISP_displacer"]
            if type(content_displacer) == dict:  # if there is a displacer
                origin_result = query_result[row_index][key]
                if content_displacer.__contains__(origin_result):
                    query_result[row_index][key] = content_displacer[origin_result]
            if query_result[row_index][key] == None:
                query_result[row_index][key] = ""
    cur.close()
    return render_template(
        "search.htm",
        user_info_dict=user_info_dict,
        bsns_table_dict=bsns_table_dict,
        query_result=query_result,
    )


@app.route("/tmplt_based_ui/target_scope", methods=["GET"])
def t_base_target_scope():
    logined_person_id = session.get("logined_person_id")
    user_info_dict = get_user_info_dict(logined_person_id)

    db = get_db()
    cur = db.cursor()
    b_name = request.args.get("b_name")  # business name
    tar_id = request.args.get("id")  # target id
    bsns_table_dict = bsnses.getFomatdDict(b_name)
    query_sql_str = bsnses.createQuerySQL(
        b_name,
        read_auth_role=user_info_dict.get("auth_role"),
        filters_list=[],
        id=tar_id,
    )

    # # debug
    # query_sql_str = """
    #     SELECT
    #             v_lab_planned_proj_menbers.proj_id              ,
    #             v_lab_planned_proj_menbers.proj_name            ,
    #             v_lab_planned_proj_menbers.menber_person_id     ,
    #             v_lab_planned_proj_menbers.menber_name          ,
    #             v_lab_planned_proj_menbers.menber_card_number   ,
    #             v_lab_planned_proj_menbers.act_type             ,
    #             v_lab_planned_proj_menbers.menber_role
    #     FROM
    #             v_lab_planned_proj_menbers
    #     WHERE
    #             proj_id = 1
    # """
    query_result = cur.execute(query_sql_str).fetchall()
    print(query_sql_str)  # debug
    print(query_result)  # debug
    cur.close()
    return render_template(
        "target_scope.htm",
        user_info_dict=user_info_dict,
        bsns_table_dict=bsns_table_dict,
        query_result=query_result,
    )


@app.route("/tmplt_based_ui/target_insert_form", methods=["GET"])
def t_base_target_insert_form():
    logined_person_id = session.get("logined_person_id")
    user_info_dict = get_user_info_dict(logined_person_id)
    b_name = request.args.get("b_name")  # business name
    bsns_table_dict = bsnses.getFomatdDict(b_name)
    return render_template(
        "target_insert_form.htm",
        user_info_dict=user_info_dict,
        bsns_table_dict=bsns_table_dict,
    )


@app.route("/tmplt_based_ui/target_update_form", methods=["GET"])
def t_base_target_update_form():
    logined_person_id = session.get("logined_person_id")
    user_info_dict = get_user_info_dict(logined_person_id)

    db = get_db()
    cur = db.cursor()
    b_name = request.args.get("b_name")  # business name
    tar_id = request.args.get("id")  # target id
    bsns_table_dict = bsnses.getFomatdDict(b_name)
    query_sql_str = bsnses.createQuerySQL(
        b_name, read_auth_role="tourist", filters_list=[], id=tar_id
    )
    query_result = cur.execute(query_sql_str).fetchall()
    # print(query_sql_str)  # debug
    # print(query_result)  # debug
    cur.close()
    return render_template(
        "target_update_form.htm",
        user_info_dict=user_info_dict,
        bsns_table_dict=bsns_table_dict,
        query_result=query_result,
    )


@app.route("/tmplt_based_ui/pdf_tag_gen_form", methods=["GET"])
def t_base_pdf_tag_gen_form():
    logined_person_id = session.get("logined_person_id")
    user_info_dict = get_user_info_dict(logined_person_id)

    db = get_db()
    cur = db.cursor()
    b_name = request.args.get("b_name")  # business name
    tmpl_id = request.args.get("tmpl_id")

    data_query_sql_str = bsnses.createQuerySQL(
        b_name, read_auth_role="tourist", filters_list=[]
    )
    data_query_result = cur.execute(data_query_sql_str).fetchall()


    template_query_sql_str = "SELECT * FROM 'o_pdf_tag_templates' WHERE template_id = %s"%(tmpl_id,)

    template_query_result = cur.execute(template_query_sql_str).fetchall()
    tmpl_str = template_query_result[0]['json_content']

    return render_template("pdf_tag_gen_form.htm", user_info_dict=user_info_dict, tmpl_str = tmpl_str)


@app.route("/tmplt_based_ui/debug/view_table", methods=["GET"])
def t_base_debug_view_table():
    logined_person_id = session.get("logined_person_id")
    user_info_dict = get_user_info_dict(logined_person_id)
    db = get_db()
    cur = db.cursor()

    t_name = request.args.get("t_name")
    table_info = cur.execute("PRAGMA table_info('%s')" % (t_name,)).fetchall()

    query_result = cur.execute("SELECT * FROM '%s'" % (t_name,)).fetchall()
    cur.close()
    return render_template(
        "debug_view_table.htm",
        user_info_dict=user_info_dict,
        table_info=table_info,
        query_result=query_result,
    )


# [Request] Single-Page UI
@app.route("/sigl_page_ui/", methods=["GET"])
def sigl_page_ui():
    if request.method == "POST":  # Nothing to do
        pass
    elif request.method == "GET":  # Show page
        return "Single Page"


# [Request] Tests
@app.route("/test/db", methods=["GET"])
def test_db():

    return "Test DB"


@app.route("/test/json_form", methods=["POST"])
def test_json_form():
    if hasattr(request, "json"):
        print("====================")
        print("has json!")
        print("type:", type(request.json))
        print(request.json)
    else:
        print("has no json!")
    if hasattr(request, "data"):
        print("has data!")
        print("type:", type(request.data))
        print(request.form)
    else:
        print("has no data!")
    if hasattr(request, "form"):
        print("has form!")
        print("type:", type(request.form))
        print(request.form)
    else:
        print("has no form!")

    return "Test DB"


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
