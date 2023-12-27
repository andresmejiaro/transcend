# home/profile.py

from utils.logger import log_message
import curses
import logging

class Profile:
    def __init__(self, stdscr, http, ws):
        self.stdscr = stdscr
        self.next_view = None
        self.http = http
        self.ws = ws
        self.user_data = None
        self.views = None
        self.current_view_index = 0

    async def get_user_input(self):
        try:
            key = self.stdscr.getch()
            log_message(f"User input: {key}")
            if key == curses.KEY_LEFT:
                return "left"
            elif key == curses.KEY_RIGHT:
                return "right"
            elif key == curses.KEY_ENTER or key == 10 or key == 13:
                return "enter"
            elif key == 27:  # ESC key
                return None
            elif key != -1:  # Ignore special keys with value -1
                return key
            
        except Exception as e:
            log_message(f"Error getting user input: {e}", level=logging.ERROR)
            return None

    def process_input(self, user_input):
        try:
            if user_input == "right":
                self.current_view_index = (self.current_view_index + 1) % len(self.views)
            elif user_input == "left":
                self.current_view_index = (self.current_view_index - 1) % len(self.views)
            elif user_input == "enter":
                current_view = self.views[self.current_view_index]["view"]
                self.next_view = current_view
                current_view.reset_index()

        except Exception as e:
            log_message(f"Error processing user input: {e}", level=logging.ERROR)
            return None

    def update_screen(self, all_views):
        try:
            if self.views is None:
                self.views = all_views

            self.stdscr.clear()

            # Display menu bar
            self.stdscr.addstr(0, 1, "Menu: ")
            for i, view_data in enumerate(self.views):
                name = view_data["name"]
                if i == self.current_view_index:
                    # Highlight the selected view
                    self.stdscr.addstr(0, len("Menu: ") + 1 + sum(len(v["name"]) + 2 for v in self.views[:i]), name, curses.A_REVERSE)
                else:
                    self.stdscr.addstr(0, len("Menu: ") + 1 + sum(len(v["name"]) + 2 for v in self.views[:i]), name)

            # Display current subview
            current_subview = self.views[self.current_view_index]["view"]
            current_subview.display()

            self.stdscr.refresh()
            
        except Exception as e:
            log_message(f"Error updating screen: {e}", level=logging.ERROR)

    def get_next_view(self):
        return self.next_view

# Preview of the Profile view
    def display(self):
        # Display profile content
        self.stdscr.addstr(2, 2, "User Profile")
        # Add more content as needed

# Helper functions
    def reset_index(self):
        self.current_view_index = 0