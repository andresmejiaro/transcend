# UI/UI_controller.py

import curses
import logging
import os
import sys
import time

from UI.input_bar.input_bar import InputBar
from UI.main_content.main_content import MainContent
from UI.nav_bar.nav_bar import NavBar
from utils.file_manager import FileManager
from utils.logger import log_message

class UIController:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.file_manager = FileManager()
        # self.nav_bar = NavBar(self.stdscr)
        # self.main_content = MainContent(self.stdscr)
        # self.input_bar = InputBar(self.stdscr)

    def handle_input(self, key):
        # Handle user input here
        if key == ord('q'):
            # Example: Quit the application if 'q' is pressed
            raise KeyboardInterrupt

    def display(self):
        # Display NavBar
        self.nav_bar.display()

        # Display Main Content
        self.main_content.display(f"Main Content: {self.counter}")

        # Display Input Bar
        self.input_bar.display(f"Input Bar: {self.counter}")

        # Update the screen
        self.stdscr.refresh()
