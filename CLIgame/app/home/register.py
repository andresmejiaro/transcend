# app/home/register.py

from utils.logger import log_message
import logging
import os
import curses
import time

class Register:
    def __init__(self, stdscr, http, ws):
        self.stdscr = stdscr
        self.logo = self.load_logo()
        self.next_view = None
        self.inputs = [
            {"name": "Username", "value": ""},
            {"name": "Password", "value": ""},
            {"name": "FullName", "value": ""},
            {"name": "Email   ", "value": ""},
            ]
        self.current_input_index = 0
        self.error_message = None
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

    def process_input(self, user_input, all_views):
        current_input = self.inputs[self.current_input_index]

        if user_input == "enter":
            if not current_input["value"]:
                self.error_message = f"{current_input['name']} cannot be empty!"
            else:
                self.current_input_index += 1
                if self.current_input_index == len(self.inputs):
                    if self.Register(all_views) is False:
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
                prompt = f"{input_data['name']}: "
                input_string = '*' * len(input_data['value'])
                if i == self.current_input_index:
                    # Highlight the current input field
                    prompt = f"{prompt}"
                self.display_prompt(prompt, input_string, i)

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

    def display_prompt(self, prompt, input_string, index):
        rows, cols = self.stdscr.getmaxyx()
        logo_row = max(0, (rows - len(self.logo)) // 2)
        prompt_row = logo_row + len(self.logo) + 2 + index  # Add spacing and index
        prompt_col = max(0, (cols - len(prompt)) // 2)

        # Set the background color to highlight the current input field
        if index == self.current_input_index:
            self.stdscr.addstr(prompt_row, prompt_col, prompt, curses.A_REVERSE)
            self.stdscr.addstr(prompt_row, prompt_col + len(prompt), input_string, curses.A_REVERSE)
        else:
            self.stdscr.addstr(prompt_row, prompt_col, prompt)
            self.stdscr.addstr(prompt_row, prompt_col + len(prompt), input_string)

    def display_error_message(self, message):
        rows, cols = self.stdscr.getmaxyx()

        # Calculate the position for the error message below the logo and inputs
        logo_height = len(self.logo) if self.logo else 0
        error_row = max(0, (rows - logo_height - len(self.inputs)) // 2) + logo_height + len(self.inputs) + 4
        error_col = max(0, (cols - len(message)) // 2)

        # Display the error message in the center of the screen
        self.stdscr.addstr(error_row, error_col, message)
        self.stdscr.refresh()

        # Pause for a moment (adjust sleep duration as needed)
        time.sleep(2)
# -----------------------------

# Register API Call
    def Register(self, all_views):
        entered_data = {input_data["name"]: input_data["value"] for input_data in self.inputs}
        log_message(f"Entered Data: {entered_data}")

        response = self.http.register(entered_data["Username"], entered_data["Password"], entered_data["FullName"], entered_data["Email   "])

        log_message(f"Register response: {response}")

        if response:
            next_view = next(view_data for view_data in all_views if view_data["name"] == "Home")
            self.next_view = next_view["view"]
        else:
            self.display_error_message("Register failed!")
            self.current_input_index = 0  # Reset the input index to the first field
            for input_data in self.inputs:
                input_data["value"] = ""  # Clear the input values
            self.error_message = None  # Clear the error message
            self.update_screen()  
