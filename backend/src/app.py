import io
import json
import threading
import time

import flask
from flask_cors import CORS

import backend
import config

app = flask.Flask(__name__)
app.secret_key = '__@zqhf-oj-v2-secret-code'

CORS(app, resources=r'/*')


def is_logged_in():
    return flask.session.get('user_id') is not None


def get_login_details():
    return backend.query_user_by_id(flask.session.get('user_id'))


def require_admin_permission():
    if not is_logged_in():
        return {'code': 7, 'text': '用户未登录!'}
    # is not administrator or super-administrator
    if get_login_details()['other_message']['permission_level'] < 1:
        return {'code': 1, 'text': '权限不足!'}
    return True


@app.before_request
def before_request():
    backend.db = backend.connect_db()


@app.route("/", methods=['GET'])
def root_router():
    return {"code": 0, "text": "API服务状态正常!"}


@app.route("/v1/judge/info", methods=['GET'])
def judge_server_info_router():
    return {"code": 0, "text": "请求成功!", "data": backend.get_judge_server_info()}


@app.route("/v1/judge/get/<int:start>/<int:limit>", methods=['GET'])
def judge_record_get_by_swap_router(start, limit):
    return {
        'code': 0,
        'text': '操作成功!',
        'data': backend.query_records_by_size(start, limit)
    }


@app.route("/v1/judge/get/<int:ident>", methods=['GET'])
def judge_record_get_by_id_router(ident):
    result = backend.query_records_by_id(ident)
    result['points'] = json.loads(result['points'])
    if result is None:
        return {
            'code': 2,
            'text': '请求的评测编号不存在!'
        }
    else:
        return {
            'code': 0,
            'text': '操作成功!',
            'data': result
        }


@app.route("/v1/user/register/<username>/<password>", methods=['POST'])
def register_router(username, password):
    if backend.query_user_by_name(username) is not None:
        return {"code": 3, "text": "用户已存在!"}
    backend.register_user(username, password)
    return {"code": 0, "text": "注册成功!"}


@app.route("/v1/user/login/<username>/<password>", methods=['POST'])
def login_router(username, password):
    if backend.query_user_by_name(username) is None:
        return {"code": 2, "text": "用户不存在!"}
    if backend.check_login(username, password):
        flask.session['user_id'] = backend.query_user_by_name(username)['id']
        return {"code": 0, "text": "登陆成功!"}
    else:
        return {"code": 6, "text": "用户名或密码错误!"}


@app.route("/v1/user/change_password", methods=['POST'])
def change_password_router():
    if flask.session.get('user_id') is not None:
        request = flask.request.get_json()
        if request.get('old_password') is None:
            return {"code": 5, "text": "缺少参数: 旧密码!"}
        if request.get('new_password') is None:
            return {"code": 5, "text": "缺少参数: 新密码!"}
        if backend.check_login(backend.query_user_by_id(flask.session.get('user_id'))['username'],
                               request.get('old_password')):
            backend.change_user_password(flask.session.get('user_id'), request.get('new_password'))
            return {"code": 0, "text": "修改成功!"}
        else:
            return {"code": 6, "text": "用户名或密码错误!"}
    else:
        return {"code": 7, "text": "用户未登录!"}


@app.route('/v1/user/logout', methods=['GET'])
def logout_router():
    if flask.session.get('user_id') is not None:
        del flask.session['user_id']
        return {"code": 0, "text": "登出成功!"}
    return {"code": 7, "text": "用户未登录!"}


@app.route("/v1/user/change_info", methods=['POST'])
def user_info_change_router():
    if flask.session.get('user_id') is not None:
        request = flask.request.get_json()
        if request.get('username') is None:
            return {"code": 5, "text": "缺少用户名!"}
        if request.get('introduction') is None:
            return {"code": 5, "text": "缺少用户简介!"}
        if request.get('full_introduction') is None:
            return {"code": 5, "text": "缺少用户长介绍!"}
        backend.change_user_attrs(flask.session.get('user_id'), request.get('username'),
                                  request.get('introduction'), request.get('full_introduction'))
        return {"code": 0, "text": "操作成功!"}
    else:
        return {"code": 7, "text": "用户未登录!"}


@app.route("/v1/user/details", methods=['GET'])
def user_detail_router():
    ident = flask.request.args.get('username')
    if ident is None:
        ident = flask.request.args.get('user_id')
        if ident is None:
            if flask.session.get('user_id') is None:
                return {"code": 7, "text": "用户未登录!"}
            result = backend.query_user_by_id(flask.session['user_id'])
            del result['password']
            return {
                'code': 0,
                'text': '请求成功',
                'data': result
            }
        else:
            result = backend.query_user_by_id(int(ident))
            if result is None:
                return {"code": 2, "text": "用户不存在!"}
            result['other_message'] = {
                'permission_level': result['other_message']['permission_level']
            }
            del result['password']
            return {
                'code': 0,
                'text': '请求成功',
                'data': result
            }
    else:
        if ident.startswith('"'):
            ident = ident[1:-1]
        result = backend.query_user_by_name(ident)
        if result is None:
            return {"code": 2, "text": "用户不存在!"}
        del result['password']
        del result['other_message']
        return {
            'code': 0,
            'text': '请求成功',
            'data': result
        }


@app.route("/v1/problem_lists/get/<int:start>/<int:limit>", methods=['GET'])
def problem_lists_get_by_swap_router(start, limit):
    return {
        'code': 0,
        'text': '操作成功!',
        'data': backend.query_problem_list_by_size(start, limit)
    }


@app.route("/v1/problem_lists/get/<int:ident>", methods=['GET'])
def problem_lists_get_by_id_router(ident):
    result = backend.query_problem_list_by_id(ident)
    if result is None:
        return {
            'code': 2,
            'text': '请求的题单编号不存在!'
        }
    else:
        return {
            'code': 0,
            'text': '操作成功!',
            'data': result
        }


@app.route("/v1/problem_lists/post", methods=['POST'])
def problem_lists_post_router():
    require_admin = require_admin_permission()
    if require_admin is not True:
        return require_admin

    data = flask.request.get_json()
    if backend.create_problem_list(flask.session.get('user_id'), data['name'], data['description'], []):
        return {'code': 0, 'text': '请求成功!'}
    else:
        return {'code': 5, 'text': '具有相同名称的题单已存在!'}


@app.route("/v1/problem_lists/edit/<int:pid>", methods=['POST'])
def problem_lists_edit_router(pid: int):
    require_admin = require_admin_permission()
    if require_admin is not True:
        return require_admin

    data = flask.request.get_json()
    if backend.edit_problem_list(flask.session.get('user_id'), pid, data['name'], data['description'],
                                 data['problems']):
        return {'code': 0, 'text': '请求成功!'}
    else:
        return {'code': 3, 'text': '将要修改的题单不存在!'}


@app.route("/v1/bulletins/get/<int:start>/<int:count>", methods=['GET'])
def bulletins_get_by_size_router(start, count):
    return {
        'code': 0,
        'text': '请求成功',
        'data': backend.query_bulletins_by_size(start, count)
    }


@app.route("/v1/bulletins/get/<int:ident>", methods=['GET'])
def bulletins_get_by_id_router(ident):
    return {
        'code': 0,
        'text': '请求成功',
        'data': backend.query_bulletins_by_id(ident)
    }


@app.route("/v1/bulletins/post", methods=['POST'])
def bulletin_post_router():
    require_admin = require_admin_permission()
    if require_admin is not True:
        return require_admin

    data = flask.request.get_json()
    if backend.create_bulletin(data['name'], data['content']):
        return {'code': 0, 'text': '请求成功!'}
    else:
        return {'code': 3, 'text': '具有相同公告标题的公告已存在!'}


@app.route("/v1/bulletins/edit/<int:ident>", methods=['POST'])
def bulletin_edit_router(ident: int):
    require_admin = require_admin_permission()
    if require_admin is not True:
        return require_admin

    data = flask.request.get_json()
    print(data)
    if backend.set_bulletin_by_id(ident, data['name'], data['content']):
        return {'code': 0, 'text': '请求成功!'}
    else:
        return {'code': 2, 'text': '将要修改的公告不存在!'}


@app.route("/v1/bulletins/delete/<int:ident>", methods=['POST'])
def bulletin_remove_router(ident: int):
    require_admin = require_admin_permission()
    if require_admin is not True:
        return require_admin

    backend.remove_bulletin_by_id(ident)
    return {'code': 0, 'text': '请求成功!'}


@app.route("/v1/ranking/get", methods=['GET'])
def ranking_get_10th_router():
    return {
        'code': 0,
        'text': '请求成功',
        'data': backend.query_ranking(0, 10)
    }


@app.route("/v1/ranking/get/<int:start>/<int:count>", methods=['GET'])
def ranking_get_router(start, count):
    return {
        'code': 0,
        'text': '请求成功',
        'data': backend.query_ranking(start, count)
    }


@app.route("/v1/problems/<int:ident>/judge/submit", methods=['POST'])
def judge_submit_router(ident):
    if flask.session.get("user_id") is None:
        return {"code": 7, "text": "用户未登录!"}

    request = flask.request.get_json()
    if request.get('code') is None:
        return {
            'code': 5,
            'text': '表单缺少代码文本参数'
        }
    if request.get('lang') is None:
        return {
            'code': 5,
            'text': '表单缺少代码语言参数'
        }

    timestamp = int(time.time() * 100)

    jid = backend.create_judge(ident, flask.session['user_id'], request['code'],
                               request['lang'], timestamp)

    th = threading.Thread(target=backend.submit_judge_main,
                          args=(jid, flask.session['user_id'], ident, request['code'], request['lang'], timestamp))
    th.start()
    time.sleep(0.1)

    return {
        'code': 0,
        'text': '提交评测成功!',
        'data': backend.get_judge_jid(ident, flask.session['user_id'], timestamp)
    }


@app.route("/v1/problems/get/<int:start>/<int:count>", methods=['GET'])
def problems_get_size_router(start, count):
    return {
        'code': 0,
        'text': '请求成功',
        'data': backend.query_problem_by_size(start, count)
    }


@app.route("/v1/problems/get/<int:ident>", methods=['GET'])
def problems_get_id_router(ident):
    return {
        'code': 0,
        'text': '请求成功',
        'data': backend.query_problem_by_id(ident)
    }


@app.route("/v1/problems/delete/<int:ident>", methods=['POST'])
def problems_remove_router(ident):
    require_admin = require_admin_permission()
    if require_admin is not True:
        return require_admin

    if backend.delete_problem(ident):
        return {
            'code': 0,
            'text': '请求成功'
        }
    else:
        return {
            'code': 2,
            'text': '将要删除的题目不存在！'
        }


@app.route("/v1/problems/edit/<int:ident>", methods=['POST'])
def problem_edit_router(ident: int):
    require_admin = require_admin_permission()
    if require_admin is not True:
        return require_admin

    request = flask.request.get_json()
    if request.get('name') is None:
        return {
            'code': 5,
            'text': '表单缺少题目名称参数'
        }
    if request.get('description') is None:
        return {
            'code': 5,
            'text': '表单缺少题目描述参数'
        }
    if request.get('tags') is None:
        return {
            'code': 5,
            'text': '表单缺少题目标签参数'
        }
    if request.get('examples') is None:
        return {
            'code': 5,
            'text': '表单缺少题目样例参数'
        }
    if request.get('timeout') is None:
        return {
            'code': 5,
            'text': '表单缺少题目超时时间参数'
        }
    if request.get('memory_limit') is None:
        return {
            'code': 5,
            'text': '表单缺少题目内存限制参数'
        }
    if backend.edit_problem(pid=ident,
                            name=request['name'],
                            description=request['description'], tags=request['tags'],
                            io_examples=request['examples'], timeout=request['timeout'],
                            memory_limit=request['memory_limit']):
        return {
            'code': 0,
            'text': '操作成功!'
        }
    else:
        return {
            'code': 2,
            'text': '将要修改的题目不存在!'
        }


@app.route("/v1/problems/post", methods=['POST'])
def problems_post_router():
    require_admin = require_admin_permission()
    if require_admin is not True:
        return require_admin

    request = flask.request.get_json()
    if request.get('name') is None:
        return {
            'code': 5,
            'text': '表单缺少题目名称参数'
        }
    if request.get('description') is None:
        return {
            'code': 5,
            'text': '表单缺少题目描述参数'
        }
    if request.get('tags') is None:
        return {
            'code': 5,
            'text': '表单缺少题目标签参数'
        }
    if request.get('examples') is None:
        return {
            'code': 5,
            'text': '表单缺少题目样例参数'
        }
    if request.get('timeout') is None:
        return {
            'code': 5,
            'text': '表单缺少题目超时时间参数'
        }
    if request.get('memory_limit') is None:
        return {
            'code': 5,
            'text': '表单缺少题目内存限制参数'
        }
    backend.post_problem(author=backend.query_user_by_id(flask.session.get("user_id"))['username'],
                         name=request['name'],
                         description=request['description'], tags=request['tags'],
                         io_examples=request['examples'], timeout=request['timeout'],
                         memory_limit=request['memory_limit'])
    return {
        'code': 0,
        'text': '请求成功'
    }


@app.route("/v1/problems/checkpoints/get-list/<int:ident>", methods=['GET'])
def get_checkpoints_list_router(ident):
    if backend.query_problem_by_id(ident) is not None:
        return {
            'code': 0,
            'text': '请求成功!',
            'data': backend.get_checkpoint_list(ident)
        }
    else:
        return {
            'code': 2,
            'text': '题目不存在!'
        }


@app.route("/v1/problems/checkpoints/remove/<int:ident>/<checkpoint_name>", methods=['POST'])
def remove_checkpoint_from_problem_router(ident, checkpoint_name):
    if backend.query_problem_by_id(ident) is not None:
        c_list = backend.get_checkpoint_list(ident)
        if c_list.count(checkpoint_name):
            if backend.remove_checkpoint_from_problem(ident, checkpoint_name):
                return {
                    'code': 0,
                    'text': '请求成功!'
                }
            else:
                return {
                    'code': 2,
                    'text': '将要删除的检查点文件不存在!'
                }
        else:
            return {
                'code': 2,
                'text': '将要删除的检查点不存在!'
            }
    else:
        return {
            'code': 2,
            'text': '题目不存在!'
        }


@app.route("/v1/problems/checkpoints/upload/<int:ident>/<checkpoint_name>/in", methods=['POST'])
def upload_checkpoint_input_router(ident, checkpoint_name):
    with io.BytesIO() as dst:
        flask.request.files.get('file').save(dst)
        dst.seek(0)
        if backend.add_in_checkpoint_to_problem(ident, checkpoint_name, dst.read()):
            return {
                'code': 0,
                'text': '请求成功!'
            }
        else:
            return {
                'code': 2,
                'text': '题目不存在!'
            }


@app.route("/v1/problems/checkpoints/upload/<int:ident>/<checkpoint_name>/out", methods=['POST'])
def upload_checkpoint_output_router(ident, checkpoint_name):
    with io.BytesIO() as dst:
        flask.request.files.get('file').save(dst)
        dst.seek(0)
        if backend.add_out_checkpoint_to_problem(ident, checkpoint_name, dst.read()):
            return {
                'code': 0,
                'text': '请求成功!'
            }
        else:
            return {
                'code': 2,
                'text': '题目不存在!'
            }


@app.route("/v1/search/problems/by_id/<int:content>", methods=['GET'])
def search_problems_id_router(content):
    return {
        'code': 0,
        'text': '请求成功',
        'data': backend.search_problems('by_id', content)
    }


@app.route("/v1/search/problems/by_author/<content>", methods=['GET'])
def search_problems_author_router(content):
    return {
        'code': 0,
        'text': '请求成功',
        'data': backend.search_problems('by_author', content)
    }


@app.route("/v1/search/problems/by_description/<content>", methods=['GET'])
def search_problems_description_router(content):
    return {
        'code': 0,
        'text': '请求成功',
        'data': backend.search_problems('by_description', content)
    }


@app.route("/v1/search/problems/by_tags/<content>", methods=['GET'])
def search_problems_tags_router(content):
    return {
        'code': 0,
        'text': '请求成功',
        'data': backend.search_problems('by_tags', content)
    }


@app.route("/v1/search/problem_lists/by_name/<content>", methods=['GET'])
def search_problem_lists_by_name(content):
    return {
        'code': 0,
        'text': '请求成功',
        'data': backend.search_problem_list_by_name(content)
    }


@app.route("/v1/search/problem_lists/by_description/<content>", methods=['GET'])
def search_problem_lists_by_description(content):
    return {
        'code': 0,
        'text': '请求成功',
        'data': backend.search_problem_list_by_description(content)
    }


@app.route("/v1/search/problem_lists/by_problem/<int:content>", methods=['GET'])
def search_problem_lists_by_problem(content):
    return {
        'code': 0,
        'text': '请求成功',
        'data': backend.search_problem_list_by_problem(content)
    }


if __name__ == "main":
    app.run(host=config.get("api-server-host"), port=config.get("api-server-port"))
