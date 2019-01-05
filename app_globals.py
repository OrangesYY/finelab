from flask import  g 
from finedb import DataFrame
import hashlib,sqlite3

bsnses = DataFrame("data/data_frame.json")

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


def get_user_info_dict(person_id):
    if person_id == 0 or person_id == None:
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

def pass_hash(in_string):
    md5 = hashlib.md5()
    md5.update((in_string + "nice_day").encode("utf-8"))
    return md5.hexdigest()

