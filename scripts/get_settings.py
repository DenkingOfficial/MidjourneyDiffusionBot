import os
import json


def get_settings(model="illuminati_v1.1") -> dict:
    filename = os.path.join("params/models.json")
    try:
        with open(filename, mode="r") as f:
            return json.loads(f.read())[model]
    except FileNotFoundError:
        return {}
