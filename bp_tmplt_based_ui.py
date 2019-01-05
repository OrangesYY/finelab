from flask import Blueprint, request, session, render_template
import json
from app_globals import bsnses, get_db, get_user_info_dict

tmplt_based_ui = Blueprint('tmplt_based_ui',__name__) 


# [Request] Template Based UI
@tmplt_based_ui.route('/search', methods=["GET"])
def search():
    logined_person_id = session.get("logined_person_id")
    user_info_dict = get_user_info_dict(logined_person_id)

    db = get_db()
    cur = db.cursor()
    b_name = request.args.get("b_name")
    key_words = request.args.get("search_key_word")
    bsns_table_dict = bsnses.getFomatdDict(b_name)
    filters_list = []
    if key_words != None:
        for item in bsns_table_dict['$SFLD']:
            _filter = {}
            _filter['left'] = item
            _filter['type'] = 'LIKE'
            _filter['right'] = '%'+key_words+'%'
            filters_list.append(_filter.copy())

    query_sql_str = bsnses.createQuerySQL(
        b_name, 
        read_auth_role=user_info_dict.get("auth_role"), 
        filters_list=filters_list
    )
    query_result = cur.execute(query_sql_str).fetchall()
    cur.close()

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
    
    return render_template(
        "search.htm",
        user_info_dict=user_info_dict,
        bsns_table_dict=bsns_table_dict,
        query_result=query_result,
    )




@tmplt_based_ui.route("/user_register_form", methods=["GET"])
def t_base_register_form():
    logined_person_id = session.get("logined_person_id")
    user_info_dict = get_user_info_dict(logined_person_id)
    return render_template("user_register_form.htm", user_info_dict=user_info_dict)


@tmplt_based_ui.route("/user_login_form", methods=["GET"])
def t_base_login_form():
    logined_person_id = session.get("logined_person_id")
    user_info_dict = get_user_info_dict(logined_person_id)
    return render_template("user_login_form.htm", user_info_dict=user_info_dict)


@tmplt_based_ui.route("/user_logout", methods=["GET"])
def t_base_logout():
    session["logined_person_id"] = False
    logined_person_id = session.get("logined_person_id")
    user_info_dict = get_user_info_dict(logined_person_id)
    return render_template("user_logout.htm", user_info_dict=user_info_dict)



@tmplt_based_ui.route("/target_scope", methods=["GET"])
def t_base_target_scope():
    logined_person_id = session.get("logined_person_id")
    user_info_dict = get_user_info_dict(logined_person_id)
    print("before call")
    db = get_db()
    print("after call")
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
    #print(query_sql_str)  # debug
    #print(query_result)  # debug
    cur.close()
    return render_template(
        "target_scope.htm",
        user_info_dict=user_info_dict,
        bsns_table_dict=bsns_table_dict,
        query_result=query_result,
    )


@tmplt_based_ui.route("/target_insert_form", methods=["GET"])
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


@tmplt_based_ui.route("/target_update_form", methods=["GET"])
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


@tmplt_based_ui.route("/pdf_tag_gen_form", methods=["GET"])
def t_base_pdf_tag_gen_form():
    logined_person_id = session.get("logined_person_id")
    user_info_dict = get_user_info_dict(logined_person_id)

    db = get_db()
    cur = db.cursor()
    b_name = request.args.get("b_name")  # business name
    tmpl_id = request.args.get("tmpl_id")

    templates_query_sql_str = "SELECT * FROM 'o_pdf_tag_templates'"
    templates_query_result = cur.execute(templates_query_sql_str).fetchall()


    if b_name != None:
        data_query_sql_str = bsnses.createQuerySQL(
            b_name, read_auth_role="tourist", filters_list=[]
        )
        data_query_result = cur.execute(data_query_sql_str).fetchall()
        data_json_string = json.dumps(data_query_result,indent=4,ensure_ascii=False)
    else:
        data_json_string = ""
    
    if tmpl_id != None:
        template_query_sql_str = "SELECT * FROM 'o_pdf_tag_templates' WHERE template_id = %s"%(tmpl_id,)
        template_query_result = cur.execute(template_query_sql_str).fetchall()
        tmpl_str = template_query_result[0]['json_content']
    else:
        tmpl_str = ""

    return render_template(
        "pdf_tag_gen_form.htm", 
        user_info_dict=user_info_dict,
        data_json_string = data_json_string, 
        tmpl_str = tmpl_str,
        templates_query_result = templates_query_result  # for selection
    )


@tmplt_based_ui.route("/debug/view_table", methods=["GET"])
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
