#!/bin/python3
import hashlib
import os, json
import sys
import time

def do_start(program: str):
    while os.access(hashlib.md5(program.encode('utf-8')).hexdigest() + '.lock', os.F_OK):
        print("Resource locked.")
        time.sleep(1)
    pid = os.fork()
    if pid == 0:
        with open(hashlib.md5(program.encode('utf-8')).hexdigest() + '.lock', 'w+') as file:
            file.write(str(os.getpid()))
        
        os.system(program)
        os.remove(hashlib.md5(program.encode('utf-8')).hexdigest() + '.lock')
    else:
        sys.exit(0)
    
def do_stop(program: str):
    try:
        with open(hashlib.md5(program.encode('utf-8')).hexdigest() + '.lock', 'r+') as file:
            os.kill(int(file.read()), 15)
        os.remove(hashlib.md5(program.encode('utf-8')).hexdigest() + '.lock')
        return True
    except Exception as e:
        print(str(e))
        return False
    
if sys.argv[1] == 'start':
    if sys.argv[2] == 'api':
        do_start('cd ../backend/src && gunicorn -w 4 -b 0.0.0.0:9013 app:app')
    elif sys.argv[2] == 'judge':
        do_start('cd ../judge && python3 judgeServer.py')
        
    
if sys.argv[1] == 'stop':
    if sys.argv[2] == 'api':
        do_stop('cd ../backend/src && gunicorn -w 4 -b 0.0.0.0:9013 app:app')
    elif sys.argv[2] == 'judge':
        do_stop('cd ../judge && python3 judgeServer.py')