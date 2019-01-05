from flask import Blueprint, request, session, render_template
import json
from app_globals import bsnses, get_db, get_user_info_dict, pass_hash

user_api = Blueprint('user_api',__name__) 

# [Request] User System API
@user_api.route("/login", methods=["POST", "GET"])
def user_login():
    if request.method == "POST":  # Log in, Return Status
        db = get_db()
        cur = db.cursor()
        input_list = request.form

        success = 0
        return_text = "Failed"
        try:
            query_result = cur.execute(
                "SELECT * FROM o_persons " + "WHERE username = ?",
                (input_list["username"],),
            ).fetchall()


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


@user_api.route("/logout", methods=["POST", "GET"])
def user_logout():
    if request.method == "POST":  # Nothing to do
        pass
    elif request.method == "GET":  # Log Out
        session["logined_person_id"] = False
        return "Get Logout"


@user_api.route("/register", methods=["POST", "GET"])
def user_register():
    if request.method == "POST":  # User register, Return Status
        db = get_db()
        cur = db.cursor()
        input_list = request.form

        success = 1

        try:
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


@user_api.route("/info", methods=["POST", "GET"])
def user_info():
    if request.method == "POST":  # Change user info
        return "Change user info"
    elif request.method == "GET":  # Get User info
        return "Get user info"