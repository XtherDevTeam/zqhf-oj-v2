import json

config_file_path = "config.json"

def get(key):
    with open(config_file_path, "r+") as file:
        return json.loads(file.read())[key]
    
def set(key, val):
    with open(config_file_path, "w+") as file:
        with open(config_file_path, "r+") as rfile:
            c = json.loads(rfile.read())
            c[key] = val
            file.write(json.dumps(c))