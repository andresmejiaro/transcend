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

            for frame_line in logo:
                self.stdscr.addstr(row, col, frame_line)
                row += 1

            # Adjust the delay to achieve the desired frame rate
            time.sleep(1 / frame_rate)

        except Exception as e:
            log_message(f"Error printing animated logo: {e}", level=logging.ERROR)

    def print_message_under_logo(self, message, logo):
        try:
            message_row = self.rows // 2 + len(logo) + 2
            message_col = self.cols // 2 - len(message) // 2

            self.stdscr.addstr(message_row, message_col, message)

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

    def print_input_prompt(self, prompt, input_string, index):
        try:
            prompt_row = self.rows // 2 + len(self.logo) + 2 + index  # Add spacing and index
            prompt_col = self.cols // 2 - len(prompt) // 2

            # Set the background color to highlight the current input field
            if index == self.current_input_index:
                self.stdscr.addstr(prompt_row, prompt_col, prompt, curses.A_REVERSE)
                self.stdscr.addstr(prompt_row, prompt_col + len(prompt), input_string, curses.A_REVERSE)
            else:
                self.stdscr.addstr(prompt_row, prompt_col, prompt)
                self.stdscr.addstr(prompt_row, prompt_col + len(prompt), input_string)

        except Exception as e:
            log_message(f"Error printing input prompt: {e}", level=logging.ERROR)