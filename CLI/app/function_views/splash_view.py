# app/function_views/splash_view.py

import curses
import time

from utils.logger import log_message
from utils.data_storage import load_texture
import logging

def display_splash_screen(stdscr):
    try:
        last_frame_time = time.time()  # Initialize last_frame_time

        # Load logo frames
        logo_frames = [load_texture('logo.txt'), load_texture('logo2.txt')]
        current_logo_frame = 0

        frame_rate = 2

        while True:
            stdscr.clear()

            # Get the terminal size
            rows, cols = get_terminal_size(stdscr)

            if rows < 24 or cols < 80:
                print_screen_too_small(stdscr, rows, cols)
                stdscr.refresh()
                continue
                
            # Print the logo
            print_logo(stdscr, rows, cols, logo_frames[current_logo_frame])

            # Print frame rate
            print_frame_rate(stdscr, rows, cols, last_frame_time)

            # Print header
            print_header(stdscr, rows, cols)

            # Print message under logo
            print_message_under_logo(stdscr, rows, cols, "Press any key to continue...")

            # Refresh the screen
            stdscr.refresh()

            # Animation delay
            print_animated_logo(frame_rate)

            # Switch to the next logo frame
            current_logo_frame = (current_logo_frame + 1) % len(logo_frames)

            # Check for user input
            user_input = stdscr.getch()
            if user_input != curses.ERR:
                break  # Break the loop when any key is pressed

    except Exception as e:
        log_message(f"Error displaying splash screen: {e}", level=logging.ERROR)

# Helper methods (unchanged)
def get_terminal_size(stdscr):
    rows, cols = stdscr.getmaxyx()
    return rows, cols
# --------------------------------------------

# Widget methods
def print_screen_too_small(stdscr, max_y, max_x):
    try:
        stdscr.addstr(0, 0, "Terminal is too small, please resize the terminal to at least 80x24.", curses.color_pair(3))

    except Exception as e:
        log_message(f"Error printing screen too small message: {e}", level=logging.ERROR)

def print_header(stdscr, max_y, max_x):
    try:
        header = "Welcome to Pong!"
        row, col = 1, max_x // 2 - len(header) // 2
        stdscr.addstr(row, col, header)

    except Exception as e:
        log_message(f"Error printing header: {e}", level=logging.ERROR)

def print_frame_rate(stdscr, max_y, max_x, last_frame_time):
    try:
        current_time = time.time()
        frame_rate = 1 / (current_time - last_frame_time)
        last_frame_time = current_time

        stdscr.addstr(0, max_x - 21, f"Frame Rate: {frame_rate:.2f} FPS", curses.color_pair(3) | curses.A_DIM | curses.A_BOLD)

    except Exception as e:
        log_message(f"Error printing frame rate: {e}", level=logging.ERROR)

def print_logo(stdscr, max_y, max_x, logo):
    try:
        logo_height = len(logo)
        logo_width = len(logo[0])

        row = max_y // 2 - logo_height // 2
        col = max_x // 2 - logo_width // 2

        for frame in logo:
            stdscr.addstr(row, col, frame)
            row += 1

    except Exception as e:
        log_message(f"Error printing logo: {e}", level=logging.ERROR)

def print_animated_logo(frame_rate):
    try:
        # Adjust the delay to achieve the desired frame rate
        time.sleep(1 / frame_rate)

    except Exception as e:
        log_message(f"Error during animation delay: {e}", level=logging.ERROR)

def print_message_under_logo(stdscr, max_y, max_x, message):
    try:
        row, col = max_y - 2, max_x // 2 - len(message) // 2
        stdscr.addstr(row, col, message, curses.color_pair(4) | curses.A_BLINK)

    except Exception as e:
        log_message(f"Error printing message under logo: {e}", level=logging.ERROR)

# --------------------------------------------



