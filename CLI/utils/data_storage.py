# utils/data_storage.py

import os
import json
import logging
from utils.logger import log_message


DATA_DIR = "data"
TEXTURES_DIR = "textures"

def initialize_data_directory():
    try:
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
    except Exception as e:
        log_message(f"Error creating data directory: {e}", level=logging.ERROR)

def save_data(file_name, data):
    try:
        file_path = os.path.join(DATA_DIR, file_name)
        with open(file_path, "w") as data_file:
            json.dump(data, data_file)
    except Exception as e:
        log_message(f"Error saving data: {e}", level=logging.ERROR)

def load_data(file_name):
    try:
        file_path = os.path.join(DATA_DIR, file_name)
        if os.path.exists(file_path):
            with open(file_path, "r") as data_file:
                return json.load(data_file)
        return None
    except Exception as e:
        log_message(f"Error loading data: {e}", level=logging.ERROR)
        return None
    
def load_texture(file_name):
    try:
        file_path = os.path.join(TEXTURES_DIR, file_name)
        if os.path.exists(file_path):
            with open(file_path, "r") as texture_file:
                return texture_file.read().splitlines()
        return None
    except Exception as e:
        log_message(f"Error loading texture: {e}", level=logging.ERROR)
        return None
    
def load_gif(file_name):
    try:
        file_path = os.path.join(TEXTURES_DIR, file_name)
        if os.path.exists(file_path):
            with open(file_path, "r") as gif_file:
                return gif_file.read().splitlines()
        return None
    except Exception as e:
        log_message(f"Error loading gif: {e}", level=logging.ERROR)
        return None