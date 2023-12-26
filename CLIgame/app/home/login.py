# app/home/login.py

from utils.logger import log_message
import logging
import os
import curses

class Login:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.logo = self.load_logo()
        self.next_view = None
        self.inputs = [{"name": "Username", "value": ""}, {"name": "Password", "value": ""}]
        self.current_input_index = 0
        self.error_message = None

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
        try:
            while True:
                key = self.stdscr.getch()

                if key == curses.KEY_ENTER or key in [10, 13]:
                    return "enter"
                elif key == 27:  # ESC key
                    return None
                elif key == curses.KEY_BACKSPACE:
                    return "backspace"
                elif key != -1:  # Ignore special keys with value -1
                    return key

        except Exception as e:
            log_message(f"Error getting user input: {e}", level=logging.ERROR)
            return None

    def process_input(self, user_input):
        current_input = self.inputs[self.current_input_index]

        if user_input == "enter":
            if not current_input["value"]:
                self.error_message = f"{current_input['name']} cannot be empty!"
            else:
                self.current_input_index += 1
                if self.current_input_index == len(self.inputs):
                    self.login()
                    return
                else:
                    self.error_message = None  # Clear any previous error messages
        elif user_input == "backspace":
            current_input["value"] = current_input["value"][:-1]
        elif user_input and isinstance(user_input, int):
            # Only append if it's a printable character
            if 32 <= user_input <= 126:
                current_input["value"] += chr(user_input)

    def update_screen(self):
        try:
            self.stdscr.clear()

            if self.logo:
                self.display_logo()

            for i, input_data in enumerate(self.inputs):
                self.display_prompt(f"{input_data['name']}: ", '*' * len(input_data['value']))

            # Display error message if exists
            if self.error_message:
                self.stdscr.addstr(len(self.inputs) + 2, 0, self.error_message, curses.color_pair(2))

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

    def display_prompt(self, prompt, input_string):
        rows, cols = self.stdscr.getmaxyx()
        logo_row = max(0, (rows - len(self.logo)) // 2)
        prompt_row = logo_row + len(self.logo) + 2  # Add spacing
        prompt_col = max(0, (cols - len(prompt)) // 2)

        self.stdscr.addstr(prompt_row, prompt_col, prompt)
        self.stdscr.addstr(prompt_row, prompt_col + len(prompt), input_string)
# -----------------------------

# Login API Call
    def login(self):
        # Placeholder for login logic
        # For now, let's just print the entered data
        entered_data = {input_data["name"]: input_data["value"] for input_data in self.inputs}
        log_message(f"Entered Data: {entered_data}")

        # Set the next view if needed
        # For example, self.next_view = HomeView(self.stdscr)
        pass


