# home/friends.py

from utils.logger import log_message
import curses

class Friends:
    def __init__(self, stdscr, http, ws):
        self.stdscr = stdscr
        self.http = http
        self.ws = ws

    def display(self):
        # Display profile content
        self.stdscr.addstr(2, 2, "User Friends")
        # Add more content as needed

    def update_data(self):
        # Update data if needed
        pass