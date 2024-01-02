# app/function_views/splash_view.py

import logging

# Utility Imports
from utils.logger import log_message
from utils.file_manager import FileManager
# View Imports
from app.widgets.widgets import Widget
# Next View
from app.class_views.login_view import Login

class SplashView(Widget):
    def __init__(self, stdscr, ui_controller, frame_rate):
        super().__init__(stdscr)
        self.ui_controller = ui_controller
        self.file_manager = FileManager()
        self.next_view = None
        self.frame_rate = frame_rate

    def __str__(self):
            # Return a string representing the current view
            return "splash"

# Screen Updating
    async def draw(self):
        try:
            self.frame_rate[0] = 30

            self._clear_screen()

            self.update_terminal_size()

            if self.rows < 30 or self.cols < 120:
                self.print_screen_too_small()
                return

            # self.print_current_time()
            self.print_frame_rate()
            self.print_header("Welcome to Pong!")
            self.print_logo_centered(self.file_manager.load_texture("pong.txt"))
            self.print_message_bottom("Press any key to continue...")

            user_input = await self.ui_controller.handle_keyboard_input_directly()
            if user_input == 32:
                log_message(f"Splash screen user input: {user_input}", level=logging.DEBUG)
                self.next_view = Login(self.stdscr, self.ui_controller, self.frame_rate)

            self._refresh_screen()

        except Exception as e:
            log_message(f"Error displaying splash screen: {e}", level=logging.ERROR)
            self.next_view = self
            
    def get_next_view(self):
        return self.next_view
# -----------------------------