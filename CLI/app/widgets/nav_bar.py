# app/widgets/nav_bar.py

import curses
import logging
import time
from datetime import datetime

from utils.logger import log_message
from app.widgets.widgets import Widget

class NavBar(Widget):
    def __init__(self, stdscr, items):
        super().__init__(stdscr)
        self.items = items
        self.selected_item = 0

    def __str__(self):
        return "nav_bar"
    
    def draw(self):
        # Draw items
        for index, item in enumerate(self.items):
            if index == self.selected_item:
                # Highlight the selected item
                self._addstr(0, index * (self.cols // len(self.items)), f"{item}", curses.A_REVERSE)
            else:
                self._addstr(0, index * (self.cols // len(self.items)), f"{item}")

        # Display current time on the right side
        current_time = datetime.now().strftime("%H:%M:%S")
        self._addstr(0, self.cols - len(current_time), current_time)

    def handle_input(self, key):
        if key == curses.KEY_RIGHT and self.selected_item < len(self.items) - 1:
            self.selected_item += 1
        elif key == curses.KEY_LEFT and self.selected_item > 0:
            self.selected_item -= 1

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):
        self.items.remove(item)

    def get_selected_item(self):
        return self.items[self.selected_item]
