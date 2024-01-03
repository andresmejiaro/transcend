# utils/logger.py

import logging
import logging
import inspect

def log_message(message, level=logging.INFO):
    frame = inspect.currentframe().f_back
    
    function_name = frame.f_code.co_name

    log_message = f"{function_name}: {message}"
    
    logging.log(level, log_message)


