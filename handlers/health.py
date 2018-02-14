import datetime

from flask import json


def monitor():
    return json.dumps({"API STATUS": "LIVE", "CURRENT TIMESTAMP": str(datetime.datetime.now())}), 200
