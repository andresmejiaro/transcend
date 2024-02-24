# app/views/home_page.py

import curses
import logging
import json
import asyncio
import aiohttp

from utils.logger import log_message
from utils.url_macros import LOBBY_URI_TEMPLATE, PONG_URI_TEMPLATE
from utils.file_manager import FileManager
from utils.task_manager import TaskManager
from app.widgets.widgets import Widget
from app.widgets.nav_bar import NavBar
from app.class_views.game_view import GamePage

class HomePage(Widget):
    def __init__(self, stdscr, ui_controller, frame_rate, process_speed, task_manager):
        super().__init__(stdscr)

        self.file_manager = FileManager()
        self.task_manager = task_manager
        self.ui_controller = ui_controller
        
        # Frame rate timing
        self.frame_rate = frame_rate
        self.pause_frame = False
        self.popup_active = True

        # Process speed timing
        self.process_speed = process_speed

        # Next view to be displayed
        self.next_view = None

        # Online users
        self.online_users = {}

        # Initialize the nav bar
        self.nav_bar_items = ["Home", "Join Queue", "Exit"]
        self.nav_bar = NavBar(stdscr, self.nav_bar_items)

        # Input Box
        self.input_string = ""

        # Game Management
        self.game_message = None
        self.game_task = None
        self.match_id = None
        self.left_score = 0
        self.right_score = 0
        self.client_id = self.file_manager.load_data('client_info.json')['client_id']
        self.username = self.file_manager.load_data('client_info.json')['username']
        self.opponent_id = None
        self.opponent_username = None
        self.game_update = None
        
        # Lobby Task - Websocket connection to the lobby
        token_info = self.file_manager.load_data('token.json')
        token = token_info['token']
        uri = LOBBY_URI_TEMPLATE.format(token=token)
        ws_data ={
            "task_name": "lobby",
            "uri": uri,
        }
        self.task_manager.create_task(task_name="lobby", task_func=self.connect_ws_task, data=ws_data)

    def __str__(self):
        # Return a string representing the current view
        return "home"

    # Keyboard Input Handler
    async def process_keyboard_input(self, keyboard_input):
        try:
            # log_message(f"Keyboard Input from UI Controller: {keyboard_input}", level=logging.DEBUG)
            key_name = curses.keyname(keyboard_input).decode('utf-8')

            if keyboard_input in [curses.KEY_ENTER, 10]:
                # Handle Enter key press
                selected_item = self.nav_bar.get_selected_item()

                if selected_item == "Exit":
                    log_message("Exiting", level=logging.DEBUG)
                    self.next_view = "exit"

                elif selected_item == "Join Queue":
                    log_message("Joining Queue", level=logging.DEBUG)
                    asyncio.create_task(self.send_to_websocket_by_name("lobby", "join_queue", {'queue_name': 'global'}))

                elif selected_item == "Settings":
                    self.next_view = "settings"

                elif selected_item == "Home":
                    if self.game_task:
                        self.game_task = None
                        self.game_update = None
                        self.task_manager.stop_task_by_name(f'game_{self.match_id}')

            elif keyboard_input == curses.KEY_UP and self.game_task:
                asyncio.create_task(self.send_to_websocket_by_name(f'game_{self.match_id}', "keyboard", {'command':'keyboard', 'key_status': 'on_press', 'key': 'up'}))
                asyncio.create_task(self.send_to_websocket_by_name(f'game_{self.match_id}', "keyboard", {'command':'keyboard', 'key_status': 'on_release', 'key': 'up'}))

            elif keyboard_input == curses.KEY_DOWN and self.game_task:
                asyncio.create_task(self.send_to_websocket_by_name(f'game_{self.match_id}', "keyboard", {'command':'keyboard', 'key_status': 'on_press', 'key': 'down'}))
                asyncio.create_task(self.send_to_websocket_by_name(f'game_{self.match_id}', "keyboard", {'command':'keyboard', 'key_status': 'on_release', 'key': 'down'}))

            elif keyboard_input in [curses.KEY_BACKSPACE, 127]:
                # Handle Backspace key press
                self.input_string = self.input_string[:-1]

            elif key_name.isprintable():
                # Handle other key presses
                self.input_string += key_name

            # We can pass inputs to the nav bar to handle and any other widgets that need to handle input
            self.nav_bar.handle_input(keyboard_input)

        except Exception as e:
            log_message(f"Error in process_keyboard_input: {e}", level=logging.ERROR)

    # Screen Updating and Screen Switching
    async def draw(self):
        try:
            self._clear_screen()

            self.frame_rate[0] = 30
            
            max_y, max_x = self.stdscr.getmaxyx()
            self.update_terminal_size()

            # If the screen is too small, print a message and return
            if self.rows < 30 or self.cols < 70:
                self.print_screen_too_small()
                return
            
            # If we're in a game, draw the game
            if self.game_update and self.game_task:

                self.nav_bar.draw()
                
                self.rectdrawer(self.game_update, "ball", self.stdscr)
                self.rectdrawer(self.game_update, "leftPaddle", self.stdscr)
                self.rectdrawer(self.game_update, "rightPaddle", self.stdscr)
                self.print_score(self.left_score, self.right_score)
                
                if self.game_message:
                    self.print_message_bottom(self.game_message)
                    # asyncio.sleep(10)
                    # self.game_message = None                
            else:
                # Draw the nav bar
                self.frame_rate[0] = 5
                self.nav_bar.draw()

                self.print_header("Home - Welcome to Pong!")

                self.print_frame_rate()

                self.print_online_users(max_y, max_x)

            self._refresh_screen()   

        except Exception as e:
            log_message(f"Error in draw: {e}", level=logging.ERROR)

    # Input Processing Handler
    async def process_input(self):
        try:
            self.process_speed[0] = 500

            user_input = await self.ui_controller.check_and_process_inputs_filterd(["lobby", f'game_{self.match_id}'])

            if user_input:
                task_name = user_input.get("task_name")
                input_data = user_input.get("data")

                if task_name == "lobby":
                    self.process_lobby_input(input_data)
                elif self.game_task and task_name == f'game_{self.match_id}':
                    self.process_game_input(input_data)
                else:
                    log_message(f"Unknown task name: {task_name}", level=logging.WARNING)
                    
        except asyncio.CancelledError:
            # Catch the cancellation when leaving the view
            pass
        except Exception as e:
            log_message(f"Error in process_input: {e}", level=logging.ERROR)

    # Next View
    def get_next_view(self):
        return self.next_view

    # Cleanup
    def cleanup(self):
        pass


    # Task Specific Input Processing
    def process_lobby_input(self, lobby_input):
        try:
            # log_message(f"Lobby Input from UI Controller: {lobby_input}", level=logging.DEBUG)

            if isinstance(lobby_input, str):
                message_data = json.loads(lobby_input)
            else:
                message_data = lobby_input

            message_type = message_data.get("type")
            data = message_data.get("data", {})

            if message_type == "user_joined":
                self.handle_user_joined(data)
            elif message_type == "user_left":
                self.handle_user_left(data)
            elif message_type == "found_opponent":
                token_info = self.file_manager.load_data('token.json')
                token = token_info['token']
                log_message(f"Found opponent: {data}", level=logging.INFO)
                self.match_id = data.get("match_id")
                uri = PONG_URI_TEMPLATE.format(match_id=self.match_id, token=token)
                ws_data ={
                    "task_name": f'game_{self.match_id}',
                    "uri": uri,
                }
                log_message(f"Connecting to websocket: {uri}", level=logging.INFO)
                self.game_task = self.task_manager.create_task(task_name=f'game_{self.match_id}', task_func=self.connect_ws_task, data=ws_data)

        except Exception as e:
            log_message(f"Error in process_lobby_input: {e}", level=logging.ERROR)

    def process_game_input(self, game_input):
        try:
            # log_message(f"Game Input from UI Controller: {game_input}", level=logging.DEBUG)
            if self.game_task:
                if isinstance(game_input, str):
                    message_data = json.loads(game_input)
                else:
                    message_data = game_input

                message_type = message_data.get("type")
                data = message_data.get("data", {})

                log_message(f"Game Input from UI Controller: {message_type} {data}", level=logging.DEBUG)
                
                if self.game_task:
                    if self.left_score == 11 or self.right_score == 11:
                        self.game_task = None
                        self.game_update = None
                        self.task_manager.stop_task_by_name(f'game_{self.match_id}')
                        self.game_message = "Game Over!"
                        asyncio.sleep(3)
                        self.game_message = None
                        self.left_score = 0
                        self.right_score = 0
                        self.match_id = None
                        self.opponent_id = None
                        self.opponent_username = None
                    
                    elif message_type == "message":
                        # log_message(f"Message from game: {data}", level=logging.DEBUG)
                        self.game_message = data.get("message")
                        asyncio.create_task(self.send_to_websocket_by_name(f'game_{self.match_id}', "start_ball", {}))

                    elif message_type == "screen_report":
                        # log_message(f"Screen Report from game: {data}", level=logging.DEBUG)
                        self.game_update = data.get("game_update")
                        self.left_score = data.get("left_score")
                        self.right_score = data.get("right_score")

                    elif message_type == "match_finished":
                        # log_message(f"Match Finished from game: {data}", level=logging.DEBUG)
                        self.game_task = None
                        self.game_update = None
                        self.game_message = "Game Over!"
                        asyncio.sleep(10)
                        self.task_manager.stop_task_by_name(f'game_{self.match_id}')
                        self.game_message = None
                        self.left_score = 0
                        self.right_score = 0
                        self.match_id = None
                        self.opponent_id = None
                        self.opponent_username = None

        except Exception as e:
            log_message(f"Error in process_game_input: {e}", level=logging.ERROR)
    # -----------------------------


    # Lobby Task Handling Methods
    def handle_user_joined(self, user_data):
        try:
            online_users = user_data.get("online_users")
            updated_users = dict(self.online_users)
            updated_users.update(online_users)
            self.online_users = updated_users

        except Exception as e:
            log_message(f"Error in handle_user_joined: {e}", level=logging.ERROR)

    def handle_user_left(self, user_data):
        try:
            left_user_id = user_data.get("client_id")
            updated_users = dict(self.online_users)
            updated_users.pop(left_user_id, None)
            self.online_users = updated_users

        except Exception as e:
            log_message(f"Error in handle_user_left: {e}", level=logging.ERROR)
    
    # View Specific Methods - They should be structured with rows and columns in mind
    def print_online_users(self, max_y, max_x):
        try:
            # Print the online users
            row, col = 2, 0  # Starting position
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
    # -----------------------------

    async def send_to_websocket_by_name(self, task_name, command, data):
        try:
            # We will send JSON messages to the server
            if command == 'keyboard':
                message = json.dumps(data)
            else:
                message = json.dumps({
                    "command": command,
                    "data": data
                })
            # log_message(f"Sending message: {message} to {task_name}, with command {command}", level=logging.DEBUG)
            # Acquire the lock before accessing the queue
            async with self.ui_controller.list_of_shared_data[task_name]["send_lock"]:
                self.ui_controller.list_of_shared_data[task_name]["send_queue"].put(message)
                ws = self.ui_controller.list_of_shared_data[task_name]["ws"]
                await ws.send_str(message)
                # log_message(f'Current Queue: {self.ui_controller.list_of_shared_data[task_name]["send_queue"]}', level=logging.DEBUG)
                self.input_string = ""

        except Exception as e:
            log_message(f"Error in send_message: {e}", level=logging.ERROR)

    async def connect_ws_task(self, data):
        try:
            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(connector=connector) as session:
                uri = data['uri']
                # formatted_uri = uri.format(token=token)
                log_message(f"Connecting to websocket: {uri}", level=logging.INFO)
                async with session.ws_connect(uri) as ws:
                    ws_data ={
                        "receive_queue": asyncio.Queue(),
                        "send_queue": asyncio.Queue(),
                        "receive_lock": asyncio.Lock(),
                        "send_lock": asyncio.Lock(),
                        "ws": ws,                  
                    }
                    self.ui_controller.add_shared_data(f'{data["task_name"]}', ws_data)
                    try:

                        async for msg in ws:
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                async with ws_data["receive_lock"]:
                                    # log_message(f'{data["task_name"]} received message: {msg}', level=logging.DEBUG)
                                    await ws_data["receive_queue"].put(msg.data)
                            elif msg.type == aiohttp.WSMsgType.ERROR:
                                break

                        log_message("Websocket task completed", level=logging.DEBUG)
                        
                    except (asyncio.CancelledError, GeneratorExit):
                        log_message("Websocket task cancelled", level=logging.DEBUG)
                        raise
                    except Exception as e:
                        log_message(f"Websocket task error: {e}", level=logging.ERROR)
                        raise
                        
        except (asyncio.CancelledError, GeneratorExit):
            log_message("Websocket task cancelled", level=logging.DEBUG)
            raise
        except aiohttp.ClientError as e:
            log_message(f"An error occurred in Lobby Websocket Task: {e}", level=logging.ERROR)
            self.exit_status = 1
        except Exception as e:
            log_message(f"An error occurred in Lobby Websocket Task: {e}", level=logging.ERROR)
            self.exit_status = 1
    
    