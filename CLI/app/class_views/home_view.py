# app/views/home_page.py

import curses
import logging
import time
import json

from utils.logger import log_message
from utils.url_macros import LOBBY_URI_TEMPLATE
from utils.file_manager import FileManager
from utils.task_manager import TaskManager
from app.widgets.widgets import Widget

class HomePage(Widget):
    def __init__(self, stdscr, ui_controller, frame_rate):
        super().__init__(stdscr)

        self.file_manager = FileManager()
        self.task_manager = TaskManager()

        # Shared data between Tasks (Queues and Locks)
        self.ui_controller = ui_controller

        # Frame rate timing
        self.frame_rate = frame_rate

        # Next view to be displayed
        self.next_view = None

        # Online users
        self.online_users = {}

    def __str__(self):
        # Return a string representing the current view
        return "home"

# Update the screen        
    async def draw(self):
        try:
            self._clear_screen()

            self.frame_rate[0] = 30

            max_y, max_x = self.stdscr.getmaxyx()
            self.update_terminal_size()

            if self.rows < 30 or self.cols < 120:
                self.print_screen_too_small()
                return
            
            self.print_header("Home - Welcome to Pong!")

            self.print_current_time()

            user_input = await self.ui_controller.check_and_process_inputs()

            if user_input:
                log_message(f"User input: {user_input}", level=logging.DEBUG)
                self.process_input(user_input)               
        
            self.print_online_users(max_y, max_x)

            self._refresh_screen()

        except Exception as e:
            log_message(f"Error in draw: {e}", level=logging.ERROR)

    def get_next_view(self):
        return self.next_view
# -------------------------------------

# Input Processing Handler
    def process_input(self, user_input):
        try:
            # Inputs are recieved as a dictionary with the following format:
            # {"task_name": "task(lobby)", "data": "input_data"}
            # We will process the input based on the task name
            task_name = user_input.get("task_name")
            input_data = user_input.get("data")

            if task_name == "lobby":
                self.process_lobby_input(input_data)
            elif task_name == "keyboard":
                self.process_keyboard_input(input_data)


        except Exception as e:
            log_message(f"Error in process_input: {e}", level=logging.ERROR)
# -------------------------------------

# Input Processing Methods
    def process_lobby_input(self, lobby_input):
        try:
            log_message(f"Lobby Input from UI Controller: {lobby_input}", level=logging.DEBUG)

            if isinstance(lobby_input, str):
                message_data = json.loads(lobby_input)
            else:
                message_data = lobby_input

            message_type = message_data.get("type")
            data = message_data.get("data", {})

            if message_type == "user_joined":
                self.handle_user_joined(data)
            elif message_type == "user_left":
                self.handle_user_left(data)

        except Exception as e:
            log_message(f"Error in process_lobby_input: {e}", level=logging.ERROR)

    def process_keyboard_input(self, keyboard_input):
        try:
            # Here we format the message so the specific view can process it
            log_message(f"Keyboard Input from UI Controller: {keyboard_input}", level=logging.DEBUG)
            # We will format the info in a dictionary with the following format:
            # {"task_name": "keyboard", "data": keyboard_input}
            # We will process the input by getting the key code and converting it to the key name and then processing it

            # Convert the key code to the key name
            key_name = curses.keyname(keyboard_input).decode('utf-8')

            # For now just display the input on the screen
            self.stdscr.addstr(6, 0, str(key_name))  # Ensure input is converted to a string before display

        except Exception as e:
            log_message(f"Error in process_keyboard_input: {e}", level=logging.ERROR)
# -------------------------------------


# Send messages to websocket
    async def send_message(self, message):
        try:
            message = {"command": "list_of_users"}
            message = json.dumps(message)
            # Acquire the lock before accessing the queue
            async with self.list_of_shared_data["lobby"]["send_lock"]:
                await self.list_of_shared_data["lobby"]["send_queue"].put(message)

        except Exception as e:
            log_message(f"Error in send_message: {e}", level=logging.ERROR)
# -------------------------------------
            
# Lobby Methods
    def handle_user_joined(self, user_data):
        try:
            online_users = user_data.get("online_users")
            updated_users = dict(self.online_users)
            updated_users.update(online_users)
            self.online_users = updated_users

        except Exception as e:
            log_message(f"Error in handle_user_joined: {e}", level=logging.ERROR)

    def handle_user_left(self, user_data):
        try:
            left_user_id = user_data.get("client_id")
            updated_users = dict(self.online_users)
            updated_users.pop(left_user_id, None)
            self.online_users = updated_users

        except Exception as e:
            log_message(f"Error in handle_user_left: {e}", level=logging.ERROR)





# View Specific Methods - They should be structed with rows and columns in mind, so that they can be displayed in the terminal
    def print_online_users(self, max_y, max_x):
        try:
            # Print the online users
            row, col = 1, 0  # Starting position
            self.stdscr.addstr(row, col, "Online Users:")
            row += 1
            for index, username in enumerate(self.online_users.values(), start=1):
                # Check if there's enough space to print the next user
                if row < max_y:
                    self.stdscr.addstr(row, col, f"{index}. {username}")
                    row += 1
                else:
                    log_message("Not enough space to display all online users.", level=logging.WARNING)
                    break

        except Exception as e:
            log_message(f"Error printing online users: {e}", level=logging.ERROR)
# -------------------------------------



