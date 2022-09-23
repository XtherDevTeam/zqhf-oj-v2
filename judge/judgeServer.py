#!/bin/python3
from subprocess import Popen, PIPE
import uuid

import config
import flask
import io
import json
import os
import pickle
import time
import _judger
import threading
import platform
import psutil
import cpuinfo

lock = threading.Lock()

app = flask.Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 256*1024*1024

machine = {
    'cpu': cpuinfo.get_cpu_info()['brand_raw'],
    'mem': psutil.virtual_memory().total / 1024 / 1024
}

def cmdline2arglist(cmdline: str):
    res = []
    temp = ""
    in_str = False
    for i in cmdline:
        if in_str:
            if i == '"' or i == '\'':
                in_str = False
            else:
                temp += i
        elif i == '"' or i == '\'':
            instr = True
        elif i == ' ':
            if temp != "":
                res.append(temp)
                temp = ""
        else:
            temp += i
    
    if temp != "":
        res.append(temp)
    
    return res

            

def getPluginDetails(name: str):
    with open(config.plugins_dir + '/' + name + '.json', 'r+') as file:
        return json.loads(file.read())


def execute_plugin(use_plugin: str, source_file: str, input: str, env: dict, time_out: int = 1000,
                   memlimit: int = 1024):
    
    fork = getPluginDetails(use_plugin)
    
    task_id = uuid.uuid4()
    
    pipe_stdin = f'/tmp/{task_id}-stdin.log'
    pipe_stdout = f'/tmp/{task_id}-stdout.log'
    pipe_stderr = f'/tmp/{task_id}-stderr.log'
    
    source_fp = f'/tmp/{task_id}-source.{fork["file-ext"]}'
    binary_fp = f'/tmp/{task_id}-test.o'
    
        
    with open(source_fp, 'w+') as file:
        file.write(source_file)

    fork['compile_command'] = fork['compile_command'].replace('$source_file', source_fp)
    fork['compile_command'] = fork['compile_command'].replace('$binary_file', binary_fp)
    fork['exec_command'] = fork['exec_command'].replace('$source_file', source_fp)
    fork['exec_command'] = fork['exec_command'].replace('$binary_file', binary_fp)
    
    ret_stdout = ''
    ret_stderr = ''

    stat = ''
    fp = Popen(fork['compile_command'], shell=True, cwd=os.getcwd(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
    fp.stdout.flush()
    fp.stderr.flush()
    fp.wait()
    if fp.returncode != 0:
        stat = 'Compile Error'
        ret_stdout += fp.stdout.read().decode('utf-8')
        ret_stderr += fp.stderr.read().decode('utf-8')
        fp.stdout.flush()
        return [stat, ret_stdout, ret_stderr, fp.returncode]
    
    print(pipe_stdin, pipe_stdout, pipe_stderr)
    
    with open(pipe_stdin, 'w+') as file:
        file.write(input)
        
    with open(pipe_stdout, 'w+') as file:
        pass
        
    with open(pipe_stderr, 'w+') as file:
        pass
    
    # .split()
    arglist = cmdline2arglist(fork['exec_command'])
    print(arglist)
    
    result = _judger.run(max_cpu_time=time_out,
                max_real_time=2*time_out, 
                max_memory=memlimit * 1024,
                max_stack=_judger.UNLIMITED,
                exe_path=arglist[0],
                input_path=pipe_stdin,
                output_path=pipe_stdout,
                error_path=pipe_stderr,
                args=arglist[1:],
                env=[],
                log_path="/tmp/judger_log.log",
                seccomp_rule_name=None,
                uid=0,
                gid=0,
                max_output_size=_judger.UNLIMITED,
                max_process_number=1)
    
    with open(pipe_stdout, 'r') as file:
        ret_stdout = file.read()
        
    with open(pipe_stderr, 'r') as file:
        ret_stderr = file.read()
    
    # 向前兼容
    if result['result'] == _judger.RESULT_SUCCESS:
        stat = 'OK'
    elif result['result'] == _judger.RESULT_CPU_TIME_LIMIT_EXCEEDED:
        stat = 'Time Limit Exceeded'
    elif result['result'] == _judger.RESULT_REAL_TIME_LIMIT_EXCEEDED:
        stat = 'Time Limit Exceeded'
    elif result['result'] == _judger.RESULT_MEMORY_LIMIT_EXCEEDED:
        stat = 'Memory Limit Exceeded'
    elif result['result'] == _judger.RESULT_RUNTIME_ERROR:
        stat = 'Runtime Error'
    elif result['result'] == _judger.RESULT_SYSTEM_ERROR:
        stat = 'System Error'
        
    ret_stderr += '\nDebug: ' + json.dumps(result) + '\n'
    
    print(pipe_stdin, pipe_stdout, pipe_stderr)
    
    try:
        os.remove(pipe_stdin)
        os.remove(pipe_stdout)
        os.remove(pipe_stderr)
        os.remove(source_fp)
        os.remove(binary_fp)
    except:
        pass
    
    return [stat, ret_stdout, ret_stderr, result['signal']]


def checker(result, expectedOutput):
    if (result['status'] != 'OK'):
        return result

    if result['stdout'] != "":
        while result['stdout'][-1] == '\n' or result['stdout'][-1] == ' ':
            result['stdout'] = result['stdout'][0:-1]

    if expectedOutput != "":
        while expectedOutput[-1] == '\n' or expectedOutput[-1] == ' ':
            expectedOutput = expectedOutput[0:-1]

    if len(result['stdout']) != len(expectedOutput):
        # print(execute_result[1],'\n',now_item[4])
        result['status'] = 'Wrong Answer at character ' + str(len(result['stdout'])) + ' of ' + str(len(expectedOutput))
        return result

    else:
        for i in range(len(expectedOutput) - 1):
            if (result['stdout'][i] != expectedOutput[i]):
                result['status'] = 'Wrong Answer at character ' + str(i)
                return result

    if len(result['stdout']) > 1024:
        result['stdout'] = result['stdout'][0:1024] + "\n[Excessive output]\n"
    if len(result['stderr']) > 1024:
        result['stderr'] = result['stderr'][0:1024] + "\n[Excessive output]\n"

    result['status'] = 'Accepted'
    # print(result)
    return result

@app.route('/submit', methods=['POST'])
def submit_1():
    with lock:
        data = flask.request.json
        result_data = execute_plugin(data['plugin'], data['source_file'], data['input'], data['env_variables'],
                                    data['time_limit'], data['mem_limit'])
        return checker({
            'status': result_data[0],
            'stdout': str(result_data[1]),
            'stderr': str(result_data[2]),
            'return_code': str(result_data[3])
        }, data['output'])
    
@app.route('/info', methods=['GET'])
def info():
    data = config.judge_server_conf
    
    data['machine'] = machine
    
    if lock.locked():
        data['status'] = 'busy'
    else:
        data['status'] = 'free'
    
    return data

@app.route('/status', methods=['GET'])
def status():
    data = {}
    
    if lock.locked():
        data['status'] = 'busy'
    else:
        data['status'] = 'free'
    
    return data

if __name__ == '__main__':
    app.run(host=config.host, port=config.port)