# utils/input_handler.py

import asyncio
import curses
from utils.logger import log_message

async def get_user_string(stdscr):
    loop = asyncio.get_running_loop()

    input_string = ""
    while True:
        try:
            key = await loop.run_in_executor(None, stdscr.getch)

            if key == 10:  # Enter key
                return input_string
            elif key == curses.KEY_BACKSPACE:
                input_string = input_string[:-1]
            elif key == 27:  # ESC key
                return None  # Return None to indicate termination
            else:
                input_string += chr(key)

            # Update the screen or do other processing as needed
        except Exception as e:
            # Use the logger for exception handling
            log_message("get_user_string", str(e))
            return "error"

async def get_user_ch(stdscr):
    loop = asyncio.get_running_loop()
    
    try:
        key = await loop.run_in_executor(None, stdscr.getch)

        if key == curses.KEY_UP:
            return "up"
        elif key == curses.KEY_DOWN:
            return "down"
        elif key == curses.KEY_LEFT:
            return "left"
        elif key == curses.KEY_RIGHT:
            return "right"
        elif key == ord("q"):
            return "quit"
        elif key == ord("h"):
            return "help"
        elif key == 27:  # ESC key
            return None  # Return None to indicate termination
        elif key == curses.KEY_EXIT:
            return None
        else:
            return "invalid command"
    except Exception as e:
        # Handle exceptions (e.g., log the error)
        log_message("get_user_ch", str(e))
        return "error"
