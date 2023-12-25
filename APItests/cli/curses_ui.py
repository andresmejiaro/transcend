# curses_ui.py

import curses
import signal
import time
from enum import Enum

class Page(Enum):
    HOME = "Home"
    PLAY = "Play"
    STATS = "Stats"
    FRIENDS = "Friends"
    SETTINGS = "Settings"

class CursesUI:
    def __init__(self, stdscr, logo_file="logo.txt", api_client=None, websocket_manager=None, lobby_websocket=None):
        """Initialize the CursesUI instance.

        Args:
            stdscr (curses.window): The curses window object.
            logo_file (str): The path to the file containing the logo.
            api_client: The API client object.
            websocket_manager: The websocket manager object.
            lobby_websocket: The lobby websocket object.
        """
        self.stdscr = stdscr
        self.selected_index = 0  # Initialize selected_index as an instance variable
        self.logo = self.read_logo_from_file("./textures/logo.txt")
        signal.signal(signal.SIGWINCH, self.handle_resize)
        curses.curs_set(0)  # Hide the cursor
        self.stdscr.timeout(100)  # Set a timeout for getch to enable non-blocking input
        self.screen_height, self.screen_width = self.stdscr.getmaxyx()
        self.api_client = api_client
        self.websocket_manager = websocket_manager
        self.lobby_websocket = lobby_websocket
        self.login_attempts = {}
        self.form_row = 0  # Initialize form_row as an instance variable
        self.form_col = 0  # Initialize form_col as an instance variable
        self.blue_color_pair = 0  # Initialize blue_color_pair as an instance variable
        self.pages = [Page.HOME, Page.PLAY, Page.STATS, Page.FRIENDS, Page.SETTINGS]
        self.selected_page_index = 0

# Drawing methods
    def draw_home_page(self):
        """Draw the home page."""
        if self.screen_height < 30 or self.screen_width < 120:
            return self.draw_error_page("Terminal size is too small. Please resize to at least 30x120.")

        self.clear_screen()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)

        # Draw ASCII art centered
        start_row = (self.screen_height - len(self.logo)) // 2
        for i, line in enumerate(self.logo):
            self.center_text(line, start_row + i)

        # Draw "Press any key to start" centered
        prompt_message = "Press any key to start"
        self.center_text(prompt_message, start_row + len(self.logo) + 2)
        self.stdscr.refresh()

        return self.stdscr.getch()

    def draw_login_register_page(self, choices):
        """Draw the login/register page.

        Args:
            choices (list): List of choices for login/register.
        Returns:
            int: The selected index.
        """
        if self.screen_height < 30 or self.screen_width < 120:
            return self.draw_error_page("Terminal size is too small. Please resize to at least 30x120.")

        self.clear_screen()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)

        # Draw ASCII art centered
        start_row = (self.screen_height - len(self.logo)) // 2
        for i, line in enumerate(self.logo):
            self.center_text(line, start_row + i)

        # Draw choices for login/register centered
        choices_row = start_row + len(self.logo) + 2
        total_width = sum(len(choice) for choice in choices) + (len(choices) - 1) * 2  # Total width considering spaces between choices
        choices_col = (self.screen_width - total_width) // 2

        for i, choice in enumerate(choices):
            if i == self.selected_index:  # Highlight the selected choice
                self.stdscr.addstr(choices_row, choices_col, choice, curses.color_pair(1) | curses.A_BOLD | curses.A_REVERSE)
            else:
                self.stdscr.addstr(choices_row, choices_col, choice, curses.color_pair(1))
            choices_col += len(choice) + 2  # Move the column position for the next choice

        self.stdscr.refresh()

        # Get user input
        key = self.get_user_input()

        return self.process_user_input(key, choices)

    def draw_login_page(self):
        """Draw the login page."""
        if self.screen_height < 30 or self.screen_width < 120:
            return self.draw_error_page("Terminal size is too small. Please resize to at least 30x120.")

        self.clear_screen()
        curses.start_color()
        blue_color_pair = 2  # New color pair for the blue text
        curses.init_pair(blue_color_pair, curses.COLOR_CYAN, curses.COLOR_BLACK)

        # Draw ASCII art centered
        start_row = (self.screen_height - len(self.logo)) // 2
        for i, line in enumerate(self.logo):
            self.center_text(line, start_row + i)

        # Draw login form centered
        form_row = start_row + len(self.logo) + 2
        form_col = (self.screen_width - 30) // 2  # Adjust the width of the form
        self.stdscr.addstr(form_row, form_col, "Username:", curses.color_pair(blue_color_pair))
        username_col = form_col + 10  # Adjust the column position for the username input
        username = self.draw_text_input(form_row, username_col, 20)

        password_row = form_row + 2  # Increase the space between the form and password label
        self.stdscr.addstr(password_row, form_col, "Password:", curses.color_pair(blue_color_pair))
        password_col = form_col + 10  # Adjust the column position for the password input
        password = self.draw_text_input(password_row, password_col, 20)  # Mask password input

        self.form_row = form_row
        self.form_col = form_col
        self.blue_color_pair = blue_color_pair

        username, password, valid = self.handle_login_input(username, password)

        if valid:
            self.draw_long_success_message()
            return username, password
        else:
            self.draw_error_message()
            self.draw_login_page

    def draw_landing_page(self):
        self.clear_screen()

        # Draw the top navigation bar
        self.draw_navigation_bar()

        # Draw the content based on the selected page
        self.draw_selected_page_content()

        # Handle user input for navigation
        self.handle_landing_page_input()


    def draw_navigation_bar(self):
        # Set the color for the navigation bar
        self.stdscr.attron(curses.color_pair(1))

        # Calculate the width for each navigation item
        item_width = self.screen_width // len(self.pages)

        # Draw each page in the navigation bar
        for i, page in enumerate(self.pages):
            # Highlight the selected page
            if i == self.selected_page_index:
                self.stdscr.addstr(0, i * item_width, f"{page.value} ", curses.A_BOLD | curses.A_REVERSE)
            else:
                self.stdscr.addstr(0, i * item_width, f"{page.value} ")

        # Refresh the screen
        self.stdscr.refresh()

        # Reset the attributes
        self.stdscr.attroff(curses.color_pair(1))

    def draw_selected_page_content(self):
        """Draw the content for the selected page."""
        selected_page = self.pages[self.selected_page_index]

        if selected_page == Page.HOME:
            self.draw_home_page_content()
        elif selected_page == Page.PLAY:
            self.draw_play_page_content()
        elif selected_page == Page.STATS:
            self.draw_stats_page_content()
        elif selected_page == Page.FRIENDS:
            self.draw_friends_page_content()
        elif selected_page == Page.SETTINGS:
            self.draw_settings_page_content()

# Handling methods
    def handle_landing_page_input(self):
        """Handle user input for the landing page."""
        key = self.stdscr.getch()

        if key == curses.KEY_LEFT and self.selected_page_index > 0:
            self.move_to_previous_page()
            self.draw_selected_page_content()  # Draw content as user scrolls
        elif key == curses.KEY_RIGHT and self.selected_page_index < len(self.pages) - 1:
            self.move_to_next_page()
            self.draw_selected_page_content()  # Draw content as user scrolls
        elif key == 10:  # Enter key
            self.show_selected_page_content()  # Show content on Enter key

    def move_to_previous_page(self):
        """Move to the previous page in the navigation."""
        self.selected_page_index -= 1
        self.redraw_navigation_and_content()

    def move_to_next_page(self):
        """Move to the next page in the navigation."""
        self.selected_page_index += 1
        self.redraw_navigation_and_content()

    def show_selected_page_content(self):
        """Show the content for the selected page."""
        # Clear the screen before drawing the selected page content
        self.clear_screen()

        # Draw the navigation bar again
        self.draw_navigation_bar()

        # Draw the content for the selected page
        self.draw_selected_page_content()

        # Update the screen
        self.stdscr.refresh()

    def redraw_navigation_and_content(self):
        """Redraw the navigation bar and content for the selected page."""
        # Draw the navigation bar
        self.draw_navigation_bar()

        # Draw the content for the selected page
        self.draw_selected_page_content()

        # Update the screen
        self.stdscr.refresh()

# -----------------------------

# Validation methods
    def handle_login_input(self, username, password):
        valid = self.validate_login(username, password)
        self.print_to_debbug_file(f"valid: {valid}\n")
        return username, password, valid          

    def validate_login(self, username, password):
        """Validate the login credentials.

        Args:
            username (str): The username.
            password (str): The password.
        Returns:
            bool: True if the login is valid, False otherwise.
        """
        valid = False  # Initialize valid here

        if username and password:
            # Check login attempts before making the API call
            self.track_login_attempt(username)
            attempts, _ = self.login_attempts.get(username, (0, 0))
            if attempts > 3:
                # Display an error message
                error_message = "Too many login attempts. Please try again later."
                self.stdscr.addstr(self.form_row + 5, self.form_col, error_message, curses.color_pair(self.blue_color_pair) | curses.A_BOLD)
                self.stdscr.refresh()
                return None  # Return early without waiting

            valid = self.api_client.login(username, password)

        return valid
    
    def track_login_attempt(self, username):
        attempts, last_attempt = self.login_attempts.get(username, (0, 0))
        if time.time() - last_attempt > 60:
            attempts = 0
        attempts += 1
        self.login_attempts[username] = (attempts, time.time())
# -----------------------------

# Drawing helper methods
    def draw_error_message(self):
        error_message = "Invalid username or password. Please try again."
        self.stdscr.addstr(self.form_row + 5, self.form_col, error_message, curses.color_pair(self.blue_color_pair) | curses.A_BOLD)
        self.stdscr.refresh()
        time.sleep(2)

    def draw_long_success_message(self):

        success_message = "Login successful. Redirecting to the Home Page..."
        self.stdscr.addstr(self.form_row + 5, self.form_col, success_message, curses.color_pair(self.blue_color_pair) | curses.A_BOLD)
        self.stdscr.refresh()
        time.sleep(2)

    def draw_text_input(self, row, col, max_length, mask_char='*'):
        curses.curs_set(1)  # Show cursor for text input
        input_text = ""
        while True:
            # Display the masked characters
            masked_text = mask_char * len(input_text)
            self.stdscr.addstr(row, col, masked_text)

            self.stdscr.refresh()
            key = self.stdscr.getch()

            if key == 10:  # Enter key
                curses.curs_set(0)  # Hide cursor after input
                return input_text
            elif key == 27:  # Escape key
                curses.curs_set(0)  # Hide cursor on escape
                return None
            elif key == curses.KEY_BACKSPACE:
                # Handle backspace to delete the last character
                if input_text:
                    input_text = input_text[:-1]
                    # Clear the last character visually by overwriting with a space
                    self.stdscr.addstr(row, col + len(input_text), ' ')
            elif len(input_text) < max_length and 32 <= key <= 126:
                # Only append the actual character to the input_text
                input_text += chr(key)
# -----------------------------

# Utility methods       
    def print_to_debbug_file(self, text):
        with open("debbug.txt", "a") as file:
            file.write(text)

    def handle_resize(self, signum, frame):
        self.screen_height, self.screen_width = self.stdscr.getmaxyx()
        self.stdscr.refresh()

    def center_text(self, text, row):
        start_col = (self.screen_width - len(text)) // 2
        self.stdscr.addstr(row, start_col, text, curses.color_pair(1))

    def read_logo_from_file(self, logo_file):
        with open(logo_file, "r") as file:
            return file.read().splitlines()

    def clear_screen(self):
        self.stdscr.clear()
        self.stdscr.refresh()
# -----------------------------
        
# Input Utility methos
    def get_user_input(self):
        """Get user input."""
        return self.stdscr.getch()
    
    def process_user_input(self, key, choices):
        """Process user input for the login/register page.

        Args:
            key (int): The key pressed by the user.
            choices (list): List of choices for login/register.
        Returns:
            int: The selected index.
        """
        if key == 27:  # ASCII value for Escape key
            return -1  # Indicate escape key
        elif key == ord(' ') or key == 10:  # ASCII value for Space or Enter key
            return self.selected_index  # Confirm selection
        elif key == curses.KEY_LEFT and self.selected_index > 0:
            self.selected_index -= 1  # Move left
        elif key == curses.KEY_RIGHT and self.selected_index < len(choices) - 1:
            self.selected_index += 1  # Move right
        elif key == ord('e'):  # Additional check for the 'e' key for the "Exit" option
            return len(choices)  # Return the index corresponding to "Exit"

        return -2  # Invalid input (should not happen)
    
# -----------------------------
    
# Draw Content Windows
    def draw_home_page_content(self):
        """Draw the content for the Home page."""
        self.draw_navigation_bar()
        
        # Add a message specific to the Home page content
        content_message = "This is the Home page content."
        self.stdscr.addstr(2, 0, content_message, curses.color_pair(1))
        
        # Refresh the screen
        self.stdscr.refresh()
        
    def draw_play_page_content(self):
        """Draw the content for the Play page."""
        self.draw_navigation_bar()

        content_message = "This is the Play page content."
        self.stdscr.addstr(2, 0, content_message, curses.color_pair(1))

        self.stdscr.refresh()

    def draw_stats_page_content(self):
        """Draw the content for the Stats page."""
        self.draw_navigation_bar()

        content_message = "This is the Stats page content."
        self.stdscr.addstr(2, 0, content_message, curses.color_pair(1))

        self.stdscr.refresh()

    def draw_friends_page_content(self):
        """Draw the content for the Friends page."""
        self.draw_navigation_bar()

        content_message = "This is the Friends page content."
        self.stdscr.addstr(2, 0, content_message, curses.color_pair(1))

        self.stdscr.refresh()

    def draw_settings_page_content(self):
        """Draw the content for the Settings page."""
        self.draw_navigation_bar()

        content_message = "This is the Settings page content."
        self.stdscr.addstr(2, 0, content_message, curses.color_pair(1))

        self.stdscr.refresh()

