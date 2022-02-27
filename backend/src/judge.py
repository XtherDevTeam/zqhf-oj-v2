import io
import json
import pickle
import requests


def submit(judge_server_address, judge_plugin, source_file, data_input, data_output, time_limit,
           mem_limit, env_variables):
    packed_data = io.BytesIO(pickle.dumps(
        {
            'plugin': judge_plugin,
            'input': data_input,
            'output': data_output,
            'time_limit': time_limit,
            'mem_limit': mem_limit,
            'env_variables': env_variables,
            'source_file': source_file
        }
    ))
    recv_data = json.loads(
        requests.get("http://%s/submit" % judge_server_address,
                     files={'data': packed_data}).content)

    return recv_data
