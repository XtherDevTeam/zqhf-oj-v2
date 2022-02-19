import config
import flask
import backend

app = flask.Flask(__name__)


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


@app.route("/v1/register/<username>/<password>", methods=['POST'])
def register_router(username, password):
    if backend.query_user_by_name(username) is not None:
        return {"code": 3, "text": "用户已存在!"}
    backend.register_user(username, password)
    return {"code": 0, "text": "注册成功!"}


@app.route("/v1/login/<username>/<password>", methods=['POST'])
def login_router(username, password):
    if backend.query_user_by_name(username) is None:
        return {"code": 2, "text": "用户不存在!"}
