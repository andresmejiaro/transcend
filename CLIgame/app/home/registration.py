# app/home/registration.py

import os
import curses
import logging
from utils.logger import log_message

class Registration:
    def __init__(self, stdscr, http, ws):
        self.stdscr = stdscr
        self.choices = ["LOGIN", "REGISTER"]
        self.selected_index = 0  # Index of the currently selected choice
        self.logo = self.load_logo()
        self.next_view = None
        self.http = http
        self.ws = ws

    def load_logo(self):
        file_path = os.path.join(os.path.dirname(__file__), "textures", "logo.txt")
        try:
            with open(file_path, "r") as logo_file:
                return logo_file.read().splitlines()
        except FileNotFoundError as e:
            log_message(f"Error loading logo frames: {e}", level=logging.ERROR)
            return None
        except Exception as e:
            log_message(f"Error loading logo frames: {e}", level=logging.ERROR)
            return None

    async def get_user_input(self):
        # Get user input for the login view
        try:
            key = self.stdscr.getch()
            if key == curses.KEY_LEFT:
                return "left"
            elif key == curses.KEY_RIGHT:
                return "right"
            elif key == curses.KEY_ENTER or key in [10, 13]:
                return "enter"
            elif key == 27:  # ESC key
                return None
            elif key != -1:  # Ignore special keys with value -1
                return key
            
        except Exception as e:
            log_message(f"Error getting user input: {e}", level=logging.ERROR)
            return None

    def process_input(self, user_input, all_views):
        # Process user input for the login view
        if user_input == "left":
            self.selected_index = (self.selected_index - 1) % len(self.choices)
        elif user_input == "right":
            self.selected_index = (self.selected_index + 1) % len(self.choices)
        elif user_input == "enter":
                login = next(view_data for view_data in all_views if view_data["name"] == "Login")
                register = next(view_data for view_data in all_views if view_data["name"] == "Register")
                self.next_view = login["view"] if self.selected_index == 0 else register["view"]
                
    def update_screen(self):
        try:
            self.stdscr.clear()

            if self.logo:
                self.display_logo()

            self.display_choices()
            self.display_additional_info()

            self.stdscr.refresh()

        except Exception as e:
            log_message(f"Error updating screen: {e}", level=logging.ERROR)

    def get_next_view(self):
        return self.next_view

# Display Helper Methods
    def display_logo(self):
        rows, cols = self.stdscr.getmaxyx()
        logo_row = max(0, (rows - len(self.logo)) // 2)
        col = max(0, (cols - len(self.logo[0])) // 2)
        for i, line in enumerate(self.logo):
            self.stdscr.addstr(logo_row + i, col, line)

    def display_choices(self):
        rows, cols = self.stdscr.getmaxyx()
        logo_row = max(0, (rows - len(self.logo)) // 2)

        # Calculate the total width required for the choices
        total_width = sum(len(choice) for choice in self.choices) + len(self.choices) - 1

        # Calculate the starting column position to center the choices
        start_col = max(0, (cols - total_width) // 2)

        # Add additional spacing between LOGIN and REGISTER
        start_col += 2  # You can adjust this value for more or less spacing

        for i, choice in enumerate(self.choices):
            self.display_choice(logo_row, start_col, choice, i == self.selected_index)
            start_col += len(choice) + 1  # Add 1 for spacing

    def display_choice(self, logo_row, start_col, choice, is_selected):
        # Helper function to display an individual choice
        if is_selected:
            self.stdscr.addstr(logo_row + len(self.logo) + 1, start_col, choice, curses.A_REVERSE)
        else:
            self.stdscr.addstr(logo_row + len(self.logo) + 1, start_col, choice)

    def display_additional_info(self):
        rows, cols = self.stdscr.getmaxyx()
        logo_row = max(0, (rows - len(self.logo)) // 2)

        # Display additional information at the bottom of the screen
        bottom_message = "Or press ESC to exit..."
        bottom_row = logo_row + len(self.logo) + 3  # Add spacing
        col = max(0, (cols - len(bottom_message)) // 2)
        self.stdscr.addstr(bottom_row, col, bottom_message)
# ---------------------------------------------

