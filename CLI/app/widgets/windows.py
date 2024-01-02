# app/widgets/windows.py

import curses
from utils.logger import log_message

class Window:
    def __init__(self, stdscr, height, width, start_y, start_x):
        self.stdscr = stdscr
        self.window = curses.newwin(height, width, start_y, start_x)

    def refresh(self):
        self.window.refresh()

    def addstr(self, row, col, text, attr=0):
        try:
            self.window.addstr(row, col, text, attr)
        except curses.error as e:
            log_message(f"Error adding string at ({row}, {col}): {e}")
