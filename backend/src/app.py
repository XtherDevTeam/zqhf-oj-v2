import pickle

import flask
import config
import backend
from flask_cors import CORS

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
    if pickle.loads(get_login_details()['other_message'])['permission_level'] < 1:
        return {'code': 1, 'text': '权限不足!'}
    return True


@app.before_request
def before_request():
    backend.db = backend.connect_db()


@app.teardown_request
def teardown_request(exception):
    backend.db.commit()
    backend.db.close()


@app.route("/", methods=['GET'])
def root_router():
    return {"code": 0, "text": "API服务状态正常!"}


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


@app.route('/v1/user/logout', methods=['GET'])
def logout_router():
    if flask.session.get('user_id') is not None:
        del flask.session['user_id']
        return {"code": 0, "text": "登出成功!"}
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
            del result['other_message']
            return {
                'code': 0,
                'text': '请求成功',
                'data': result
            }
        else:
            result = backend.query_user_by_id(int(ident))
            if result is None:
                return {"code": 2, "text": "用户不存在!"}
            del result['password']
            del result['other_message']
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


@app.route("/v1/bulletins/get/<int:start>/<int:count>", methods=['GET'])
def bulletins_get_router(start, count):
    return {
        'code': 0,
        'text': '请求成功',
        'data': backend.query_bulletins_by_size(start, count)
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


@app.route("/v1/bulletins/edit/<int:id>", methods=['POST'])
def bulletin_edit_router(ident: int):
    require_admin = require_admin_permission()
    if require_admin is not True:
        return require_admin

    data = flask.request.get_json()
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


if __name__ == "main":
    app.run(host=config.get("api-server-host"), port=config.get("api-server-port"))
