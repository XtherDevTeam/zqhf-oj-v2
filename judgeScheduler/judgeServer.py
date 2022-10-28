#!/bin/python3
from subprocess import Popen, PIPE
from urllib import request

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
    print('got a execute task')
    l = api.get_free_judger_list()
    while not len(l):
        time.sleep(1)
        pass
    return api.send_task(l[0], flask.request.json)


@app.route('/checker', methods=['POST'])
def submit_2():
    print('got a checker task')
    l = api.get_free_judger_list()
    while not len(l):
        time.sleep(1)
        pass
    
    filelist = []
    for i in flask.request.files.keys():
        file_obj = flask.request.files.get(i)
        origin_file_name = file_obj.filename
        filelist.append((i, (origin_file_name, file_obj.stream.read(), file_obj.content_type)))
    
    return api.send_judge_task(l[0], filelist)
    

@app.route('/info', methods=['GET'])
def info():
    return api.ask_info(config.judger_hosts[config.ask_from])

@app.route('/machines', methods=['GET'])
def machines():
    return api.get_judger_info()

if __name__ == '__main__':
    app.run(host=config.host, port=config.port)