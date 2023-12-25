# main.py

import curses
from curses_ui import CursesUI
from http_api import http_api
from websocket_api import websocket_api
from landing_page_handler import LandingPageHandler 

class CursesApp:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.resize_terminal()  # Resize the terminal initially
        self.api_client = http_api()
        self.websocket_manager = websocket_api()
        self.lobby_websocket = None
        self.curses_ui = CursesUI(stdscr, self.websocket_manager, self.api_client, self.lobby_websocket)
        self.mode = "home"  # Initial mode
        self.landing_page_handler = LandingPageHandler(self.api_client, self.websocket_manager, self.curses_ui)

    def resize_terminal(self):
        curses.resizeterm(30, 120)  # Adjust the dimensions as needed

    def quit(self):
        curses.curs_set(1)  # Restore cursor visibility
        curses.endwin()  # End curses mode
        self.set_mode("exit")

    def run(self):
        try:
            while self.mode != "exit":
                if self.mode == "home":
                    self.handle_home_mode()
                elif self.mode == "login_register":
                    self.handle_login_register_mode()
                elif self.mode == "login":
                    self.handle_login_mode()
                elif self.mode == "register":
                    self.handle_register_mode()
                elif self.mode == "landing_page":
                    self.handle_landing_page_mode()
                elif self.mode == "logout":
                    self.handle_logout()
                elif self.mode == "exit":
                    self.quit()

        except KeyboardInterrupt:
            self.quit()  # Handle Ctrl+C
            raise

    def handle_home_mode(self):
        key = self.curses_ui.draw_home_page()
        if key == ord('q'):
            self.quit()
        elif key == ord(' '):
            self.set_mode("login_register")

    def handle_login_register_mode(self):
        choices = ["Login", "Register", "Exit"]
        selected_choice = self.curses_ui.draw_login_register_page(choices)

        if selected_choice == 0:
            self.set_mode("login")
        elif selected_choice == 1:
            self.set_mode("register")
        elif selected_choice == 2:
            self.set_mode("exit")

    def handle_login_mode(self):
        login_result = self.curses_ui.draw_login_page()

        if login_result is None:
            self.set_mode("login_register")
            return

        username, password = login_result

        if self.api_client.login(username, password):
            # Successful login, change mode or perform other actions
            self.set_mode("landing_page")
        else:
            # Failed login, handle the error or display a message
            self.set_mode("login_register")
            # Display the error message, delay, or take other actions as needed...

    def handle_register_mode(self):
        username = self.curses_ui.draw_register_page()

        if username is None:
            self.set_mode("home")
        else:
            self.set_mode("landing_page")

    def handle_landing_page_mode(self):
        self.lobby_websocket = self.landing_page_handler.handle_landing_page()
        logout = self.curses_ui.draw_landing_page()

        if logout:
            self.set_mode("logout")

    def handle_logout(self):
        self.api_client.logout()
        self.set_mode("home")

    def set_mode(self, mode):
        self.mode = mode


def main(stdscr):
    curses_app = CursesApp(stdscr)
    curses_app.run()

if __name__ == "__main__":
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)

    try:
        main(stdscr)
    except KeyboardInterrupt:
        pass  # Ctrl+C was pressed
    finally:
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()
