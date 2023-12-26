# utils/input_handler.py

import asyncio
import curses
import logging
from utils.logger import log_message

def get_user_string(stdscr, prompt, row, col):
    input_string = ""
    while True:
        try:
            stdscr.clear()
            
            # Display the prompt and input string
            stdscr.addstr(row, col, prompt)
            stdscr.addstr(row + 1, col, input_string)

            key = stdscr.getch()

            if key == 10:  # Enter key
                log_message(f'get_user_string: {input_string}', level=logging.INFO)
                return input_string
            elif key == curses.KEY_BACKSPACE:
                input_string = input_string[:-1]
            elif key == 27:  # ESC key
                return None  # Return None to indicate termination
            else:
                input_string += chr(key)

            stdscr.refresh()
        except Exception as e:
            log_message(f'get_user_string: {e}', level=logging.ERROR)
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
        elif key == 10:  # Enter key
            return "enter"
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
        log_message(f'get_user_ch: {e}', level=logging.ERROR)
        return "error"
