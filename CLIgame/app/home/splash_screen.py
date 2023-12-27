# app/home/splash_screen.py

from app.home.registration import Registration
from utils.logger import log_message
import logging
import time
import os

class SplashScreen:
    def __init__(self, stdscr, http, ws):
        self.stdscr = stdscr
        self.next_view = None
        self.logo = self.load_logo()
        self.http = http
        self.ws = ws

    def load_logo(self):
        file_path = os.path.join(os.path.dirname(__file__), "textures", "logo.txt")
        try:
            with open(file_path, "r") as logo_file:
                return logo_file.read().splitlines()
        except FileNotFoundError as e:
            log_message(f"Error loading logo frames: {e}")
            return None
        except Exception as e:
            log_message(f"Error loading logo frames: {e}")
            return None

    async def get_user_input(self):
        user_input = self.stdscr.getch()
        return user_input

    def process_input(self, user_input, all_views):
        try:
            # Process user input for the splash screen
            if user_input:
                # Set the next view to Login when the user presses Enter
                next_view = next(view_data for view_data in all_views if view_data["name"] == "Registration")
                self.next_view = next_view["view"]

        except Exception as e:
            log_message(f"Error processing input: {e}")

    def update_screen(self):
        try:
            # Update the screen for the splash screen
            self.stdscr.clear()

            # Display the logo centered on the screen
            if self.logo:
                rows, cols = self.stdscr.getmaxyx()
                logo_row = max(0, (rows - len(self.logo)) // 2)
                col = max(0, (cols - len(self.logo[0])) // 2)
                for i, line in enumerate(self.logo):
                    self.stdscr.addstr(logo_row + i, col, line)

            # Display a static message right under the logo
            message = "Welcome to the Game!\nPress Enter to start..."
            rows, cols = self.stdscr.getmaxyx()
            text_row = logo_row + len(self.logo) + 1  # Add 1 for spacing
            col = max(0, (cols - len(message.splitlines()[0])) // 2)
            for i, line in enumerate(message.splitlines()):
                self.stdscr.addstr(text_row + i, col, line)

        except Exception as e:
            log_message(f"Error updating splash screen: {e}")

    def get_next_view(self):
        # Implement logic to switch views if needed
        # For the splash screen, you might want to transition after a certain time
        # return self.home  # Transition to the home view
        return self.next_view
