import io
import json
import pickle
import requests


def get_machine_list(judge_server_address):
    recv_data = json.loads(
        requests.get("http://%s/machines" % judge_server_address).content)

    return recv_data

def submit(judge_server_address, judge_plugin, source_file, data_input, data_output, time_limit,
           mem_limit, env_variables):
    recv_data = json.loads(
        requests.post("http://%s/submit" % judge_server_address,
                    json={
                        'plugin': judge_plugin,
                        'input': data_input,
                        'output': data_output,
                        'time_limit': time_limit,
                        'mem_limit': mem_limit,
                        'env_variables': env_variables,
                        'source_file': source_file
                    }, timeout=114514191).content,)

    return recv_data


def judge(judge_server_address, points):
    recv_data = json.loads(
        requests.post("http://%s/checker" % judge_server_address,
                    timeout=114514191, files=points).content,)

    return recv_data