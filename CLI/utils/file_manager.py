# utils/data_storage/file_manager.py

import os
import json
import logging
from utils.logger import log_message

class FileManager:
    def __init__(self):
        self.DATA_DIR = "game_files/data"
        self.TEXTURES_DIR = "game_files/textures"
        self.LOGS_DIR = "game_files/logs"


    def save_data(self, file_name, data):
        try:
            file_path = os.path.join(self.DATA_DIR, file_name)
            with open(file_path, "w") as data_file:
                json.dump(data, data_file)
        except Exception as e:
            log_message(f"Error saving data: {e}", level=logging.ERROR)

    def load_data(self, file_name):
        try:
            file_path = os.path.join(self.DATA_DIR, file_name)
            if os.path.exists(file_path):
                with open(file_path, "r") as data_file:
                    return json.load(data_file)
            return None
        except Exception as e:
            log_message(f"Error loading data: {e}", level=logging.ERROR)
            return None
        
    def load_texture(self, file_name):
        try:
            file_path = os.path.join(self.TEXTURES_DIR, file_name)
            if os.path.exists(file_path):
                with open(file_path, "r") as texture_file:
                    return texture_file.read().splitlines()
            return None
        except Exception as e:
            log_message(f"Error loading texture: {e}", level=logging.ERROR)
            return None
        
    def load_gif(self, file_name):
        try:
            file_path = os.path.join(self.TEXTURES_DIR, file_name)
            if os.path.exists(file_path):
                with open(file_path, "r") as gif_file:
                    return gif_file.read().splitlines()
            return None
        except Exception as e:
            log_message(f"Error loading gif: {e}", level=logging.ERROR)
            return None