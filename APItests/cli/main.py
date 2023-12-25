import curses
import asyncio
import json
from curses_ui import CursesUI
from http_api import http_api
from websocket_api import websocket_api

BASE_WS_URL = "ws://localhost:8001/ws"

class CursesApp:
# Initialization methods
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.resize_terminal()
        self.api_client = http_api()
        self.websocket_manager = websocket_api()
        self.lobby_websocket = None
        self.curses_ui = CursesUI(stdscr, self.api_client, self.websocket_manager, self.lobby_websocket)
        self.mode = "home"
        self.listen_task = None

    def resize_terminal(self):
        curses.resizeterm(30, 120)
# -----------------------------

# Clean up methods
    async def quit(self):
        if self.lobby_websocket:
            await self.cleanup()
        else:
            self.cleanup_curses()

        self.api_client.close_session()

        exit(0)
    
    def cleanup_curses(self):
        curses.curs_set(1)
        curses.endwin()

    async def cleanup(self):
        try:
            # Handle cancellation of listening task if running
            if self.listen_task:
                await self.listen_task.cancel()
                await asyncio.gather(self.listen_task, return_exceptions=True)

            # Close WebSocket connection with timeout
            if self.lobby_websocket:
                try:
                    await asyncio.wait_for(self.websocket_manager.close(self.lobby_websocket), timeout=5)
                except asyncio.TimeoutError:
                    print("Timeout closing WebSocket connection")
                    exit(1)

        finally:
            self.cleanup_curses()
            self.set_mode("exit")

    async def run(self):
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
                    await self.handle_landing_page_mode()
                elif self.mode == "logout":
                    self.handle_logout()
                elif self.mode == "exit":
                    await self.quit()

        except KeyboardInterrupt:
            await self.quit()  # Handle Ctrl+C
# -----------------------------

# Mode handling methods
    def handle_home_mode(self):
        key = self.curses_ui.draw_home_page()
        if key == ord('q'):
            asyncio.create_task(self.quit())
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
            asyncio.create_task(self.quit())

    def handle_login_mode(self):
        login_result = self.curses_ui.draw_login_page()

        if login_result is None:
            self.set_mode("login_register")
            return

        username, password = login_result

        if self.api_client.login(username, password):
            self.set_mode("landing_page")
        else:
            self.set_mode("login_register")

    def handle_register_mode(self):
        username = self.curses_ui.draw_register_page()

        if username is None:
            self.set_mode("home")
        else:
            self.set_mode("landing_page")

    async def handle_landing_page_mode(self):
        try:
            if not self.lobby_websocket:
                url = f"{BASE_WS_URL}/lobby2/"
                user_info = self.load_user_info()
                client_id = user_info.get("client_id", "")
                self.lobby_websocket = await self.websocket_manager.connect(url, {"client_id": client_id})
                self.listen_task = asyncio.create_task(self.listen_for_updates())

            logout = self.curses_ui.draw_landing_page()

            if logout:
                await self.cleanup()
                return

            await asyncio.sleep(1)  # Adjust the sleep duration as needed

        except Exception as e:
            print(f"Error connecting to WebSocket: {e}")
            self.set_mode("home")

    def handle_logout(self):
        asyncio.create_task(self.cleanup())
# -----------------------------

# Lobby Listener Method
    async def listen_for_updates(self):
        try:
            self.print_to_debug_file("Listening for updates...\n")
            while True:
                try:
                    data = await self.websocket_manager.receive(self.lobby_websocket)
                    self.print_to_debug_file(f"Received data: {data}\n")

                except asyncio.CancelledError:
                    break
                
        except asyncio.CancelledError:
            pass
# -----------------------------

# Helper methods
    def set_mode(self, mode):
        self.mode = mode

    def load_user_info(self):
        with open("./tmp_files/client_info.txt", "r") as f:
            user_info_json = f.read().strip()
            user_info = json.loads(user_info_json)
            return user_info

    def print_to_debug_file(self, message):
        with open("./debbug.txt", "a") as file:
            file.write(message)
# -----------------------------

# Main method
def main(stdscr):
    curses_app = CursesApp(stdscr)
    asyncio.run(curses_app.run(), debug=True)

if __name__ == "__main__":
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)

    try:
        main(stdscr)

    except KeyboardInterrupt:
        pass

    finally:
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()
