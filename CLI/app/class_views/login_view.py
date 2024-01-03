# app/function_views/login_view.py

import logging
import curses
import time
import asyncio

from utils.logger import log_message
from network.http_api import http_api
from app.widgets.widgets import Widget
from utils.file_manager import FileManager
from utils.task_manager import TaskManager
# Next View
from app.class_views.home_view import HomePage

class Login(Widget):
    def __init__(self, stdscr, ui_controller, frame_rate):
        super().__init__(stdscr)
        self.http = http_api()
        self.file_manager = FileManager()
        self.task_manager = TaskManager()
        self.ui_controller = ui_controller
        self.logged_in = False

        self.logo = self.file_manager.load_texture("logo.txt")
        self.inputs = [{"name": "Username", "value": ""}, {"name": "Password", "value": ""}]
        self.current_input_index = 0
        self.error_message = None
        self.next_view = None
        self.frame_rate = frame_rate
    
    def __str__(self):
        # Return a string representing the current view
        return "login"
 
# Screen Updating
    async def draw(self):
        try:
            self._clear_screen()

            self.frame_rate[0] = 60

            self.update_terminal_size()

            if self.rows < 30 or self.cols < 120:
                self.print_screen_too_small()
                return
            
            self.print_header("Login")
            self.print_frame_rate()

            if self.logo:
                self.print_logo_centered(self.file_manager.load_texture("pong.txt"))

            user_input = await self.ui_controller.handle_keyboard_input_directly()

            if user_input:
                log_message(f"User input: {user_input}", level=logging.DEBUG)
                self.process_input(user_input)

            for i, input_data in enumerate(self.inputs):
                prompt = f"{input_data['name']}: "
                input_string = '*' * len(input_data['value'])
                if i == self.current_input_index:
                    # Highlight the current input field
                    prompt = f"{prompt}"
                self.display_prompt(prompt, input_string, i)

            self._refresh_screen()

        except Exception as e:
            log_message(f"Error updating screen: {e}", level=logging.ERROR)

    def get_next_view(self):
        return self.next_view
# -----------------------------

# Input Processing
    def process_input(self, user_input):
        current_input = self.inputs[self.current_input_index]

        if user_input == 10:
            if not current_input["value"]:
                self.error_message = f"{current_input['name']} cannot be empty!"
            else:
                self.current_input_index += 1
                if self.current_input_index == len(self.inputs):
                    if self.login() is False:
                        self.current_input_index = 0
                        for input_data in self.inputs:
                            input_data["value"] = ""
                        self.error_message = None
                    else:
                        self.logged_in = True
                        self.next_view = HomePage(self.stdscr, self.ui_controller, self.frame_rate)
                        return True
                else:
                    self.error_message = None  # Clear any previous error messages
        elif user_input == 263:
            current_input["value"] = current_input["value"][:-1]
        elif user_input and isinstance(user_input, int):
            # Only append if it's a printable character
            if 32 <= user_input <= 126:
                current_input["value"] += chr(user_input)
# -----------------------------


# View Specific Methods
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

# Login API Call
    def login(self):
        entered_data = {input_data["name"]: input_data["value"] for input_data in self.inputs}
        log_message(f"Entered Data: {entered_data}")

        response = self.http.login(entered_data["Username"], entered_data["Password"])
        log_message(f"Login response: {response}")

        if response:
            self.current_input_index = 0
            for input_data in self.inputs:
                input_data["value"] = ""
            self.error_message = None
            self.logged_in = True
            return True
        else:
            self.display_error_message("Login failed!")
            self.current_input_index = 0  # Reset the input index to the first field
            for input_data in self.inputs:
                input_data["value"] = ""  # Clear the input values
            self.error_message = None  # Clear the error message
            return False
# -----------------------------