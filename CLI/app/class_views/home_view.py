# app/views/home_page.py

import curses
import logging
import asyncio
import time

from utils.logger import log_message

class HomePage():
    def __init__(self, stdscr, messages_send_queue, messages_receive_queue, send_message_lock, receive_message_lock):
        self.stdscr = stdscr
        self.messages_send_queue = messages_send_queue
        self.messages_receive_queue = messages_receive_queue
        self.send_message_lock = send_message_lock
        self.receive_message_lock = receive_message_lock
        self.last_frame_time = time.time()

    async def get_user_input(self):
        try:
            key = self.stdscr.getch()
            log_message(f"Key pressed: {key}", level=logging.DEBUG)
            if key:
                return key
            

        except Exception as e:
            log_message(f"Error in get_user_input: {e}", level=logging.ERROR)
            return None

    async def process_inputs(self, user_input):
        try:
            if user_input == -1:
                log_message("No key pressed", level=logging.DEBUG)
            
        except Exception as e:
            log_message(f"Error in process_inputs: {e}", level=logging.ERROR)

    async def get_send_message_queue(self):
        return self.messages_send_queue

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
        
    async def update_screen(self):
        try:
            self.stdscr.clear()

            self.stdscr.addstr(0, 0, "Welcome to the Home Page!")
            self.stdscr.addstr(2, 0, "Press any key to continue...")
            
            # Display received messages
            self.stdscr.addstr(4, 0, "Received Messages:")

            # Calculate frame rate and print the frame
            current_time = time.time()
            frame_rate = 1 / (current_time - self.last_frame_time)
            self.last_frame_time = current_time

            # Get the size of the terminal
            y, x = self.stdscr.getmaxyx()
            # Print the frame rate on the top right
            self.stdscr.addstr(0, x-21, f"Frame Rate: {frame_rate:.2f} FPS")

            self.stdscr.refresh()

        except Exception as e:
            log_message(f"Error in update_screen: {e}", level=logging.ERROR)

    async def get_next_view(self):
        return None

    async def cleanup(self):
        # Cleanup resources if needed
        pass
