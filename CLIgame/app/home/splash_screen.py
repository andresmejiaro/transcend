# app/home/splash_screen.py

from utils.logger import log_message
import time
import os
from app.home.login import Login  # Import the Login view

class SplashScreen:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.next_view = None
        self.logo_frames = self.load_logo_frames()

    def load_logo_frames(self):
        # Update the file path to your ASCII logo file
        file_path = os.path.join(os.path.dirname(__file__), "textures", "logo.txt")
        try:
            with open(file_path, "r") as logo_file:
                return logo_file.read().splitlines()  # Split lines for multi-line logo
        except FileNotFoundError:
            log_message(f"Logo file not found at: {file_path}")
            return None

    def process_input(self, user_input):
        # Process user input for the splash screen
        if user_input:
            # Set the next view to Login when the user presses Enter
            self.next_view = Login(self.stdscr)

    def update_screen(self):
        # Update the screen for the splash screen
        self.stdscr.clear()

        # Display the logo centered on the screen
        if self.logo_frames:
            rows, cols = self.stdscr.getmaxyx()
            logo_row = max(0, (rows - len(self.logo_frames)) // 2)
            col = max(0, (cols - len(self.logo_frames[0])) // 2)
            for i, line in enumerate(self.logo_frames):
                self.stdscr.addstr(logo_row + i, col, line)

        # Display a static message right under the logo
        message = "Welcome to the Game!\nPress Enter to start..."
        rows, cols = self.stdscr.getmaxyx()
        text_row = logo_row + len(self.logo_frames) + 1  # Add 1 for spacing
        col = max(0, (cols - len(message.splitlines()[0])) // 2)
        for i, line in enumerate(message.splitlines()):
            self.stdscr.addstr(text_row + i, col, line)

    def get_next_view(self):
        # Implement logic to switch views if needed
        # For the splash screen, you might want to transition after a certain time
        # return self.home  # Transition to the home view
        return self.next_view
