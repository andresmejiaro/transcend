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
    def __init__(self, stdscr, task_manager):
        self.stdscr = stdscr
        self.file_manager = FileManager()
        self.task_manager = task_manager

        # Shared data between Tasks (Queues and Locks)
        self.list_of_shared_data = {}

    def __str__(self):
        return "ui_controller"
    
    def cleanup(self):
        self.list_of_shared_data = {}

# Process Input Methods
    async def check_and_process_inputs_filterd(self, inputs_to_check=[]):
        try:
            for shared_data_name, shared_data in self.list_of_shared_data.items():
                try:
                    # Try to get an item from the queue
                    input_data = shared_data["receive_queue"].get_nowait()

                    # If successful, process the input
                    # log_message(f"Processing input from {shared_data_name}", level=logging.DEBUG)
                    # log_message(f"Input data: {input_data}", level=logging.DEBUG)
                    # processed_inputs = await self.handle_input(shared_data_name, input_data)
                    processed_inputs = {"task_name": shared_data_name, "data": input_data}

                    # If the input was processed, return it
                    if processed_inputs:
                        if processed_inputs["task_name"] in inputs_to_check:
                            return processed_inputs
                    else:
                        return "Queues Empty"

                except asyncio.QueueEmpty:
                    # Queue is empty, continue to the next shared_data
                    pass
                
        except Exception as e:
            log_message(f"Error in check_and_process_inputs: {e}", level=logging.ERROR)
     
# Use to handle keyboard input directly from the UI Controller without processing all other inputs for use with no ws views
    async def handle_keyboard_input_directly(self):
        try:
            # We receive keyboard input from the receive_queue so we can process it
            if self.list_of_shared_data["keyboard"]["receive_queue"].empty():
                return None
            
            # Acquire the lock before accessing the queue
            async with self.list_of_shared_data["keyboard"]["receive_lock"]:
                # Get the keyboard input
                input_data = await self.list_of_shared_data["keyboard"]["receive_queue"].get()
                return input_data
        
        except Exception as e:
            log_message(f"Error in handle_keyboard_input: {e}", level=logging.ERROR)



# Shared Data Methods
    def add_shared_data(self, name, shared_data):
        log_message(f"Adding shared data: {name}", level=logging.DEBUG)
        self.list_of_shared_data[name] = shared_data
        log_message(f"Shared data added: {self.list_of_shared_data}", level=logging.DEBUG)

    def remove_shared_data(self, name):
        del self.list_of_shared_data[name]

    def get_shared_data(self, name):
        return self.list_of_shared_data[name]
    
    def get_all_shared_data(self):
        return self.list_of_shared_data
    
    def get_shared_data_names(self):
        return self.list_of_shared_data.keys()
  # ---------------------------------------------
    
