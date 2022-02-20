import hashlib
import pickle
import sqlite3
from contextlib import closing
import time
import config

DATABASE = config.get("database-path")
db = None


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


def check_login(user: str, password: str):
    user_item = query_user_by_name(user)
    if user_item is None:
        return False
    return user_item['password'] == make_password_md5(user, password)


def register_user(user: str, password: str, permission_level: int = 1):
    query_db(
        '''insert into oj_users (username, password, introduction, full_introduction, ac_count, other_message) values 
        (?, ?, ?, ?, ?, ?)''',
        [user, make_password_md5(user, password), "", "", 0, pickle.dumps({
            "images_own": [],
            "files_own": [],
            "permission_level": permission_level  # 0 is user, 1 is admin, 2 is super admin, -1 is banned user
        })]
    )
    db.commit()


def query_user_by_name(user: str):
    return query_db("select * from oj_users where username = ?", [user], True)


def query_user_by_id(user: int):
    return query_db("select * from oj_users where id = ?", [user], True)


def delete_user_by_name(user: str):
    return query_db("delete from oj_users where username = ?", [user], True)


def delete_user_by_id(user: int):
    return query_db("delete from oj_users where id = ?", [user], True)


def set_user_attr_by_name(user: str, attr_name: str, attr_val):
    return query_db("update oj_users set %s = ? where username = ?" % attr_name, [attr_val, user], True)


def set_user_attr_by_id(user: int, attr_name: str, attr_val):
    return query_db("update oj_users set %s = ? where id = ?" % attr_name, [attr_val, user], True)


def query_bulletins_by_size(start: int, count: int):
    return query_db("select * from oj_bulletins order by id limit ? offset ?", [count, start])


def query_bulletins_by_name(name: str):
    return query_db("select * from oj_bulletins where name = ?", [name], one=True)


def query_bulletins_by_id(ident: int):
    return query_db("select * from oj_bulletins where id = ?", [ident], one=True)


def create_bulletin(name: str, content: str):
    if query_bulletins_by_name(name) is not None:
        return False

    cur_time = time.time()
    cur_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(cur_time))
    query_db("insert into oj_bulletins (name, time, content) values (?, ?, ?)", [name, cur_time, content])
    return True


def set_bulletin_by_name(sel_name: str, name: str, content: str):
    if query_bulletins_by_name(name) is None:
        return False
    cur_time = time.time()
    cur_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(cur_time))
    query_db("update oj_bulletins set name = ?, time = ?, content = ? where name = ?",
             [name, cur_time, content, sel_name])
    return True


def set_bulletin_by_id(sel_id: int, name: str, content: str):
    if query_bulletins_by_name(name) is None:
        return False
    cur_time = time.time()
    cur_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(cur_time))
    query_db("update oj_bulletins set name = ?, time = ?, content = ? where id = ?",
             [name, cur_time, content, sel_id])
    return True


def remove_bulletin_by_id(ident: int):
    if query_bulletins_by_id(ident) is None:
        return False
    query_db("delete from oj_bulletins where id = ?", [ident])
    return True


def remove_bulletin_by_name(name: str):
    if query_bulletins_by_name(name) is None:
        return False
    query_db("delete from oj_bulletins where name = ?", [name])
    return True


def query_ranking(start: int, count: int):
    return query_db("select * from main.oj_users order by ac_count limit ? offset ?", [count, start])
