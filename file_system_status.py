import logging
import json

LOCATION = "status.json"

def clear():
    f = open(LOCATION, 'w')
    f.write('{}\n')
    f.close()


def load():
    try:
        f = open(LOCATION,'r')
        json_data = f.read()
        f.close()
    except IOError:
        json_data = '{}'
    return json.loads(json_data)

def save(app_status):
    f = open(LOCATION, 'w')
    f.write(json.dumps(app_status))
    f.close()


