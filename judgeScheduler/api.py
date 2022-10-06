import requests, config, json

"""
@brief 询问指定评测机状态
@return Dict 状态信息
"""
def ask_stat(host : str) -> dict:
    status = json.loads(requests.get(f'http://{host}/status').content)
    return status

"""
@brief 询问指定评测机信息
@return Dict 状态信息
"""
def ask_info(host : str) -> dict:
    status = json.loads(requests.get(f'http://{host}/info').content)
    return status

"""
@brief 获取当前空闲评测机列表
@return List 空闲评测机列表
"""
def get_free_judger_list() -> list:
    ret = []
    idx = 0
    for i in config.judger_hosts:
        if ask_stat(i)['status'] == 'free':
            ret.append(idx)
        idx += 1
    return ret

"""
@brief 获取每台评测机的详细信息
@return List 评测机的详细信息
"""
def get_judger_info() -> list:
    ret = []
    for i in config.judger_hosts:
        ret.append(ask_info(i))
    return ret

"""
@brief 向指定评测机发送任务
@return Dict 评测机的返回值
"""
def send_task(host : int, param : dict) -> dict:
    print(param)
    resp = requests.post("http://%s/submit" % config.judger_hosts[host],
                            json=param, timeout=114514191)
    try:
        resp = json.loads(resp.content)
        return resp
    except:
        return {
            'status': 'System Error',
            'stdout': 'The specified judge machine encountered an error during judging.',
            'stderr': '',
            'return_code': '255'
        }
        

def send_judge_task(host: int, files: list) -> dict:
    resp = requests.post("http://%s/checker" % config.judger_hosts[host],
                            files=files, timeout=114514191)
    try:
        resp = json.loads(resp.content)
        return resp
    except:
        return {
            'ac': False,
            'score': 0,
            'checkpoints': [
                {
                    'status': 'System Error',
                    'stdout': 'The specified judge machine encountered an error during judging.',
                    'stderr': '',
                    'return_code': '255'
                }
            ]
        }