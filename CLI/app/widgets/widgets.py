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

    def _clear_screen(self):
        self.stdscr.clear()

    def _refresh_screen(self):
        self.stdscr.refresh()

    def _addstr(self, row, col, text, attr=0):
        try:
            self.stdscr.addstr(row, col, text, attr)
            
        except curses.error as e:
            log_message(f"Error adding string at ({row}, {col}): {e}", level=logging.ERROR)

    def print_screen_too_small(self):
        self._clear_screen()
        self._addstr(0, 0, "Screen too small!", curses.color_pair(3) | curses.A_BOLD)
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

    def print_message_under_logo(self, message, logo):
        message_row = self.rows // 2 + len(logo) + 2
        message_col = self.cols // 2 - len(message) // 2

        if message_row < self.rows and message_col < self.cols:
            self._addstr(message_row, message_col, message)

    def print_frame_rate(self):
        try:
            current_time = time.time()
            frame_rate = 1 / (current_time - self.last_frame_time)
            self.last_frame_time = current_time

            self._addstr(0, self.cols - 21, f"Frame Rate: {frame_rate:.2f} FPS", curses.color_pair(3) | curses.A_DIM | curses.A_BOLD)

        except Exception as e:
            log_message(f"Error printing frame rate: {e}", level=logging.ERROR)

    def print_input_prompt(self, prompt, input_string, index):
        try:
            prompt_row = self.rows // 2 + len(self.logo) + 2 + index  # Add spacing and index
            prompt_col = self.cols // 2 - len(prompt) // 2

            # Set the background color to highlight the current input field
            if index == self.current_input_index:
                self._addstr(prompt_row, prompt_col, prompt, curses.A_REVERSE)
                self._addstr(prompt_row, prompt_col + len(prompt), input_string, curses.A_REVERSE)
            else:
                self._addstr(prompt_row, prompt_col, prompt)
                self._addstr(prompt_row, prompt_col + len(prompt), input_string)

        except Exception as e:
            log_message(f"Error printing input prompt: {e}", level=logging.ERROR)
