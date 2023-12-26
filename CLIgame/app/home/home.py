# app/home/home.py

from utils.logger import log_message
from app.home.splash_screen import SplashScreen
from app.home.login import Login
from app.home.register import Register
import time

class Home:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.current_subview = SplashScreen(stdscr)
        self.refresh_rate = 0.5  # Adjust the refresh rate as needed
        self.last_refresh_time = time.time()

    def process_input(self, user_input):
        # Process user input for the home view
        # Delegate input processing to the current subview if available
        if self.current_subview:
            next_subview = self.current_subview.process_input(user_input)
            if next_subview:
                # If the subview returns the next subview, update it
                self.current_subview = next_subview

    def update_screen(self):
        # Update the screen for the home view
        # Delegate screen updating to the current subview if available
        if self.current_subview:
            self.current_subview.update_screen()

        # Check if it's time to refresh the screen
        current_time = time.time()
        if current_time - self.last_refresh_time >= self.refresh_rate:
            self.stdscr.refresh()  # Refresh the screen
            self.last_refresh_time = current_time

    def get_next_view(self):
        # Implement logic to switch subviews if needed
        # For example, you might transition to another subview after a certain condition
        return None  # For now, don't switch to another view immediately
