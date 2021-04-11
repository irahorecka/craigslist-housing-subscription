import json
import os

FILE_PATH = os.path.dirname(os.path.abspath(__file__))


def get_users():
    with open(os.path.join(FILE_PATH, "users.json")) as f:
        return json.load(f)
