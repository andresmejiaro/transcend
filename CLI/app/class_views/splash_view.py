# app/function_views/splash_view.py

import curses
import logging

from app.widgets.widgets import Widget
from utils.logger import log_message
from utils.file_manager import FileManager

class SplashView(Widget):
    def __init__(self, stdscr):
        super().__init__(stdscr)
        self.file_manager = FileManager()


    def display_splash_screen(self):
        try:
            # Load logo frames
            logo_frames = [self.file_manager.load_texture('logo.txt'), self.file_manager.load_texture('logo2.txt')]

            current_logo_frame = 0

            frame_rate = 2

            while True:
                self.stdscr.clear()

                # Get the terminal size
                self.update_terminal_size()

                if self.rows < 24 or self.cols < 80:
                    self.print_screen_too_small()
                    self.stdscr.refresh()
                    continue
            
                # Print frame rate
                self.print_frame_rate()

                # Print header
                self.print_header("Welcome to Pong!")

                # Print message under logo
                self.print_message_under_logo("Press any key to continue...", logo_frames[current_logo_frame])

                # Animation delay
                self.print_animated_logo(logo_frames[current_logo_frame], frame_rate)

                # Refresh the screen
                self.stdscr.refresh()

                # Switch to the next logo frame
                current_logo_frame = (current_logo_frame + 1) % len(logo_frames)

                # Refresh the screen
                self.stdscr.refresh()

                # Check for user input
                user_input = self.stdscr.getch()
                if user_input != curses.ERR:
                    break  # Break the loop when any key is pressed

        except Exception as e:
            log_message(f"Error displaying splash screen: {e}", level=logging.ERROR)
