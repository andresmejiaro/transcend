# game/game.py

import asyncio
import curses
import threading
import websockets

BASE_WS_URL = "ws://localhost:8001/ws"

class Game:
    def __init__(self, stdscr, http, ws):
        self.stdscr = stdscr
        self.http = http
        self.ws = ws
        self.websocket_uri = BASE_WS_URL
        self.exit_flag = False
        self.user_input = None

    async def game_loop(self):
        async with websockets.connect(self.websocket_uri) as websocket:
            while not self.exit_flag:
                # Receive updates from the server
                server_message = await websocket.recv()

                # Update game state and render frames based on server messages
                # (Implement your game logic here)

    def start_game_loop(self):
        # Start the game loop in a separate thread
        game_thread = threading.Thread(target=self._start_game_loop)
        game_thread.start()

    def _start_game_loop(self):
        asyncio.run(self.game_loop())

    def stop_game_loop(self):
        # Set the exit flag to stop the game loop
        self.exit_flag = True

    async def get_user_input(self):
        # Implement your user input handling here
        pass

    def process_input(self, user_input, all_views):
        # Implement your input processing logic here
        pass

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


    def display(self):
        # Implement your display logic here
        pass

    def get_next_view(self):
        # Implement logic to determine if the view should switch
        return None
