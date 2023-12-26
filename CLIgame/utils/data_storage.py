# utils/data_storage.py

import os
import json

DATA_DIR = "data"

def initialize_data_directory():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def save_data(file_name, data):
    file_path = os.path.join(DATA_DIR, file_name)
    with open(file_path, "w") as data_file:
        json.dump(data, data_file)

def load_data(file_name):
    file_path = os.path.join(DATA_DIR, file_name)
    if os.path.exists(file_path):
        with open(file_path, "r") as data_file:
            return json.load(data_file)
    return None