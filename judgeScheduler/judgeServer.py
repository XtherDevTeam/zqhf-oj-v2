#!/bin/python3
from subprocess import Popen, PIPE

import config
import flask
import io
import json
import os
import pickle
import time
import api

app = flask.Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 256*1024*1024

@app.route('/submit', methods=['POST'])
def submit_1():
    l = api.get_free_judger_list()
    while not len(l):
        time.sleep(1)
        pass
    return api.send_task(l[0], flask.request.json)
    
@app.route('/info', methods=['GET'])
def info():
    return api.ask(config.judger_hosts[config.ask_from])

@app.route('/machines', methods=['GET'])
def machines():
    return api.get_judger_info()

if __name__ == '__main__':
    app.run(host=config.host, port=config.port)