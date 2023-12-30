# utils/logger.py

import os
import datetime
import logging

LOGS_DIR = "logs"

def initialize_logs_directory():
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)

def initialize_logger():
    log_file_path = os.path.join(LOGS_DIR, "app_log.txt")

    logging.basicConfig(
        filename=log_file_path,
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] [%(funcName)s] %(message)s",
    )

def log_message(message, level=logging.INFO):
    logging.log(level, message)
