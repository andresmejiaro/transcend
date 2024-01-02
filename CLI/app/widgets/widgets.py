# app/widgets/widgets.py

import curses
import time
import logging

from utils.logger import log_message
from utils.file_manager import FileManager

class Widget:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.file_manager = FileManager()
        self.last_frame_time = time.time()
        self.update_terminal_size()
        
        self.color_counter = 1

    def update_terminal_size(self):
        try:
            self.rows, self.cols = self.stdscr.getmaxyx()
            
        except Exception as e:
            log_message(f"Error getting terminal size: {e}", level=logging.ERROR)

    def _clear_screen(self):
        self.stdscr.clear()

    def _refresh_screen(self):
        self.stdscr.refresh()

    def _addstr(self, row, col, text, attr=0):
        try:
            self.stdscr.addstr(row, col, text, attr)
            
        except curses.error as e:
            log_message(f"Error adding string at ({row}, {col}): {e}", level=logging.ERROR)

    def print_logo_centered(self, logo):
        logo_height = len(logo)
        logo_width = len(logo[0])

        row = self.rows // 2 - logo_height // 2
        col = self.cols // 2 - logo_width // 2

        for frame_line in logo:
            self._addstr(row, col, frame_line, curses.color_pair(self.color_counter))
            row += 1

        # Increment the color counter for the next call
        self.color_counter = (self.color_counter % 6) + 1

    def print_screen_too_small(self, size_required=(30, 120)):
        self._clear_screen()
        self._addstr(0, 0, f"Screen too small! Please resize to at least {size_required[0]} rows and {size_required[1]} columns.", curses.color_pair(3) | curses.A_BLINK)
        self._refresh_screen()

    def print_header(self, header):
        col = self.cols // 2 - len(header) // 2
        self._addstr(1, col, header)

    def print_animated_logo(self, logo, frame_rate):
        logo_height = len(logo)
        logo_width = len(logo[0])

        row = self.rows // 2 - logo_height // 2
        col = self.cols // 2 - logo_width // 2

        for frame_line in logo:
            self._addstr(row, col, frame_line)
            row += 1

        time.sleep(1 / frame_rate)

    def print_message_bottom(self, message):
        # Print message 1 row above the bottom of the screen
        row = self.rows - 2
        col = self.cols // 2 - len(message) // 2
        self._addstr(row, col, message, curses.color_pair(6) | curses.A_DIM | curses.A_BOLD | curses.A_BLINK)

    def print_frame_rate(self):
        try:
            current_time = time.time()
            frame_rate = 1 / (current_time - self.last_frame_time)
            self.last_frame_time = current_time

            self._addstr(1, self.cols - 21, f"Frame Rate: {frame_rate:.2f} FPS", curses.color_pair(3) | curses.A_DIM | curses.A_BOLD)

        except Exception as e:
            log_message(f"Error printing frame rate: {e}", level=logging.ERROR)

    def print_current_time(self):
        try:
            current_time = time.strftime("%H:%M:%S")
            self._addstr(0, self.cols - 22, f"Current Time: {current_time}", curses.color_pair(3) | curses.A_DIM | curses.A_BOLD)

        except Exception as e:
            log_message(f"Error printing current time: {e}", level=logging.ERROR)