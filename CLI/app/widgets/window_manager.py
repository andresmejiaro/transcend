# app/widgets/window_manager.py

import os
import curses
import logging

from utils.logger import log_message
from app.widgets.windows import Window

class WindowManager:
    def __init__(self, stdscr):
        self.windows = []
        self.stdscr = stdscr

    def create_window(self, height, width, start_y, start_x):
        window = Window(self.stdscr, height, width, start_y, start_x)
        self.windows.append(window)
        return window

    def refresh_all_windows(self):
        for window in self.windows:
            window.refresh()