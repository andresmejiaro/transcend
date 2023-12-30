# app/widgets/widgets.py

import curses
import time
from utils.logger import log_message
import logging

class Widget:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.last_frame_time = time.time()
        self.update_terminal_size()

    def update_terminal_size(self):
        self.rows, self.cols = self.stdscr.getmaxyx()

    def print_screen_too_small(self):
        try:
            self.stdscr.clear()
            self.stdscr.addstr(0, 0, "Screen too small!", curses.color_pair(3) | curses.A_BOLD)
            self.stdscr.refresh()

        except Exception as e:
            log_message(f"Error printing screen too small message: {e}", level=logging.ERROR)

    def print_header(self, header):
        try:
            row, col = 1, self.cols // 2 - len(header) // 2
            self.stdscr.addstr(row, col, header)

        except Exception as e:
            log_message(f"Error printing header: {e}", level=logging.ERROR)

    def print_animated_logo(self, logo, frame_rate):
        try:
            logo_height = len(logo)
            logo_width = len(logo[0])

            row = self.rows // 2 - logo_height // 2
            col = self.cols // 2 - logo_width // 2

            for frame in logo:
                self.stdscr.addstr(row, col, frame)
                row += 1

            # Adjust the delay to achieve the desired frame rate
            time.sleep(1 / frame_rate)

        except Exception as e:
            log_message(f"Error printing animated logo: {e}", level=logging.ERROR)

    def print_message_under_logo(self, message):
        try:
            message_row = self.rows // 2 + 2
            message_col = self.cols // 2 - len(message) // 2

            self.stdscr.addstr(message_row, message_col, message, curses.color_pair(3) | curses.A_BOLD)

        except Exception as e:
            log_message(f"Error printing message under logo: {e}", level=logging.ERROR)

    def print_frame_rate(self):
        try:
            current_time = time.time()
            frame_rate = 1 / (current_time - self.last_frame_time)
            self.last_frame_time = current_time

            self.stdscr.addstr(0, self.cols - 21, f"Frame Rate: {frame_rate:.2f} FPS", curses.color_pair(3) | curses.A_DIM | curses.A_BOLD)

        except Exception as e:
            log_message(f"Error printing frame rate: {e}", level=logging.ERROR)
