import json


with open("config.json", "r") as f:
    conf = json.loads(f.read())

seed = conf['seed']