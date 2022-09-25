#!/bin/python3
import hashlib
import os
import signal
import subprocess
import sys
import time


def do_start(program: str):
    while os.access(hashlib.md5(program.encode('utf-8')).hexdigest() + '.lock', os.F_OK):
        print("Resource locked.")
        time.sleep(1)

    pid = os.fork()
    if pid == 0:
        proc = subprocess.Popen(program, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        with open(hashlib.md5(program.encode('utf-8')).hexdigest() + '.lock', 'w+') as file:
            file.write(str(os.getpid()))

        proc.communicate()
        os.remove(hashlib.md5(program.encode('utf-8')).hexdigest() + '.lock')
    else:
        time.sleep(1)


def do_stop(program: str):
    try:
        with open(hashlib.md5(program.encode('utf-8')).hexdigest() + '.lock', 'r+') as file:
            os.kill(int(file.read()), signal.SIGTERM)
        os.remove(hashlib.md5(program.encode('utf-8')).hexdigest() + '.lock')
        return True
    except Exception as e:
        print(str(e))
        return False


if sys.argv[1] == 'start':
    if sys.argv[2] == 'api':
        do_start('cd ../backend/src && gunicorn -w 4 -b 0.0.0.0:9013 app:app')
    elif sys.argv[2] == 'judge':
        do_start('cd ../judge && ./judgeServer.py')
    elif sys.argv[2] == 'web':
        os.system('service nginx start')

if sys.argv[1] == 'stop':
    os.system('killall gunicorn && killall judgeServer.py')

if sys.argv[1] == 'install':
    if sys.argv[2] == 'page':
        os.system(
            'mkdir -p /var/www/html/project; cd ../frontend; make build; cp -r -v ./dist/* /var/www/html/project/;exit')
    if sys.argv[2] == 'nginx':
        os.system('cp templates/nginx_config.conf /etc/nginx/sites-enabled/zqhf-oj-v2.conf')