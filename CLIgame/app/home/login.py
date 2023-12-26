# app/home/login.py

from utils.logger import log_message
import os
import curses  # Import curses for special keys

class Login:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.choices = ["LOGIN", "REGISTER", "EXIT"]
        self.selected_index = 0  # Index of the currently selected choice
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
        # Process user input for the login view
        if user_input == "KEY_UP":
            self.selected_index = (self.selected_index - 1) % len(self.choices)
        elif user_input == "KEY_DOWN":
            self.selected_index = (self.selected_index + 1) % len(self.choices)
        elif user_input == "KEY_ENTER" or user_input == "\n":
            choice = self.choices[self.selected_index]
            if choice == "LOGIN":
                # Handle login logic
                log_message("Selected LOGIN")
                # TODO: Add logic to transition to the next view after login
            elif choice == "REGISTER":
                # Handle register logic
                log_message("Selected REGISTER")
                # TODO: Add logic to transition to the next view after registration
            elif choice == "EXIT":
                # Handle exit logic
                log_message("Selected EXIT")
                # TODO: Add logic to exit the application

    def update_screen(self):
        # Update the screen for the login view
        self.stdscr.clear()

        if self.logo_frames:
            rows, cols = self.stdscr.getmaxyx()
            logo_row = max(0, (rows - len(self.logo_frames)) // 2)
            col = max(0, (cols - len(self.logo_frames[0])) // 2)
            for i, line in enumerate(self.logo_frames):
                self.stdscr.addstr(logo_row + i, col, line)

        # Display choices below the logo
        rows, cols = self.stdscr.getmaxyx()
        logo_row = max(0, (rows - len(self.logo_frames)) // 2)
        col = max(0, (cols - len(self.logo_frames[0])) // 2)

        # Calculate the total width required for the choices
        total_width = sum(len(choice) for choice in self.choices) + len(self.choices) - 1

        # Calculate the starting column position to center the choices
        start_col = max(0, (cols - total_width) // 2)

        for i, choice in enumerate(self.choices):
            if i == self.selected_index:
                # Highlight the selected choice
                self.stdscr.addstr(logo_row + len(self.logo_frames) + 1, start_col, choice, curses.A_REVERSE)
            else:
                self.stdscr.addstr(logo_row + len(self.logo_frames) + 1, start_col, choice)
            
            # Move the starting column position to the end of the previous choice
            start_col += len(choice) + 1  # Add 1 for spacing

    def get_next_view(self):
        # Implement logic to switch subviews if needed
        # For the login view, it may depend on the selected choice
        choice = self.choices[self.selected_index]
        if choice == "LOGIN":
            # Return the next view for login
            # Example: return HomeView(self.stdscr)
            pass
        elif choice == "REGISTER":
            # Return the next view for registration
            # Example: return RegisterView(self.stdscr)
            pass
        elif choice == "EXIT":
            # Return None or an ExitView if you have one
            # Example: return ExitView(self.stdscr)
            pass
