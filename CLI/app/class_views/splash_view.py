# app/function_views/splash_view.py

import logging
import asyncio

from utils.logger import log_message
from utils.file_manager import FileManager
from app.widgets.widgets import Widget
from app.class_views.home_view import HomePage


class SplashView(Widget):
    def __init__(self, stdscr, ui_controller, frame_rate, process_speed, task_manager):
        super().__init__(stdscr)
        self.ui_controller = ui_controller
        self.file_manager = FileManager()
        self.task_manager = task_manager
        self.next_view = None
        self.frame_rate = frame_rate
        self.process_speed = process_speed

    def __str__(self):
        # Return a string representing the current view
        return "splash"


    # Keyboard Input Handler
    async def process_keyboard_input(self, keyboard_input):
        try:
            log_message(f"Keyboard Input from UI Controller: {keyboard_input}", level=logging.DEBUG)
            if keyboard_input == 27:
                self.next_view = "exit"
            elif keyboard_input == 32:
                self.next_view = HomePage(self.stdscr, self.ui_controller, self.frame_rate, self.process_speed, self.task_manager)
            else:
                self.next_view = self
                
        except Exception as e:
            log_message(f"Error processing keyboard input: {e}", level=logging.ERROR)
            self.next_view = self
        
    # Screen Updating
    async def draw(self):
        try:
            self.frame_rate[0] = 1

            self._clear_screen()

            self.update_terminal_size()

            if self.rows < 30 or self.cols < 120:
                self.print_screen_too_small()
                return

            self.print_current_time()
            self.print_frame_rate()
            self.print_header("Welcome to Pong!")
            self.print_logo_centered(self.file_manager.load_texture("pong.txt"))
            self.print_message_bottom("Press space to continue...")

            self._refresh_screen()

        except Exception as e:
            log_message(f"Error displaying splash screen: {e}", level=logging.ERROR)
            self.next_view = self
    
    # Input Processing
    async def process_input(self):
        self.process_speed[0] = 1
            
    # Next View
    def get_next_view(self):
        return self.next_view

    # Cleanup
    def cleanup(self):
        pass
# -----------------------------
