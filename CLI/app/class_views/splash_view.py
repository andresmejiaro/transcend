# app/function_views/splash_view.py

import curses
import logging
import asyncio
import urwid

from utils.logger import log_message

# View Imports
from app.widgets.widgets import Widget
# File Manager
from utils.file_manager import FileManager
# Task Manager
from utils.task_manager import TaskManager
# Next View
from app.class_views.login_view import Login

class SplashView(Widget):
    def __init__(self, stdscr):
        super().__init__(stdscr)
        self.file_manager = FileManager()
        self.task_manager = TaskManager()
        self.next_view = None

    async def run(self):
        try:
            self.update_terminal_size()

            if self.rows < 30 or self.cols < 80:
                self.print_screen_too_small()
                self.next_view = self
                return

            self.print_current_time()
            self.print_header("Welcome to Pong!")
            self.print_message_bottom("Press any key to continue...")

            user_input = self.get_user_input()
            if user_input == 10:
                self.next_view = Login(self.stdscr)
            else:
                self.next_view = self

            self.draw_screen()

        except Exception as e:
            log_message(f"Error displaying splash screen: {e}", level=logging.ERROR)
            self.next_view = self
            
    def get_next_view(self):
        return self.next_view
    
    def get_next_view(self):
        return self.next_view

    def get_user_input(self):
        # Replace this with your actual method to get user input
        # For example, you might want to check the keyboard input queue
        return None

    def __str__(self):
        # Return a string representing the current view
        return "splash"