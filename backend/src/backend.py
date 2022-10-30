import asyncio
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
import requests
import databaseObject
import shutil
import _zqhf_oj_v2_spj

DATABASE = config.get("database-path")
db = None
lock = threading.Lock()
loadedContestDatabases = {}
loadedContestTasks = {}

event_loop = asyncio.new_event_loop()

waiting_tasks = []


def connect_db():
    global db
    db = sqlite3.connect(DATABASE, check_same_thread=False,
                         isolation_level=None)

    return db


def init_db():
    with closing(connect_db()) as db1:
        with open('sql/schema.sql', "r+") as f:
            db1.cursor().executescript(f.read())
        db1.commit()


def query_db(query, args=(), one=False):
    try:
        cur = db.execute(query, args)
    except Exception:
        pass
        
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv


def make_password_md5(password: str):
    return hashlib.md5(("__@zqhf-oj-reset-v2_" + "@" + password).encode('utf-8')).hexdigest()


def check_login(user: str, password: str):
    user_item = query_user_by_name(user)
    if user_item is None:
        return False
    return user_item['password'] == make_password_md5(password)


# 我他妈是个弱智
def register_user(user: str, password: str, permission_level: int = 0):
    query_db(
        '''insert into oj_users (username, password, introduction, full_introduction, ac_count, other_message) values 
        (?, ?, ?, ?, ?, ?)''',
        [user, make_password_md5(password), "", "", 0, pickle.dumps({
            "images_own": [],
            "files_own": [],
            "articles_own": [],
            # 0 is user, 1 is admin, 2 is super admin, -1 is banned user
            "permission_level": permission_level,
            "ac_problems": []
        })]
    )
    db.commit()


def query_user_by_name(user: str):
    return query_db("select * from oj_users where username = ?", [user], True)


def query_user_by_id(user: int):
    data = query_db('''
            select * from (
                select *,
                    rank () over ( 
                        order by ac_count desc
                    ) as ranking
                from oj_users
            ) where id = ?''', [user], True)
    data['other_message'] = pickle.loads(data['other_message'])
    return data


def query_user_by_id_min(user: int):
    data = query_db("select id, username, other_message from oj_users where id = ?", [user], True)
    data['other_message'] = pickle.loads(data['other_message'])
    data['other_message'] = {
        'permission_level': data['other_message']['permission_level']
    }
    return data


def query_user_by_id_simple(user: int):
    data = query_db("select * from oj_users where id = ?", [user], True)
    data['other_message'] = pickle.loads(data['other_message'])
    del data['password']
    del data['user_image']
    return data


def delete_user_by_name(user: str):
    return query_db("delete from oj_users where username = ?", [user], True)


def delete_user_by_id(user: int):
    return query_db("delete from oj_users where id = ?", [user], True)


def set_user_attr_by_name(user: str, attr_name: str, attr_val):
    return query_db("update oj_users set %s = ? where username = ?" % attr_name, [attr_val, user], True)


def set_user_attr_by_id(user: int, attr_name: str, attr_val):
    return query_db("update oj_users set %s = ? where id = ?" % attr_name, [attr_val, user], True)


def get_user_attr_by_id(user: int, attr_name: str):
    return query_db("select %s from oj_users where id = ?" % attr_name, [user], True)[attr_name]


def change_user_attrs(user: int, name: str, introduction: str, full_introduction: str):
    old_user_name = query_user_by_id(user)['username']
    set_user_attr_by_id(user, 'username', name)
    set_user_attr_by_id(user, 'introduction', introduction)
    set_user_attr_by_id(user, 'full_introduction', full_introduction)
    if old_user_name != name:
        query_db("update oj_problems set author = ? where author = ?",
                 [name, old_user_name], one=True)


def change_user_permission(user: int, new_level: int):
    message = query_user_by_id(user)['other_message']
    message['permission_level'] = new_level
    set_user_attr_by_id(user, 'other_message', pickle.dumps(message))


def change_user_password(user: int, password: str):
    set_user_attr_by_id(user, 'password', make_password_md5(password))


def query_records_by_swap(start: int, count: int, author: int = -1, problem: int = -1):
    data = []
    if author != -1:
        if problem != -1:
            data = query_db("select id, author, lang, problem, status, score from oj_records where author = ? and problem = ? order by id desc limit ? offset ?",
                        [author, problem, count, start])
        else:
            data = query_db("select id, author, lang, problem, status, score from oj_records where author = ? order by id desc limit ? offset ?",
                            [author, count, start])
    else:
        if problem != -1:
            data = query_db("select id, author, lang, problem, status, score from oj_records where problem = ? order by id desc limit ? offset ?",
                        [problem, count, start])
        else:
            data = query_db("select id, author, lang, problem, status, score from oj_records order by id desc limit ? offset ?",
                            [count, start])
            
    for i in data:
        i['author'] = query_user_by_id_min(i['author'])
    return data


def query_records_by_id(ident: int):
    data = query_db("select * from oj_records where id = ?", [ident], one=True)
    data['author'] = query_user_by_id_min(data['author'])
    return data


def query_bulletins_by_swap(start: int, count: int):
    data = query_db(
        "select time, name, id from oj_bulletins order by id limit ? offset ?", [count, start])
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
    query_db("insert into oj_bulletins (name, time, content) values (?, ?, ?)", [
        name, cur_time, content])
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


def query_rating(start: int, count: int):
    result = query_db(
        '''select username, id, ac_count, introduction, ranking, other_message from (
                select *,
                    rank () over ( 
                        order by ac_count desc
                    ) as ranking
                from oj_users
            ) limit ? offset ?''',
        [count, start])
    
    for i in result:
        i['other_message'] = {
            'permission_level': pickle.loads(i['other_message'])['permission_level']
        }

    return result


def search_problems(way: str, content: str):
    result = []
    if way == "by_id":
        result = query_db(
            "select id,author,name,description,tags from oj_problems where id = ?", [content])
    elif way == "by_author":
        result = query_db("select id,author,name,description,tags from oj_problems where author like ?", [
            "%" + content + "%"])
    elif way == "by_description":
        result = query_db("select id,author,name,description,tags from oj_problems where description like ?",
                          ["%" + json.dumps(content)[1:-1] + "%"])
    elif way == "by_tags":
        result = query_db("select id,author,name,description,tags from oj_problems where tags like ?",
                          ["%" + json.dumps(content)[1:-1] + "%"])
    return result


def post_problem(author: str, name: str, timeout: int, memory_limit: int, description: str = "", appear_time: int = 0,
                 tags: list = None, io_examples: list = None):
    if tags is None:
        tags = []
    if io_examples is None:
        io_examples = []
    query_db(
        "insert into oj_problems (name, description, examples, author, appear_time, tags, timeout, memory)"
        " values (?, ?, ?, ?, ?, ?, ?, ?)",
        [name, description, json.dumps(io_examples), author, appear_time, json.dumps(tags), timeout, memory_limit])

    return None


def edit_problem(pid: int, name: str, timeout: int, memory_limit: int, description: str = "", appear_time: int = 0,
                 tags: list = None,
                 io_examples: list = None, special_judge_code: str = ""):
    if tags is None:
        tags = []
    if io_examples is None:
        io_examples = []

    if query_problem_by_id(pid) is not None:
        query_db(
            "update oj_problems set name = ?, description = ?, examples = ?, tags = ?, timeout = ?, memory = ?, appear_time = ?"
            " where id = ?",
            [name, description, json.dumps(io_examples), json.dumps(tags), timeout, memory_limit, appear_time, pid])
        if special_judge_code != "" and special_judge_code is not None:
            query_db("update oj_problems set special_judge = true, special_judge_code = ? where id = ?",
                     [special_judge_code, pid])
        else:
            query_db("update oj_problems set special_judge = false where id = ?",
                     [pid])

        return True

    return False


def add_file_to_problem(pid: int, filename: str, data):
    if type(data) is bytes:
        data = data.decode('utf-8')
    if query_problem_by_id(pid) is not None:
        os.makedirs(config.get('uploads-path') +
                    "/problems_data/" + str(pid), exist_ok=True)
        with open(config.get('uploads-path') + "/problems_data/" + str(pid) + "/" + filename,
                  'w+') as file:
            file.write(data)
        return True
    else:
        return False


def add_in_checkpoint_to_problem(pid: int, checkpoint_name: str, input_data):
    if type(input_data) is bytes:
        input_data = input_data.decode('utf-8')
    if query_problem_by_id(pid) is not None:
        os.makedirs(config.get('uploads-path') +
                    "/problems_data/" + str(pid), exist_ok=True)
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
        os.makedirs(config.get('uploads-path') +
                    "/problems_data/" + str(pid), exist_ok=True)
        with open(config.get('uploads-path') + "/problems_data/" + str(pid) + "/" + checkpoint_name + '.out',
                  "w+") as file:
            file.write(output_data)
        return True
    else:
        return False
    
    
def get_in_checkpoint(pid: int, checkpoint_name: str):
    filename = config.get('uploads-path') + "/problems_data/" + str(pid) + "/" + checkpoint_name + '.in'
    if query_problem_by_id(pid) is not None:
        os.makedirs(config.get('uploads-path') +
                    "/problems_data/" + str(pid), exist_ok=True)
        
        if os.access(filename, os.F_OK):
            return filename
        return Exception("file not exist")
    else:
        raise Exception("problem not exist")


def get_out_checkpoint(pid: int, checkpoint_name: str):
    filename = config.get('uploads-path') + "/problems_data/" + str(pid) + "/" + checkpoint_name + '.out'
    if query_problem_by_id(pid) is not None:
        os.makedirs(config.get('uploads-path') +
                    "/problems_data/" + str(pid), exist_ok=True)
        
        if os.access(filename, os.F_OK):
            return filename
        return Exception("file not exist")
    else:
        raise Exception("problem not exist")


def remove_checkpoint_from_problem(pid: int, checkpoint_name: str):
    if os.access(config.get('uploads-path') + "/problems_data/" + str(pid) + "/" + checkpoint_name + '.in', os.F_OK):
        os.remove(config.get('uploads-path') + "/problems_data/" +
                  str(pid) + "/" + checkpoint_name + '.in')
    else:
        return False

    if os.access(config.get('uploads-path') + "/problems_data/" + str(pid) + "/" + checkpoint_name + '.out', os.F_OK):
        os.remove(config.get('uploads-path') + "/problems_data/" +
                  str(pid) + "/" + checkpoint_name + '.out')
    else:
        return False

    return True


def make_checkpoint_dir(pid: int):
    os.mkdir(config.get('uploads-path') + "/problems_data/" + str(pid))


def remove_checkpoint_dir(pid: int):
    shutil.rmtree(config.get('uploads-path') + "/problems_data/" + str(pid))


def get_checkpoint_list(pid: int):
    try:
        result = os.listdir(config.get('uploads-path') +
                            "/problems_data/" + str(pid))
    except:
        make_checkpoint_dir(pid)
        return []
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
        delete_comment_area('problem:' + str(pid))
        return True
    else:
        return False


def query_problem_by_id(ident: int):
    if query_comments_by_require('problem:' + str(ident)) is None:
        create_comment_area('problem:' + str(ident))

    data = query_db("select * from oj_problems where id = ?", [ident], one=True)
        
    return data


def query_problem_by_id_simple(ident: int):
    if query_comments_by_require('problem:' + str(ident)) is None:
        create_comment_area('problem:' + str(ident))

    data = query_db("select id, name, author, tags, appear_time from oj_problems where id = ?", [
        ident], one=True)
    
    if int(time.time()) >= data['appear_time']:
        data['tags'] = json.loads(data['tags'])
    else:
        data['tags'] = []
        
    return data


def query_problem_by_name(name: str):
    return query_db("select * from oj_problems where name = ?", [name])


def query_problem_by_swap(start: int, limit: int):
    data = query_db("select id, name, tags, author author, appear_time from oj_problems order by id limit ? offset ?",
                    [limit, start])
    for i in data:
        if int(time.time()) < i['appear_time']:
            i['tags'] = '[]'
            
    return data


def get_judge_server_info():
    data = json.loads(requests.get(
        f"http://{config.get('judge-server-address')}/info").content)
    data['address'] = config.get('judge-server-address')
    return data


def get_judge_machines():
    return judge.get_machine_list(config.get('judge-server-address'))


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


def submit_judge_free(data: json):
    return judge.submit(judge_server_address=config.get('judge-server-address'),
                        judge_plugin=data['plugin'],
                        source_file=data['source_file'],
                        data_input=data['input'],
                        data_output='',
                        env_variables=data['env_variables'],
                        time_limit=data['time_limit'],
                        mem_limit=data['mem_limit'])


def submit_judge_main(jid: int):
    record_content = query_records_by_id(jid)

    problem_content = query_problem_by_id(record_content['problem'])
    checkpoint_list = get_checkpoint_list(record_content['problem'])

    request_data = {
        'judge_type': 'spj' if problem_content['special_judge'] else 'text',
        'plugin': record_content['lang'],
        'source_file': record_content['code'],
        'time_limit': problem_content['timeout'],
        'mem_limit': problem_content['memory'],
        'spj_source': problem_content['special_judge_code'] if problem_content['special_judge'] else '',
        'tests': [],
    }
    
    request_files = {}

    for i in checkpoint_list:
        request_data['tests'].append([i + '.in', i + '.out'])
        
        request_files[i + '.in'] = (i + '.in', open(config.get('uploads-path') + "/problems_data/" + str(record_content['problem']) + "/" + i + '.in',
                      "rb+"), 'text/txt')
        request_files[i + '.out'] = (i + '.out', open(config.get('uploads-path') + "/problems_data/" + str(record_content['problem']) + "/" + i + '.out',
                      "rb+"), 'text/txt')
        
    request_files['json'] = ('json', json.dumps(request_data), 'application/json')
    
    response = judge.judge(config.get('judge-server-address'), request_files)
    
    query_db("update oj_records set status = ? where id = ?",
                 ['Accepted' if response['ac'] else 'Wrong answer', jid])
    
    query_db("update oj_records set points = ?, score = ? where id = ?",
                 [json.dumps(response['checkpoints']), response['score'], jid])
        


def run_judge_task(pid: int, author: int, code: str, lang: str):
    timestamp = int(time.time() * 100)
    jid = create_judge(pid, author, code, lang, timestamp)

    threading.Timer(0, submit_judge_main, (jid,)).start()

    return jid


def get_judge_jid(problem: int, author: int, timestamp: int):
    return query_db("select id from oj_records where problem = ? and author = ? and timestamp = ?",
                    [problem, author, timestamp], one=True)['id']


def query_problem_list_by_name(name: str):
    data = query_db(
        "select * from oj_problem_lists where name = ?", [name], one=True)
    if data is None:
        return data
    data['author'] = query_user_by_id_simple(data['author'])
    data['problems'] = json.loads(data['problems'])
    return data


def query_problem_list_by_id(ident: int):
    data = query_db(
        "select * from oj_problem_lists where id = ?", [ident], one=True)
    if data is None:
        return data
    data['author'] = query_user_by_id_simple(data['author'])
    data['problems'] = json.loads(data['problems'])
    for i in range(len(data['problems'])):
        data['problems'][i] = query_problem_by_id(data['problems'][i])
        data['problems'][i]['tags'] = json.loads(data['problems'][i]['tags'])

    if query_comments_by_require('problem_list:' + str(ident)) is None:
        create_comment_area('problem_list:' + str(ident))

    return data


def remove_problem_list_by_id(ident: int):
    data = query_db("delete from oj_problem_lists where id = ?", [
        ident], one=True)
    delete_comment_area('problem_list:' + str(ident))
    return data


def query_problem_list_by_swap(start: int, limit: int):
    data = query_db(
        "select id, author, name from oj_problem_lists order by id limit ? offset ?", [limit, start])
    for i in data:
        i['author'] = query_user_by_id_simple(i['author'])

    return data


def search_problem_list_by_problem(pid: int):
    data = query_db("select id, author, name from oj_problem_lists where problems like ? order by id",
                    [f'%{str(pid)}%'])
    for i in data:
        i['author'] = query_user_by_id_simple(i['author'])

    return data


def search_problem_list_by_description(words: str):
    data = query_db("select id, author, name from oj_problem_lists where description like ? order by id",
                    [f'%{words}%'])
    for i in data:
        i['author'] = query_user_by_id_simple(i['author'])

    return data


def search_problem_list_by_name(words: str):
    data = query_db("select id, author, name from oj_problem_lists where name like ? order by id",
                    [f'%{words}%'])
    for i in data:
        i['author'] = query_user_by_id_simple(i['author'])

    return data


def create_problem_list(author: int, name: str, description: str, problems: list):
    if query_problem_list_by_name(name) is not None:
        return False

    query_db("insert into oj_problem_lists (author, name, description, problems) values (?,?,?,?)",
             [author, name, description, json.dumps(problems)])

    list_id = query_db(
        "select id from oj_problem_lists where name=?", name, one=True)['id']
    create_comment_area('problem_list:' + str(list_id))

    return True


def edit_problem_list(author: int, ident: int, name: str, description: str, problems: list):
    if query_problem_list_by_id(ident) is None:
        return False

    query_db("update oj_problem_lists set name = ?, author = ?, description = ?, problems = ? where id = ?",
             [name, author, description, json.dumps(problems), ident])

    return True


def create_comment_area(create_by: str):
    query_db("insert into oj_comments (require_by, comments) values (?, ?)",
             [create_by, json.dumps([])])

    return {'code': 0, 'text': '操作成功'}


def delete_comment_area(require_by: str):
    query_db("delete from oj_comments where require_by = ?", [require_by])


def query_comments_by_require(require_by: str):
    comments = query_db(
        "select * from oj_comments where require_by = ?", [require_by], one=True)
    if comments is None:
        return None
    comments['comments'] = json.loads(comments['comments'])
    return comments


def insert_comment(require_by: str, author: id, text: str):
    comments = query_comments_by_require(require_by)
    if comments is None:
        return {'code': 4, 'text': '请求的评论区不存在'}

    comments['comments'].append({
        'author': author,
        'text': text,
        'reply': []
    })
    query_db("update oj_comments set comments = ? where require_by = ?",
             [json.dumps(comments['comments']), comments['require_by']])
    return {'code': 0, 'text': '操作成功'}


def get_comments_by_swap(require_by: str, start: int, count: int):
    try:
        data = query_comments_by_require(require_by)['comments']
        data = data[start: start + count]
        for i in range(len(data)):
            data[i]['author'] = query_user_by_id_simple(data[i]['author'])
            data[i]['index'] = i
            for j in range(len(data[i]['reply'])):
                data[i]['reply'][j]['author'] = query_user_by_id_simple(
                    data[i]['reply'][j]['author'])

        return {'code': 0, 'text': '操作成功', 'data': data}
    except Exception as e:
        # print(e)
        return {'code': 4, 'text': '请求的评论区不存在'}


def delete_comment(require_by: str, author: int, index: int):
    data = query_comments_by_require(require_by)
    if data is not None:
        data = data['comments']
        if index >= len(data):
            return {'code': 2, 'text': '请求的评论不存在'}
        # is author of this comment or it's super-administrator.
        if data[index]['author'] == author or query_user_by_id(author)['other_message']['permission_level'] == 2:
            del data[index]
            query_db("update oj_comments set comments = ? where require_by = ?",
                     [json.dumps(data), require_by])
            return {'code': 0, 'text': '操作成功'}
        else:
            return {'code': 1, 'text': '无法删除评论, 无法删除他人用户的评论'}
    else:
        return {'code': 2, 'text': '请求的评论区不存在'}


def reply_comment(require_by: str, index_of_comment: int, author: int, text: str):
    comments = query_comments_by_require(require_by)
    if comments is None:
        return {'code': 4, 'text': '请求的评论区不存在'}

    comments['comments'] = json.loads(comments['comments'])
    if len(comments['comments']) >= index_of_comment:
        return {'code': 4, 'text': '请求的评论不存在'}

    comments['comments']['reply'].append({
        'author': author,
        'text': text
    })

    comments['comments'] = json.dumps(comments['comments'])

    query_db('update oj_comments set comments = ? where require_by = ?', [
        comments['comments'], comments['author']])

    return {'code': 0, 'text': '操作成功'}


def query_articles_by_swap(start: int, count: int):
    data = query_db("select id, author, name from oj_articles where visible = true order by id desc limit  ? offset ?",
                    [count, start])
    for i in range(len(data)):
        data[i]['author'] = query_user_by_id_simple(data[i]['author'])

    return data


def query_article_by_id(ident: int, require: int):
    data = query_db("select * from oj_articles where id = ?",
                    [ident], one=True)
    if data is None:
        return {
            'code': 2,
            'text': '文章不存在'
        }
    data['author'] = query_user_by_id_simple(data['author'])
    if data['author']['id'] != require and not data['visible']:
        return {
            'code': 1,
            'text': '权限不足'
        }

    return {
        'code': 0,
        'text': '请求成功',
        'data': data
    }


def remove_article(ident: int, require: int):
    data = query_db("select author, visible from oj_articles where id = ?", [
        ident], one=True)
    if data is None:
        return {
            'code': 2,
            'text': '文章不存在'
        }

    if data['author'] == require or query_user_by_id_simple(require)['other_message']['permission_level'] == 2:
        query_db("delete from oj_articles where id = ?", [ident])
        return {
            'code': 0,
            'text': '请求成功'
        }
    else:
        return {
            'code': 1,
            'text': '权限不足'
        }


def create_article(name: str, text: str, author: int, visible: bool):
    query_db("insert into oj_articles (author, name, text, visible) values (?, ?, ?, ?)",
             [author, name, text, visible])

    create_comment_area(
        'article:' + str(query_db("select id from oj_articles order by id desc limit 1", one=True)['id']))


def edit_article(ident: int, name: str, text: str, author: int, visible: bool):
    data = query_db("select author, visible from oj_articles where id = ?", [
        ident], one=True)
    if data is None:
        return {
            'code': 2,
            'text': '文章不存在'
        }
    else:
        if data['author'] != author:
            return {
                'code': 1,
                'text': '无法对不是自己的文章进行编辑'
            }
        else:
            query_db("update oj_articles set name = ?, text = ?, visible = ?, author = ? where id = ?",
                     [name, text, visible, author, ident])
            return {
                'code': 0,
                'text': '请求成功!'
            }


def search_articles(word, way: str):
    data = []
    if way == 'by_text':
        data = query_db("select id, author, name from oj_articles where text like ? and visible = 1",
                        [f"%{word}%"])
    elif way == 'by_name':
        data = query_db("select id, author, name from oj_articles where name like ? and visible = 1",
                        [f"%{word}%"])
    elif way == 'by_author':
        data = query_db(
            "select id, author, name from oj_articles where author = %d and visible = 1" % int(word))

    for i in range(len(data)):
        data[i]['author'] = query_user_by_id_simple(data[i]['author'])

    return data


def query_articles_by_uid(uid: int):
    data = query_db(
        "select id, author, name, visible from oj_articles where author = %d" % uid)

    return {'code': 0, 'text': '请求成功', 'data': data}


def query_articles_by_swap_uid(uid: int, start: int, count: int):
    data = query_db("select id, author, name from oj_articles where author = ? order by id desc limit ? offset ?",
                    [uid, count, start])
    for i in range(len(data)):
        author = query_user_by_id_simple(data[i]['author'])
        data[i]['author'] = {
            'id': author['id'],
            'username': author['username']
        }

    return data


# 结束比赛后统计rating
def count_rating_after_contest(cid: int):
    print('Counting rating...')
    number = loadedContestDatabases[cid].query_db('select Count(*) as count from oj_contest_ranking', one=True)['count']
    count_per_page = 16
    current_page = 0
    data = query_contest_ranking_by_swap(cid, current_page, count_per_page)['data']
    while len(data) != 0:
        for i in data:
            author = i['uid']
            rank = i['ranking']
            rating_change = 0
            # 前 10% 加 50 分
            if rank <= int(number * 0.1):
                rating_change = 50
            # 前 25% 加 30 分
            elif rank <= int(number * 0.25):
                rating_change = 40
            # 前 50% 加 25 分
            elif rank <= int(number * 0.5):
                rating_change = 25

            set_user_attr_by_id(author, 'ac_count', get_user_attr_by_id(author, 'ac_count') + rating_change)

        current_page += 1
        data = query_contest_ranking_by_swap(cid, current_page, count_per_page)['data']


# 更改比赛可提交状态
def change_contest_joinable(cid: int, stat: bool):
    print('Event triggered')
    # 判断比赛是否已被删除
    if loadedContestDatabases.get(cid) is None:
        return

    if stat:
        query_db(
            "update oj_contests set joinable = ? where id = ?", [True, cid])
    else:
        print('Ending contest...')
        query_db("update oj_contests set joinable = ? where id = ?",
                 [False, cid])
        print('Executing scripts...')
        count_rating_after_contest(cid)
        loadedContestDatabases[cid].close()
        del loadedContestDatabases[cid]
        del loadedContestTasks[cid]


# 初始化比赛的定时任务
def initializeContestSchedules():
    data = query_db('''select id, start_timestamp, end_timestamp from oj_contests where end_timestamp >= ?''',
                    [int(time.time())])

    for i in data:
        if loadedContestDatabases.get(i['id']) is None:
            contests_dir = config.get('uploads-path') + '/contests/' + str(i['id'])
            if os.access(contests_dir, os.F_OK):
                loadedContestDatabases[i['id']] = databaseObject.connect(
                    contests_dir + '/contest.db')
                
        print('Event registered: contest_start, contest_end for ', i['id'])
        loadedContestTasks[i['id']] = [
            threading.Timer(i['start_timestamp'] - int(time.time()),
                            change_contest_joinable, (i['id'], True)),
            threading.Timer(i['end_timestamp'] - int(time.time()),
                            change_contest_joinable, (i['id'], False))
        ]
        
        if i['start_timestamp'] >= int(time.time()):
            loadedContestTasks[i['id']][0].start()
            
        loadedContestTasks[i['id']][1].start()


# 创建比赛
def create_contest(author_uid: str, contestName: str, contestDescription: str,
                   startTimestamp: int, endTimestamp: int, problems: list) -> dict:
    # 判断时间戳是否合法
    if startTimestamp < time.time() + 60 or endTimestamp < time.time() + 60 or endTimestamp < startTimestamp:
        return {'status': False, 'info': 'Invalid timestamp!', 'id': -1}

    query_db('''insert into oj_contests (author_uid, name, description, start_timestamp, end_timestamp, problems) values 
        (?, ?, ?, ?, ?, ?)''',
             [author_uid, contestName, contestDescription, startTimestamp, endTimestamp, json.dumps(problems)])

    data = query_db('''select id from oj_contests where author_uid = ? and name = ? and description = ? 
                        and start_timestamp = ? and end_timestamp = ? and problems = ?''',
                    [author_uid, contestName, contestDescription, startTimestamp, endTimestamp, json.dumps(problems)],
                    one=True)

    contests_dir = config.get('uploads-path') + '/contests/' + str(data['id'])

    os.makedirs(contests_dir)

    loadedContestDatabases[data['id']] = databaseObject.connect(
        contests_dir + "/contest.db")

    with open('sql/contestDatabaseInitialize.sql', "r+") as f:
        loadedContestDatabases[data['id']].databaseObject.executescript(f.read())

    loadedContestDatabases[data['id']].databaseObject.commit()

    loadedContestTasks[data['id']] = [
        threading.Timer(startTimestamp - int(time.time()),
                        change_contest_joinable, (data['id'], True)),
        threading.Timer(endTimestamp - time.time(),
                        change_contest_joinable, (data['id'], False))
    ]
    loadedContestTasks[data['id']][0].start()
    loadedContestTasks[data['id']][1].start()

    return {
        'status': True,
        'id': data['id']
    }


# 修改比赛
# Warning: 只可以在比赛开始之前更改
def edit_contest(cid: int, contestName: str, contestDescription: str,
                 startTimestamp: int, endTimestamp: int, problems: list) -> bool:
    data = query_db('''select * from oj_contests where id = ?''',
                    [cid], one=True)
    if data is None:
        return False
    else:
        if data['start_timestamp'] <= int(time.time()):
            return False
        else:
            if data['start_timestamp'] != startTimestamp:
                loadedContestTasks[cid][0].cancel()
                loadedContestTasks[cid][0] = \
                    threading.Timer(startTimestamp - int(time.time()),
                                    change_contest_joinable, (data['id'], True))
                loadedContestTasks[cid][0].start()

            if data['end_timestamp'] != endTimestamp:
                loadedContestTasks[cid][1].cancel()
                loadedContestTasks[cid][1] = \
                    threading.Timer(endTimestamp - int(time.time()),
                                    change_contest_joinable, (data['id'], False))
                loadedContestTasks[cid][1].start()

            query_db(
                "update oj_contests set name = ?, description = ?, start_timestamp = ?, end_timestamp = ?, problems = "
                "? where id = ?",
                [contestName, contestDescription, startTimestamp, endTimestamp, json.dumps(problems), cid], one=True)

            return True


# 删除比赛
def delete_contest(cid: int) -> bool:
    if query_contests_by_id(cid) is None:
        return False

    # 卸载数据库
    if loadedContestDatabases.get(cid) is not None:
        loadedContestDatabases[cid].close()
        del loadedContestDatabases[cid]

    if loadedContestTasks.get(cid) is not None:
        try:
            loadedContestTasks[cid][0].cancel()
        finally:
            pass

        try:
            loadedContestTasks[cid][1].cancel()
        finally:
            pass

        del loadedContestTasks[cid]

    # 删除比赛存放目录
    contests_dir = config.get('uploads-path') + '/contests/' + str(cid)

    shutil.rmtree(contests_dir)

    query_db("delete from oj_contests where id = ?", [cid])

    return True


# 根据比赛ID查询比赛详细信息
def query_contests_by_id(cid: int):
    data = query_db('''select * from oj_contests where id = ?''',
                    [cid], one=True)
    if data is not None:
        data['author'] = query_user_by_id_min(data['author_uid'])
        data['problems'] = json.loads(data['problems'])
        data['problems'] = [query_problem_by_id_simple(
            i) for i in data['problems']]

    return data


# 根据ID范围查询比赛简略信息
def query_contests_by_swap(start: int, count: int):
    data = query_db('''select id, author_uid, name, start_timestamp, end_timestamp, joinable 
                        from oj_contests order by id desc limit ? offset ?''',
                    [count, start])

    for i in data:
        i['author'] = query_user_by_id_min(i['author_uid'])

    return data


# 根据范围查询比赛排名
def query_contest_ranking_by_swap(cid: int, start: int, count: int):
    if loadedContestDatabases.get(cid) is None:
        contests_dir = config.get('uploads-path') + '/contests/' + str(cid)
        if os.access(contests_dir, os.F_OK):
            loadedContestDatabases[cid] = databaseObject.connect(
                contests_dir + '/contest.db')
        else:
            return {'status': False, 'info': 'Contest not exist!'}

    data = loadedContestDatabases[cid].query_db(
        '''
        select *,
            rank () over ( 
                order by final_score desc
            ) as ranking
        from oj_contest_ranking 
        limit ? offset ?
        ''',
        [count, start])

    for i in data:
        i['username'] = query_user_by_id_min(i['uid'])['username']
        i['scores'] = json.loads(i['scores'])

    return {'status': True, 'data': data}


# 根据UID查询比赛排名
def query_contest_ranking_by_uid(cid: int, uid: int):
    if loadedContestDatabases.get(cid) is None:
        contests_dir = config.get('uploads-path') + '/contests/' + str(cid)
        if os.access(contests_dir, os.F_OK):
            loadedContestDatabases[cid] = databaseObject.connect(
                contests_dir + '/contest.db')
        else:
            return {'status': False, 'info': 'Contest not exist!'}

    data = loadedContestDatabases[cid].query_db(
        '''
        select * from (
            select *,
                rank () over ( 
                    order by final_score desc
                ) as ranking
            from oj_contest_ranking
        ) where uid = ?
        ''',
        [uid],
        one=True)

    if data is None:
        return {'status': False, 'info': 'User did not participate in this contest!'}

    data['scores'] = json.loads(data['scores'])
    data['username'] = query_user_by_id_min(data['uid'])['username']

    return {'status': True, 'data': data}


# 查看用户是否已加入指定比赛
def is_user_joined_contest(cid: int, uid: int) -> bool:
    if loadedContestDatabases.get(cid) is None:
        contests_dir = config.get('uploads-path') + '/contests/' + str(cid)
        if os.access(contests_dir, os.F_OK):
            loadedContestDatabases[cid] = databaseObject.connect(
                contests_dir + '/contest.db')
        else:
            return False

    return \
        loadedContestDatabases[cid].query_db(
            "select * from oj_contest_ranking where uid = ?", [uid], one=True) is not None


# 加入比赛
def join_contest(cid: int, uid: int) -> dict:
    contest = query_contests_by_id(cid)
    if contest is None:
        return {'status': False, 'info': 'Contest not exist!'}
    if contest['end_timestamp'] <= int(time.time()):
        return {'status': False, 'info': 'Contest already ended!'}

    if is_user_joined_contest(cid, uid):
        return {'status': False, 'info': 'User already joined this contest!'}
    else:
        loadedContestDatabases[cid].query_db('''
                                            insert into oj_contest_ranking 
                                            (uid) values (?)
                                            ''',
                                             [uid])
        return {'status': True, 'info': 'Success!'}


# 查询比赛题目详细信息
def query_contest_problem_details(cid: int, tid: int) -> dict:
    contest = query_contests_by_id(cid)
    if contest is None:
        return {'status': False, 'info': 'Contest not exist!'}

    if int(time.time()) <= contest['start_timestamp'] or int(time.time()) > contest['end_timestamp']:
        return {'status': False, 'info': 'Contest has not started or has ended!'}

    if tid >= len(contest['problems']):
        return {'status': False, 'info': 'Invalid TID!'}

    return {'status': True, 'data': query_problem_by_id(contest['problems'][tid]['id'])}


# 更新比赛用户提交
def update_contest_user_score(cid: int, uid: int, scores: list, final_score: int):
    loadedContestDatabases[cid].query_db(
        "update oj_contest_ranking set scores = ?, final_score = ? where uid = ?",
        [json.dumps(scores), final_score, uid], one=True)


# 评测比赛题目代码 + 统分
def submit_to_contest_problem_helper(cid: int, tid: int, jid: int):
    submit_judge_main(jid)

    # 题目评测完毕 统计分数
    contest = query_contests_by_id(cid)
    record = query_records_by_id(jid)
    data = query_contest_ranking_by_uid(cid, record['author']['id'])
    data = data['data']

    if len(data['scores']) == 0:
        data['scores'] = [0 for _ in contest['problems']]

    data['scores'][tid] = record['score']

    data['final_score'] = 0
    for i in data['scores']:
        data['final_score'] += i

    update_contest_user_score(cid, record['author']['id'], data['scores'], data['final_score'])


# 提交比赛题目代码
def submit_to_contest_problem(cid: int, tid: int, author: int, code: str, lang: str):
    contest = query_contests_by_id(cid)
    if contest is None:
        return {'status': False, 'info': 'Contest not exist!'}

    if int(time.time()) <= contest['start_timestamp'] or int(time.time()) > contest['end_timestamp']:
        return {'status': False, 'info': 'Contest has not started or has ended!'}

    if tid >= len(contest['problems']):
        return {'status': False, 'info': 'Invalid TID!'}

    # 获取题号
    pid = contest['problems'][tid]['id']
    timestamp = int(time.time() * 100)

    judge_id = create_judge(pid, author, code, lang, timestamp)

    threading.Timer(0.1, submit_to_contest_problem_helper, (cid, tid, judge_id)).start()

    return {'status': True, 'data': judge_id}


def initialize_backend():
    connect_db()
    initializeContestSchedules()


initialize_backend()
