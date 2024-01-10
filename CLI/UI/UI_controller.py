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

        self.input_handlers = {
            "lobby": self.handle_lobby_input,
            "keyboard": self.handle_keyboard_input,
            "game": self.handle_game_input,
        }

    def __str__(self):
        return "ui_controller"
    
    def cleanup(self):
        self.list_of_shared_data = {}

# Process Input Methods
    async def check_and_process_inputs(self):
        try:
            for shared_data_name, shared_data in self.list_of_shared_data.items():
                try:
                    # Try to get an item from the queue
                    input_data = shared_data["receive_queue"].get_nowait()

                    # If successful, process the input
                    log_message(f"Processing input from {shared_data_name}", level=logging.DEBUG)
                    log_message(f"Input data: {input_data}", level=logging.DEBUG)
                    processed_inputs = await self.handle_input(shared_data_name, input_data)

                    # If the input was processed, return it
                    if processed_inputs:
                        return processed_inputs
                    else:
                        return "Queues Empty"

                except asyncio.QueueEmpty:
                    # Queue is empty, continue to the next shared_data
                    pass
                    
        except Exception as e:
            log_message(f"Error in check_and_process_inputs: {e}", level=logging.ERROR)

    async def check_and_process_inputs_filterd(self, inputs_to_check=[]):
        try:
            for shared_data_name, shared_data in self.list_of_shared_data.items():
                try:
                    # Try to get an item from the queue
                    input_data = shared_data["receive_queue"].get_nowait()

                    # If successful, process the input
                    log_message(f"Processing input from {shared_data_name}", level=logging.DEBUG)
                    log_message(f"Input data: {input_data}", level=logging.DEBUG)
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
        
    


    async def handle_input(self, data_source, input_data):
        try:
            handler = self.input_handlers.get(data_source)

            if handler:
                log_message(f"Handling input from {data_source}", level=logging.DEBUG)
                processed_inputs = await handler(input_data)
                return processed_inputs
            else:
                log_message(f"Unknown data source: {data_source}", level=logging.WARNING)

        except Exception as e:
            log_message(f"Error in handle_input: {e}", level=logging.ERROR)



# Auto Update Methods
    async def handle_lobby_input(self, lobby_input):
        try:
            # Here we format the message so the specific view can process it
            log_message(f"Lobby Input from UI Controller: {lobby_input}", level=logging.DEBUG)
            # We will format the info in a dictionary with the following format:
            # {"task_name": "lobby", "message": lobby_input}
            return {"task_name": "lobby", "data": lobby_input}
        
        except Exception as e:
            log_message(f"Error in handle_lobby_input: {e}", level=logging.ERROR)

    async def handle_lobby_output(self, message):
        try:
            # Send the message to the server
            log_message(f"Sending message to server: {message}", level=logging.DEBUG)
            await self.list_of_shared_data["lobby"]["send_queue"].put(message)
        
        except Exception as e:
            log_message(f"Error in send_message_to_server: {e}", level=logging.ERROR)

    async def handle_game_input(self, game_input):
        try:
            # Here we format the message so the specific view can process it
            log_message(f"Lobby Input from UI Controller: {game_input}", level=logging.DEBUG)
            # We will format the info in a dictionary with the following format:
            # {"task_name": "lobby", "message": lobby_input}
            return {"task_name": "game", "data": game_input}
        
        except Exception as e:
            log_message(f"Error in handle_game_input: {e}", level=logging.ERROR)        

    async def handle_game_output(self, message):
        try:
            # Send the message to the server
            log_message(f"Sending message to server: {message}", level=logging.DEBUG)
            await self.list_of_shared_data["game"]["send_queue"].put(message)
        
        except Exception as e:
            log_message(f"Error in send_message_to_server: {e}", level=logging.ERROR)
    
   
# Auto Update Methods - Beta    
    async def get_message_from_websocket(self, ws_name):
        try:
            # We receive websocket input from the receive_queue so we can process it
            if self.list_of_shared_data[ws_name]["receive_queue"].empty():
                return None
            
            # Acquire the lock before accessing the queue
            async with self.list_of_shared_data[ws_name]["receive_lock"]:
                # Get the websocket input
                input_data = await self.list_of_shared_data[ws_name]["receive_queue"].get()
                return input_data
        
        except Exception as e:
            log_message(f"Error in handle_websocket_input: {e}", level=logging.ERROR)
   
    async def send_message_to_websocket(self, ws_name, message):
        try:
            # Add message to the send_queue of the websocket
            log_message(f"Sending message to {ws_name}: {message}", level=logging.DEBUG)
            await self.list_of_shared_data[ws_name]["send_queue"].put(message)
            
        except Exception as e:
            log_message(f"Error in send_message_to_websocket: {e}", level=logging.ERROR)
    
    async def handle_keyboard_input(self, keyboard_input):
        try:
            # Here we format the message so the specific view can process it
            log_message(f"Keyboard Input from UI Controller: {keyboard_input}", level=logging.DEBUG)
            # We will format the info in a dictionary with the following format:
            return {"task_name": "keyboard", "data": keyboard_input}
        
        except Exception as e:
            log_message(f"Error in handle_keyboard_input: {e}", level=logging.ERROR)

# ---------------------------------------------

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
    
