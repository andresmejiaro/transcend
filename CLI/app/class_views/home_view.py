# app/views/home_page.py

import curses
import logging
import time
import json

from utils.logger import log_message

class HomePage():
    def __init__(self, stdscr, lobby_ws_data, keyboard_input_data):
        self.stdscr = stdscr

        # Queues and locks for sending and receiving messages
        self.messages_send_queue = lobby_ws_data["messages_send_queue"]
        self.messages_send_lock = lobby_ws_data["messages_send_lock"]
        self.messages_receive_queue = lobby_ws_data["messages_receive_queue"]
        self.receive_message_lock = lobby_ws_data["messages_receive_lock"]

        # Queue and lock for keyboard input
        self.keyboard_input_queue = keyboard_input_data["keyboard_input_queue"]
        self.keyboard_input_lock = keyboard_input_data["keyboard_input_lock"]
        
        # Frame rate timing
        self.last_frame_time = time.time()

        # Next view to be displayed
        self.next_view = None

        # Online users
        self.online_users = {}

# Core View Methods, these are called from app.py and updated based on the current view 
    
    # Update the screen        
    async def update_screen(self):
        try:
            self.stdscr.clear()

            # Set the background color for the entire window
            self.stdscr.bkgdset(' ', curses.color_pair(1))

            # Get the current terminal size
            max_y, max_x = self.stdscr.getmaxyx()

            # If the terminal is too small, display a message and return
            if max_y < 25 or max_x < 70:
                await self.print_screen_too_small(max_y, max_x)
                return
            
            await self.print_frame_rate(max_y, max_x)

            await self.print_header(max_y, max_x)

            await self.print_online_users(max_y, max_x)

            self.stdscr.refresh()

        except Exception as e:
            log_message(f"Error in update_screen: {e}", level=logging.ERROR)

    # Process received messages from the lobby ws
    async def process_lobby_recv_message(self):
        try:
            # First check if there are any messages in the queue
            if self.messages_receive_queue.empty():
                return

            # If there are messages, process them
            async with self.receive_message_lock:
                while not self.messages_receive_queue.empty():
                    message = await self.messages_receive_queue.get()
                    self.update_online_users(message)

        except Exception as e:
            log_message(f"Error in process_lobby_recv_message: {e}", level=logging.ERROR)
        
    # Process keyboard input
    async def process_inputs(self):
        try:
            # We receive keyboard input from the keyboard_input_queue so we can process it
            if self.keyboard_input_queue.empty():
                return
            
            # Acquire the lock before accessing the queue
            async with self.keyboard_input_lock:
                # Get the keyboard input
                input_data = await self.keyboard_input_queue.get()
                log_message(f'Processing input: {input_data}', level=logging.DEBUG)
                
                # For now just display the input on the screen
                self.stdscr.addstr(6, 0, str(input_data))  # Ensure input is converted to a string before display
        
        except Exception as e:
            log_message(f"Error in process_inputs: {e}", level=logging.ERROR)

    # When the view is changed, this method is called to set the next view           
    async def get_next_view(self):
        return self.next_view

    # Cleanup resources if needed, called when exiting the view
    async def cleanup(self):
        # Cleanup resources if needed
        pass
# -------------------------------------


# View Specific Methods - They should be structed with rows and columns in mind, so that they can be displayed in the terminal
    
    # Print the frame rate top right corner
    async def print_frame_rate(self, max_y, max_x):
        try:
            # Calculate frame rate and print it
            current_time = time.time()
            frame_rate = 1 / (current_time - self.last_frame_time)
            self.last_frame_time = current_time

            # Print the frame rate on the top right
            self.stdscr.addstr(0, max_x - 21, f"Frame Rate: {frame_rate:.2f} FPS", curses.color_pair(3) | curses.A_DIM | curses.A_BOLD)

        except Exception as e:
            log_message(f"Error printing frame rate: {e}", level=logging.ERROR)

    async def print_online_users(self, max_y, max_x):
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

    async def print_header(self, max_y, max_x):
        try:
            # Print the header centered
            header = "Welcome to Pong!"
            row, col = 0, max_x // 2 - len(header) // 2
            self.stdscr.addstr(row, col, header)
          
        except Exception as e:
            log_message(f"Error printing header: {e}", level=logging.ERROR)

    async def print_screen_too_small(self, max_y, max_x):
        try:
            # Print a message to the screen if the terminal is too small
            self.stdscr.addstr(0, 0, "Terminal is too small, please resize the terminal to at least 50x10.", curses.color_pair(3) | curses.A_BLINK | curses.A_UNDERLINE | curses.A_STANDOUT)

        except Exception as e:
            log_message(f"Error printing screen too small message: {e}", level=logging.ERROR)

# -------------------------------------


# Lobby Processing Methods
    def update_online_users(self, message):
        try:
            # Parse the received message as JSON
            message_data = json.loads(message)

            # Check if the message type is "user_joined" or "user_left"
            if message_data.get("type") == "user_joined" or message_data.get("type") == "user_left":
                user_data = message_data.get("data", {}).get("online_users", {})
                
                # If it's a "user_joined" message, update the online users dictionary with the new user data
                if message_data.get("type") == "user_joined":
                    self.online_users.update(user_data)
                # If it's a "user_left" message, remove the user from the online users dictionary
                elif message_data.get("type") == "user_left":
                    for client_id in user_data:
                        self.online_users.pop(client_id, None)

        except json.JSONDecodeError as e:
            log_message(f"Error decoding JSON: {e}", level=logging.ERROR)
        except Exception as e:
            log_message(f"Error updating online users: {e}", level=logging.ERROR)
