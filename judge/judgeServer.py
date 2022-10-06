#!/bin/python3
from asyncore import read
from subprocess import Popen, PIPE
import uuid

import config
import flask
import json
import os
import _judger
import threading
import psutil
import cpuinfo
import _zqhf_oj_v2_spj
import io

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


def get_stdout(task_id: str):
    with open(f'/tmp/{task_id}-stdout.log', 'r') as file:
        return file.read()
    
    
def get_stderr(task_id: str):
    with open(f'/tmp/{task_id}-stderr.log', 'r') as file:
        return file.read()


# 第三次重构 解藕
def do_remove_task_files(task_id: str, use_plugin: dict):
    pipe_stdin = f'/tmp/{task_id}-stdin.log'
    pipe_stdout = f'/tmp/{task_id}-stdout.log'
    pipe_stderr = f'/tmp/{task_id}-stderr.log'
    
    source_fp = f'/tmp/{task_id}-source.{use_plugin["file-ext"]}'
    binary_fp = f'/tmp/{task_id}-test.o'
    
    try:
        os.remove(pipe_stdin)
        os.remove(pipe_stdout)
        os.remove(pipe_stderr)
        os.remove(source_fp)
        os.remove(binary_fp)
    except:
        pass


def do_compile(task_id: str, use_plugin: dict, source_file: str):
    
    pipe_stdout = f'/tmp/{task_id}-stdout.log'
    pipe_stderr = f'/tmp/{task_id}-stderr.log'
    
    source_fp = f'/tmp/{task_id}-source.{use_plugin["file-ext"]}'
    binary_fp = f'/tmp/{task_id}-test.o'
    
    with open(source_fp, 'w+') as file:
        file.write(source_file)

    use_plugin['compile_command'] = use_plugin['compile_command'].replace('$source_file', source_fp)
    use_plugin['compile_command'] = use_plugin['compile_command'].replace('$binary_file', binary_fp)
    
    fp = Popen(use_plugin['compile_command'], shell=True, cwd=os.getcwd(), stdin=PIPE, stdout=open(pipe_stdout, 'w+'), stderr=open(pipe_stderr, 'w+'))
    fp.wait()
    
    return fp.returncode


# 第三次优化评测机 运行评测插件不需要输入 由判题流程写入文件
def execute_plugin(task_id: str, use_plugin: dict, time_out: int = 1000, memlimit: int = 1024):
    
    pipe_stdin = f'/tmp/{task_id}-stdin.log'
    pipe_stdout = f'/tmp/{task_id}-stdout.log'
    pipe_stderr = f'/tmp/{task_id}-stderr.log'
    
    source_fp = f'/tmp/{task_id}-source.{use_plugin["file-ext"]}'
    binary_fp = f'/tmp/{task_id}-test.o'

    use_plugin['exec_command'] = use_plugin['exec_command'].replace('$source_file', source_fp)
    use_plugin['exec_command'] = use_plugin['exec_command'].replace('$binary_file', binary_fp)
    
    ret_stdout = ''
    ret_stderr = ''

    stat = ''
        
    with open(pipe_stdout, 'w+') as file:
        pass
        
    with open(pipe_stderr, 'w+') as file:
        pass
    
    arglist = cmdline2arglist(use_plugin['exec_command'])
    
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
    
    return [stat, ret_stdout, ret_stderr, result['signal']]


def checker(result, expectedOutput):
    if (result['status'] != 'OK'):
        return result
    
    result['stdout'] = result['stdout'].replace('\r', '')

    if result['stdout'] != "":
        while result['stdout'][-1] == '\n' or result['stdout'][-1] == ' ':
            result['stdout'] = result['stdout'][0:-1]

    expectedOutput = expectedOutput.replace('\r', '')

    if expectedOutput != "":
        while expectedOutput[-1] == '\n' or expectedOutput[-1] == ' ' or expectedOutput[-1] == '\0' or expectedOutput[-1] == '\r':
            expectedOutput = expectedOutput[0:-1]

    if len(result['stdout']) != len(expectedOutput):
        result['status'] = 'Wrong Answer at character ' + str(len(result['stdout'])) + ' of ' + str(len(expectedOutput))
        return result

    else:
        for i in range(len(expectedOutput) - 1):
            if (result['stdout'][i] != expectedOutput[i]):
                result['status'] = 'Wrong Answer at character ' + str(i)
                return result

    result['status'] = 'Accepted'
    # print(result)
    return result


@app.route('/submit', methods=['POST'])
def submit_1():
    with lock:
        data = flask.request.json
        task_id = uuid.uuid4()
        
        use_plugin = getPluginDetails(data['plugin'])
        compile_result = do_compile(task_id=task_id, use_plugin=use_plugin, source_file=data['source_file'])
        
        pipe_stdin = f'/tmp/{task_id}-stdin.log'
        pipe_stdout = f'/tmp/{task_id}-stdout.log'
        pipe_stderr = f'/tmp/{task_id}-stderr.log'
        
        if compile_result:
            return checker({
                'status': 'CE',
                'stdout': get_stdout(task_id=task_id),
                'stderr': get_stderr(task_id=task_id),
                'return_code': '1'
            }, data['output'])
        
        with open(pipe_stdin, 'w+') as file:
            file.write(data['input'])
        
        result_data = execute_plugin(task_id, use_plugin, data['time_limit'], data['mem_limit'])
        return checker({
            'status': result_data[0],
            'stdout': str(result_data[1]),
            'stderr': str(result_data[2]),
            'return_code': str(result_data[3])
        }, data['output'])
        
        
# 第三次优化评测机 一次编译多次运行 需要主机传入所有数据点
@app.route('/checker', methods=['POST'])
def submit_2():
    print(flask.request.files.keys())
    data = json.loads(flask.request.files.get('json').stream.read())
    result = []
    result = {
        'ac': True,
        'score': 0,
        'checkpoints': [],
    }
    
    judge_type = data['judge_type']
    spj_program_task_id = ''
    spj_program_stdin = ''
    spj_use_plugin = {}
    if judge_type == 'spj':
        # 预编译spj
        spj_use_plugin = getPluginDetails('C++14')
        spj_program_task_id = uuid.uuid4()
        print('spj_uuid', spj_program_task_id)
        spj_program_stdin = f'/tmp/{spj_program_task_id}-stdin.log'
        spj_compile_result = do_compile(spj_program_task_id, spj_use_plugin, data['spj_source'])
        if spj_compile_result:
            result['checkpoints'].append({
                'status': 'System Error',
                'stdout': get_stdout(spj_program_task_id),
                'stderr': get_stderr(spj_program_task_id) + '\n' + 'An error occurred in the Special Judge Plugin\n',
                'return_code': '1'
            })
            result['ac'] = False
            return result
    
    task_id = uuid.uuid4()
    print('task_uuid', task_id)
    use_plugin = getPluginDetails(data['plugin'])
    compile_result = do_compile(task_id, use_plugin, data['source_file'])
    
    for i in data['tests']:
        pipe_stdin = f'/tmp/{task_id}-stdin.log'
        pipe_stdout = f'/tmp/{task_id}-stdout.log'
        
        in_filename = i[0]
        out_filename = i[1]
        flask.request.files[in_filename].save(pipe_stdin)
        
        if compile_result:
            result['checkpoints'].append({
                'status': 'Compile Error',
                'stdout': get_stdout(task_id),
                'stderr': get_stderr(task_id),
                'return_code': '1'
            })
            result['ac'] = False
        else:
            exec_result = execute_plugin(task_id=task_id, 
                                         use_plugin=use_plugin,
                                         time_out=data['time_limit'],
                                         memlimit=data['mem_limit'])
            result['checkpoints'].append({
                'status': exec_result[0],
                'stdout': str(exec_result[1]),
                'stderr': str(exec_result[2]),
                'return_code': str(exec_result[3])
            })
            
            # 评测
            if judge_type == 'spj':
                with open(spj_program_stdin, 'w+') as spj_infile:
                    with open(pipe_stdin, 'r+') as ins:
                        with open(pipe_stdout, 'r+') as outs:
                            spj_infile.write(_zqhf_oj_v2_spj.build_stdin(ins.read(), outs.read()))
                            
                spj_result = execute_plugin(task_id=spj_program_task_id, 
                                            use_plugin=spj_use_plugin,
                                            time_out=65536,
                                            memlimit=1048576)
                spj_result = {
                    'status': spj_result[0],
                    'stdout': str(spj_result[1]),
                    'stderr': str(spj_result[2]),
                    'return_code': str(spj_result[3])
                }
                if spj_result['return_code'] != '0':
                    spj_result['status'] = 'System Error'
                    spj_result['stderr'] += '\n' + 'An error occurred in the Special Judge Plugin\n'
                    result['checkpoints'][-1] = spj_result
                else:
                    try:
                        spj_result = _zqhf_oj_v2_spj.parse_result(spj_result['stdout'])
                        result['checkpoints'][-1]['status'] = spj_result['status']
                        result['checkpoints'][-1]['stderr'] += '\n' + 'SPJ Plugin Message: ' + spj_result['message']
                        result['score'] += spj_result['score']
                    except Exception:
                        spj_result['status'] = 'System Error'
                        spj_result['stderr'] += '\n' + 'An error occurred in the Special Judge Plugin\n'
                        result[-1] = spj_result
                        
            else:
                result['checkpoints'][-1] = checker(result['checkpoints'][-1], flask.request.files.get(out_filename).stream.read().decode('utf-8'))
                if result['checkpoints'][-1]['status'] == 'Accepted':
                    result['score'] += int(round(100 * (1 / len(data['tests'])), 0))
                
            if result['checkpoints'][-1]['status'] != 'Accepted':
                result['ac'] = False
                
            if len(result['checkpoints'][-1]['stdout']) > 1024:
                result['checkpoints'][-1]['stdout'] = result['checkpoints'][-1]['stdout'][0:1024] + "\n[Excessive output]\n"
            if len(result['checkpoints'][-1]['stderr']) > 1024:
                result['checkpoints'][-1]['stderr'] = result['checkpoints'][-1]['stderr'][0:1024] + "\n[Excessive output]\n"
            
    do_remove_task_files(task_id=task_id, use_plugin=use_plugin)
    
    if judge_type == 'spj':
        do_remove_task_files(task_id=spj_program_task_id, use_plugin=spj_use_plugin)
            
    return result
    
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