# app/views/home_page.py

import curses
import logging
import asyncio
import time

from utils.logger import log_message

class HomePage():
    def __init__(self, stdscr, messages_send_queue, messages_receive_queue, send_message_lock, receive_message_lock, keyboard_input_queue, keyboard_input_lock):
        self.stdscr = stdscr

        self.messages_send_queue = messages_send_queue
        self.messages_receive_queue = messages_receive_queue
        self.keyboard_input_queue = keyboard_input_queue

        self.send_message_lock = send_message_lock
        self.receive_message_lock = receive_message_lock
        self.keyboard_input_lock = keyboard_input_lock

        self.last_frame_time = time.time()

        self.next_view = None

# Core View Methods, these are called from app.py and updated based on the current view
        
# Update the screen        
    async def update_screen(self):
        try:
            self.stdscr.clear()

            self.stdscr.addstr(0, 0, "Welcome to the Home Page!")
            self.stdscr.addstr(2, 0, "Press any key to continue...")
            
            # Display received messages
            self.stdscr.addstr(4, 0, "Received Messages:")

            # Display the frame rate
            await self.print_frame_rate()

            self.stdscr.refresh()

        except Exception as e:
            log_message(f"Error in update_screen: {e}", level=logging.ERROR)

# Process received messages from the lobby ws
    async def process_lobby_recv_message(self):
        try:
            # First check if there are any messages in the queue
            if self.messages_receive_queue.empty():
                return

            # Clear the area where received messages are displayed
            self.stdscr.addstr(5, 0, " " * 50)

            # If there are messages, process and display them
            async with self.receive_message_lock:
                row = 5  # Starting row for displaying messages
                while not self.messages_receive_queue.empty():
                    message = await self.messages_receive_queue.get()
                    self.stdscr.addstr(row, 0, message)
                    row += 1

            self.stdscr.refresh()

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




# View Specific Methods
    async def print_frame_rate(self):
        # Calculate frame rate and print the frame
        current_time = time.time()
        frame_rate = 1 / (current_time - self.last_frame_time)
        self.last_frame_time = current_time

        # Get the size of the terminal
        y, x = self.stdscr.getmaxyx()
        # Print the frame rate on the top right
        self.stdscr.addstr(0, x-21, f"Frame Rate: {frame_rate:.2f} FPS")


