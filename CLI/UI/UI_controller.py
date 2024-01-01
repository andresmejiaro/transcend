# UI/UI_controller.py

import curses
import logging
import asyncio
import os
import sys
import time

from UI.UI_data import UIData  

from utils.task_manager import TaskManager
from utils.file_manager import FileManager
from utils.logger import log_message

class UIController:
    def __init__(self, stdscr, lobby_ws_data, keyboard_input_data):
        self.stdscr = stdscr
        self.file_manager = FileManager()
        self.task_manager = TaskManager()
        self.ui_data = UIData()

        # Shared data between Tasks (Queues and Locks)
        self.list_of_shared_data = {
            "lobby": lobby_ws_data,
            "keyboard": keyboard_input_data}
        
        self.input_handlers = {
            "lobby": self.handle_lobby_input,
            "keyboard": self.handle_keyboard_input,
        }

        # Frame rate timing
        self.last_frame_time = time.time()

        # Next view to be displayed
        self.next_view = None

        # self.nav_bar = NavBar(self.stdscr)
        # self.main_content = MainContent(self.stdscr)
        # self.input_bar = InputBar(self.stdscr)

# Entrypoing Method
    async def run(self):
        try:
            await self.update_screen()
            await self.process_inputs()

        except Exception as e:
            log_message(f"Error in run: {e}", level=logging.ERROR)

# Update Screen Methods
    def update_screen(self):
        # Display NavBar
        # self.nav_bar.display()

        # # Display Main Content
        # self.main_content.display()

        # # Display Input Bar
        # self.input_bar.display()

        # # Update the screen
        # self.stdscr.refresh()
        pass


# Process Input Methods
    async def check_and_process_inputs(self):
        try:
            while True:
                for shared_data_name, shared_data in self.list_of_shared_data.items():
                    if not shared_data["receive_queue"].empty():
                        input_data = shared_data["receive_queue"].get()
                        await self.handle_input(shared_data_name, input_data)

                await asyncio.sleep(0.015)

        except asyncio.CancelledError:
            log_message("UI Task cancelled", level=logging.DEBUG)

    async def handle_input(self, data_source, input_data):
        try:
            handler = self.input_handlers.get(data_source)

            if handler:
                await handler(input_data)
            else:
                log_message(f"Unknown data source: {data_source}", level=logging.WARNING)

        except Exception as e:
            log_message(f"Error in handle_input: {e}", level=logging.ERROR)





    def handle_lobby_input(self, lobby_input):
        # Your logic to process input from the lobby WebSocket
        # Example: Assuming lobby_input is a dictionary with a "message" key
        message = lobby_input.get("message")
        if message:
            # Process the message
            print(f"Lobby Message: {message}")

    def handle_keyboard_input(self, keyboard_input):
        # Your logic to process input from the keyboard
        # Example: Assuming keyboard_input is a string
        print(f"Keyboard Input: {keyboard_input}")
        # Perform actions based on the keyboard input


