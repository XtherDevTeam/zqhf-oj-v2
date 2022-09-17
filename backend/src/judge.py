import io
import json
import pickle
import requests


def submit(judge_server_address, judge_plugin, source_file, data_input, data_output, time_limit,
           mem_limit, env_variables):
    recv_data = json.loads(
        requests.post("http://%s/ide_submit" % judge_server_address,
                    json={
                        'plugin': judge_plugin,
                        'input': data_input,
                        'output': data_output,
                        'time_limit': time_limit,
                        'mem_limit': mem_limit,
                        'env_variables': env_variables,
                        'source_file': source_file
                    }).content)

    return recv_data
