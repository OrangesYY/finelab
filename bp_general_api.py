from flask import Blueprint, request, session, render_template
import json
from app_globals import bsnses, get_db, get_user_info_dict

general_api = Blueprint('general_api',__name__) 

# [Request] General API
@general_api.route("/target_insert", methods=["POST"])
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


@general_api.route("/target_update", methods=["POST"])
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
        query_sql_str = bsnses.createUpdateSQL(
            b_name,
            values_dict,
            filters_list=[],
            write_auth_role=user_info_dict.get("auth_role"),
            id=tar_id,
        )
        success = 1

        try:
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


@general_api.route("/target_delete", methods=["POST"])
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
    elif request.method == "GET":
        pass
