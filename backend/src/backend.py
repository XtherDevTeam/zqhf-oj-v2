import hashlib
import json
import os
import pickle
import sqlite3
import threading
from contextlib import closing
import time
import config
import judge

DATABASE = config.get("database-path")
db = None
lock = threading.Lock()


def connect_db():
    global db
    db = sqlite3.connect(DATABASE, check_same_thread=False, isolation_level=None)
    return db


def init_db():
    with closing(connect_db()) as db1:
        with open('schema.sql', "r+") as f:
            db1.cursor().executescript(f.read())
        db1.commit()


def query_db(query, args=(), one=False):
    lock.acquire()
    cur = db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    db.commit()
    lock.release()
    return (rv[0] if rv else None) if one else rv


def make_password_md5(password: str):
    return hashlib.md5(("__@zqhf-oj-reset-v2_" + "@" + password).encode('utf-8')).hexdigest()


def check_login(user: str, password: str):
    user_item = query_user_by_name(user)
    if user_item is None:
        return False
    return user_item['password'] == make_password_md5(password)


def register_user(user: str, password: str, permission_level: int = 0):
    query_db(
        '''insert into oj_users (username, password, introduction, full_introduction, ac_count, other_message) values 
        (?, ?, ?, ?, ?, ?)''',
        [user, make_password_md5(password), "", "", 0, pickle.dumps({
            "images_own": [],
            "files_own": [],
            "permission_level": permission_level,  # 0 is user, 1 is admin, 2 is super admin, -1 is banned user
            "ac_problems": []
        })]
    )
    db.commit()


def query_user_by_name(user: str):
    return query_db("select * from oj_users where username = ?", [user], True)


def query_user_by_id(user: int):
    data = query_db("select * from oj_users where id = ?", [user], True)
    data['other_message'] = pickle.loads(data['other_message'])
    return data


def delete_user_by_name(user: str):
    data = query_db("select * from oj_users where username = ?", [user], True)
    data['other_message'] = pickle.loads(data['other_message'])
    return data


def delete_user_by_id(user: int):
    return query_db("delete from oj_users where id = ?", [user], True)


def set_user_attr_by_name(user: str, attr_name: str, attr_val):
    return query_db("update oj_users set %s = ? where username = ?" % attr_name, [attr_val, user], True)


def set_user_attr_by_id(user: int, attr_name: str, attr_val):
    return query_db("update oj_users set %s = ? where id = ?" % attr_name, [attr_val, user], True)


def change_user_attrs(user: int, name: str, introduction: str, full_introduction: str):
    old_user_name = query_user_by_id(user)['username']
    set_user_attr_by_id(user, 'username', name)
    set_user_attr_by_id(user, 'introduction', introduction)
    set_user_attr_by_id(user, 'full_introduction', full_introduction)
    if old_user_name !Ï= name:
        query_db("update oj_problems set author = ? where author = ?", name, old_user_name)


def change_user_password(user: int, password: str):
    set_user_attr_by_id(user, 'password', make_password_md5(password))


def query_records_by_size(start: int, count: int):
    data = query_db("select id, author, lang, problem, status, score from oj_records order by id desc limit ? offset ?",
                    [count, start])
    return data


def query_records_by_id(ident: int):
    return query_db("select * from oj_records where id = ?", [ident], one=True)


def query_bulletins_by_size(start: int, count: int):
    data = query_db("select time, name, id from oj_bulletins order by id limit ? offset ?", [count, start])
    return data


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
    if query_bulletins_by_id(sel_id) is None:
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
    result = query_db(
        "select username, id, ac_count, introduction from oj_users order by ac_count desc limit ? offset ?",
        [count, start])

    return result


def search_problems(way: str, content: str):
    result = []
    if way == "by_id":
        result = query_db("select id,name,description,tags from oj_problems where id = ?", [content])
    elif way == "by_author":
        result = query_db("select id,name,description,tags from oj_problems where author like ?", ["%" + content + "%"])
    elif way == "by_description":
        result = query_db("select id,name,description,tags from oj_problems where description like ?",
                          ["%" + json.dumps(content)[1:-1] + "%"])
    elif way == "by_tags":
        result = query_db("select id,name,description,tags from oj_problems where tags like ?",
                          ["%" + json.dumps(content)[1:-1] + "%"])
    return result


def post_problem(author: str, name: str, timeout: int, memory_limit: int, description: str = "", tags: list = None,
                 io_examples: list = None):
    if tags is None:
        tags = []
    if io_examples is None:
        io_examples = []
    query_db(
        "insert into oj_problems (name, description, examples, author, tags, timeout, memory)"
        " values (?, ?, ?, ?, ?, ?, ?)",
        [name, description, json.dumps(io_examples), author, json.dumps(tags), timeout, memory_limit])

    last = query_db("select id from oj_problems where name = ?", [name], one=True)
    make_checkpoint_dir(last['id'])
    return None


def edit_problem(pid: int, name: str, timeout: int, memory_limit: int, description: str = "", tags: list = None,
                 io_examples: list = None):
    if tags is None:
        tags = []
    if io_examples is None:
        io_examples = []

    if query_problem_by_id(pid) is not None:
        query_db("update oj_problems set name = ?, description = ?, examples = ?, tags = ?, timeout = ?, memory = ?"
                 " where id = ?",
                 [name, description, json.dumps(io_examples), json.dumps(tags), timeout, memory_limit, pid])
        return True
    return False


def add_in_checkpoint_to_problem(pid: int, checkpoint_name: str, input_data):
    if type(input_data) == bytes:
        input_data = input_data.decode('utf-8')
    if query_problem_by_id(pid) is not None:
        with open(config.get('uploads-path') + "/problems_data/" + str(pid) + "/" + checkpoint_name + '.in',
                  'w+') as file:
            file.write(input_data)
        return True
    else:
        return False


def add_out_checkpoint_to_problem(pid: int, checkpoint_name: str, output_data):
    if type(output_data) == bytes:
        output_data = output_data.decode('utf-8')
    if query_problem_by_id(pid) is not None:
        with open(config.get('uploads-path') + "/problems_data/" + str(pid) + "/" + checkpoint_name + '.out',
                  "w+") as file:
            file.write(output_data)
        return True
    else:
        return False


def remove_checkpoint_from_problem(pid: int, checkpoint_name: str):
    if os.access(config.get('uploads-path') + "/problems_data/" + str(pid) + "/" + checkpoint_name + '.in', os.F_OK):
        os.remove(config.get('uploads-path') + "/problems_data/" + str(pid) + "/" + checkpoint_name + '.in')
    else:
        return False

    if os.access(config.get('uploads-path') + "/problems_data/" + str(pid) + "/" + checkpoint_name + '.out', os.F_OK):
        os.remove(config.get('uploads-path') + "/problems_data/" + str(pid) + "/" + checkpoint_name + '.out')
    else:
        return False

    return True


def make_checkpoint_dir(pid: int):
    os.mkdir(config.get('uploads-path') + "/problems_data/" + str(pid))


def remove_checkpoint_dir(pid: int):
    os.removedirs(config.get('uploads-path') + "/problems_data/" + str(pid))


def get_checkpoint_list(pid: int):
    result = os.listdir(config.get('uploads-path') + "/problems_data/" + str(pid))
    new_result = []
    for i in result:
        if i.endswith('.out'):
            new_result.append(i[0: -4])
        else:
            pass

    return new_result


def delete_problem(pid: int):
    if query_problem_by_id(pid) is not None:
        query_db("delete from oj_problems where id = ?", [pid])
        remove_checkpoint_dir(pid)
        return True
    else:
        return False


def query_problem_by_id(ident: int):
    return query_db("select * from oj_problems where id = ?", [ident], one=True)


def query_problem_by_name(name: str):
    return query_db("select * from oj_problems where name = ?", [name])


def query_problem_by_size(start: int, limit: int):
    return query_db("select id, name, tags, author from oj_problems order by id limit ? offset ?", [limit, start])


def get_judge_server_info():
    return {
        'address': config.get('judge-server-address'),
        'support-languages': config.get('judge-sever-support-language'),
        'support-language-exts': config.get('judge-server-language-exts'),
        'support-language-highlight-mode': config.get('judge-server-language-highlight-mode')
    }


def create_judge(problem: int, author: int, code: str, lang: str, timestamp: int):
    query_db(
        "insert into oj_records (author, code, lang, problem, timestamp, status, score) VALUES "
        "(?, ?, ?, ?, ?, 'Judging...', 0)",
        [author, code, lang, problem, timestamp])
    jid = \
        query_db(
            "select id from oj_records where author = ? and code = ? and lang = ? and problem = ? and timestamp = ?",
            [author, code, lang, problem, timestamp], one=True)['id']
    return jid


def submit_judge_main(jid: int, author: int, problem: int, code: str, lang: str, timestamp: int):
    problem_content = query_problem_by_id(problem)
    checkpoint_list = get_checkpoint_list(problem)
    checkpoint_status = []
    score = 0
    full_ac = True

    env_vars = {
        'source_file': 'temp.' + config.get('judge-server-language-exts')[lang],
        'binary_file': 'temp.bin'
    }

    for i in checkpoint_list:
        datas = ["", ""]
        with open(config.get('uploads-path') + "/problems_data/" + str(problem) + "/" + i + '.in',
                  "r+") as file:
            datas[0] = file.read()
        with open(config.get('uploads-path') + "/problems_data/" + str(problem) + "/" + i + '.out',
                  "r+") as file:
            datas[1] = file.read()
        checkpoint_status.append(judge.submit(
            judge_server_address=config.get('judge-server-address'),
            judge_plugin=lang,
            source_file=code,
            data_input=datas[0],
            data_output=datas[1],
            time_limit=problem_content['timeout'],
            mem_limit=problem_content['memory'],
            env_variables=env_vars
        ))
        if checkpoint_status[-1]['status'] != 'Accepted':
            full_ac = False
        else:
            score = score + 100 * (1 / len(checkpoint_list))
        query_db("update oj_records set points = ?, score = ? where id = ?",
                 [json.dumps(checkpoint_status), score, jid])

    if full_ac:
        other_message = query_user_by_id(author)['other_message']
        if not other_message['ac_problems'].count(problem):
            ac_count = query_user_by_id(author)['ac_count'] + 1
            other_message['ac_problems'].append(problem)
            set_user_attr_by_id(author, 'ac_count', ac_count)
            set_user_attr_by_id(author, 'other_message', pickle.dumps(other_message))
        query_db("update oj_records set status = 'Accepted' where id = ?", [jid])
    else:
        query_db("update oj_records set status = 'Wrong answer' where id = ?", [jid])

    return True


def get_judge_jid(problem: int, author: int, timestamp: int):
    return query_db("select id from oj_records where problem = ? and author = ? and timestamp = ?",
                    [problem, author, timestamp], one=True)['id']


def query_problem_list_by_name(name: str):
    data = query_db("select * from oj_problem_lists where name = ?", [name], one=True)
    if data is None:
        return data
    data['author'] = query_user_by_id(data['author'])
    data['problems'] = json.loads(data['problems'])
    return data


def query_problem_list_by_id(ident: int):
    data = query_db("select * from oj_problem_lists where id = ?", [ident], one=True)
    if data is None:
        return data
    data['author'] = query_user_by_id(data['author'])
    data['problems'] = json.loads(data['problems'])
    for i in range(len(data['problems'])):
        data['problems'][i] = query_problem_by_id(data['problems'][i])

    return data


def remove_problem_list_by_id(ident: int):
    data = query_db("delete from oj_problem_lists where id = ?", [ident], one=True)
    return data


def query_problem_list_by_size(start: int, limit: int):
    data = query_db("select id, author, name from oj_problem_lists order by id limit ? offset ?", [limit, start])
    for i in data:
        i['author'] = query_user_by_id(i['author'])

    return data


def search_problem_list_by_problem(pid: int):
    data = query_db("select id, author, name from oj_problem_lists where problems like ? order by id",
                    [f'%{str(pid)}%'])
    for i in data:
        i['author'] = query_user_by_id(i['author'])

    return data


def search_problem_list_by_description(words: str):
    data = query_db("select id, author, name from oj_problem_lists where description like ? order by id",
                    [f'%{words}%'])
    for i in data:
        i['author'] = query_user_by_id(i['author'])

    return data


def search_problem_list_by_name(words: str):
    data = query_db("select id, author, name from oj_problem_lists where name like ? order by id",
                    [f'%{words}%'])
    for i in data:
        i['author'] = query_user_by_id(i['author'])

    return data


def create_problem_list(author: int, name: str, description: str, problems: list):
    if query_problem_list_by_name(name) is not None:
        return False

    query_db("insert into oj_problem_lists (author, name, description, problems) values (?,?,?,?)",
             [author, name, description, json.dumps(problems)])
    return True


def edit_problem_list(author: int, ident: int, name: str, description: str, problems: list):
    if query_problem_list_by_id(ident) is None:
        return False

    query_db("update oj_problem_lists set name = ?, author = ?, description = ?, problems = ? where id = ?",
             [name, author, description, json.dumps(problems), ident])

    return True
