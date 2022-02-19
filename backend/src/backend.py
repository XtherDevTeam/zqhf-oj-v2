import hashlib
import sqlite3
from contextlib import closing

import config

DATABASE = config.get("database-path")
db = sqlite3.Connection()


def connect_db():
    global db
    db = sqlite3.connect(DATABASE)
    return db


def init_db():
    with closing(connect_db()) as db1:
        with open('schema.sql', "r+") as f:
            db1.cursor().executescript(f.read())
        db1.commit()


def query_db(query, args=(), one=False):
    cur = db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv


def make_password_md5(user: str, password: str):
    return hashlib.md5(("__@zqhf-oj-reset-v2_" + user + "@" + password).encode('utf-8')).hexdigest()


def register_user(user: str, password: str):
    query_db(
        '''insert into oj_users (username, password, introduction, full_introduction) values (?, ?, ?, ?)''',
        [user, make_password_md5(user, password), "", ""]
    )
    db.commit()


def query_user_by_name(user: str):
    return query_db("select * from oj_users where username = ?", [user], True)


def query_user_by_id(user: int):
    return query_db("select * from oj_users where id = ?", [user], True)


def delete_user_by_name(user: str):
    return query_db("delete * from oj_users where username = ?", [user], True)


def delete_user_by_id(user: int):
    return query_db("delete * from oj_users where id = ?", [user], True)


def set_user_attr_by_name(user: str, attr_name: str, attr_val):
    return query_db("update oj_users set %s = ? where username = ?" % attr_name, [attr_val, user], True)


def set_user_attr_by_id(user: int, attr_name: str, attr_val):
    return query_db("update oj_users set %s = ? where id = ?" % attr_name, [attr_val, user], True)
