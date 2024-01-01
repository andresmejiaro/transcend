# app/app.py

import logging
import asyncio
import curses
import aiohttp

from utils.logger import log_message
from utils.url_macros import LOBBY_URI_TEMPLATE
from utils.file_manager import FileManager
from utils.task_manager import TaskManager

from UI.UI_controller import UIController
# from app.class_views.login_view import Login
from app.class_views.splash_view import SplashView

class CLIApp:
    def __init__(self, stdscr):
        self.stdscr = stdscr        # The curses screen object
        self.ui_view = None    # The current view being displayed
        self.exit_status = 0        # The exit status of the application
        self.logged_in = False      # The logged in status of the application
        self.file_manager = FileManager()   # The file manager object - Used to load and save data to files
        self.task_manager = TaskManager()   # The task manager object - Used to create and manage tasks

        # Adjust App Frame Rate - Adjust the frame rate of the application
        self.frame_rate = 30

# Essential App Tasks - These tasks are essential to the application and will be created and started in the main loop
    # Lobby Websocket Task - Connect to the lobby websocket and send and receive messages throught the duration of the application
    async def lobby_websocket_send_and_receive_task(self, data):
        async with aiohttp.ClientSession() as session:
            client_info = self.file_manager.load_data('client_info.json')
            client_id = client_info['client_id']
            uri = LOBBY_URI_TEMPLATE.format(client_id=client_id)
            log_message(f"Connecting to websocket: {uri}", level=logging.DEBUG)
            async with session.ws_connect(uri) as ws:
                try:
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            async with data["receive_lock"]:
                                await data["receive_queue"].put(msg.data)
                                log_message(f"Received message: {msg.data}", level=logging.DEBUG)
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            break

                        # Send messages
                        while not data["send_queue"].empty():
                            async with data["send_lock"]:
                                message = await data["send_queue"].get()
                                await ws.send_str(message)
                                log_message(f"Sent message: {message}", level=logging.DEBUG)

                        await asyncio.sleep(1)

                    log_message("Websocket task completed", level=logging.DEBUG)

                except (asyncio.CancelledError, GeneratorExit):
                    log_message("Websocket task cancelled", level=logging.DEBUG)
                    raise

                except Exception as e:
                    log_message(f"Websocket task error: {e}", level=logging.ERROR)
                    raise

    # Keyboard Input Task - Get keyboard input and put it in the keyboard input queue
    async def keyboard_input_task(self, data):
        try:
            log_message("Keyboard Input Task started", level=logging.DEBUG)
            while True:
                key = self.stdscr.getch()
                if key != curses.ERR:
                    # Convert the key code to the key name
                    key_name = curses.keyname(key).decode('utf-8')

                    async with data["receive_lock"]:
                        await data["receive_queue"].put(key_name)

                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            # Catch the cancellation when leaving the view
            pass

        except Exception as e:
            log_message(f"An error occurred in Keyboard Input Task: {e}", level=logging.ERROR)
            self.exit_status = 1

    # Main Loop Task - Run the main loop of the application
    async def run_ui_controller(self):
        try:
            log_message("Launching UI", level=logging.DEBUG)
            self.ui_view = SplashView(self.stdscr)
            while True:
                self.ui_view.run()

                next_view = self.ui_view.get_next_view()

                if next_view is not None:
                    self.ui_view = next_view
                    continue

                await asyncio.sleep(self.set_frame_rate(self.frame_rate))

        except asyncio.CancelledError:
            log_message("UI Task cancelled", level=logging.DEBUG)
            # await self.ui_view.cleanup()

        except KeyboardInterrupt:
            # Catch the keyboard interrupt
            log_message("Keyboard interrupt detected. Exiting...")
            # await self.ui_view.cleanup()
            self.exit_status = 0

        except Exception as e:
            log_message(f"An error occurred in UI Task: {e}", level=logging.ERROR)
            # await self.ui_view.cleanup()
            self.exit_status = 1
# -------------------------------------

# Entry Point - Initializes tasks and runs the main loop, additionaly tasks will be created and started and stopped as needed in the main loop

    async def start(self):
        try:
            # await self.splash()
            # await self.login()

            # Create ws lobby task using the task_manager
            lobby_ws_data = {
                "receive_queue": asyncio.Queue(),
                "send_queue": asyncio.Queue(),
                "receive_lock": asyncio.Lock(),
                "send_lock": asyncio.Lock(),
            }
            self.task_manager.create_task(task_name="lobby", task_func=self.lobby_websocket_send_and_receive_task, data=lobby_ws_data)

            # Create keyboard input task using the task_manager
            keyboard_input_data = {
                "receive_queue": asyncio.Queue(),
                "receive_lock": asyncio.Lock(),
            }
            self.task_manager.create_task(task_name="keyboard", task_func=self.keyboard_input_task, data=keyboard_input_data)

            # Create the current view
            self.ui_view = UIController(
                stdscr=self.stdscr,
                lobby_ws_data=lobby_ws_data,
                keyboard_input_data=keyboard_input_data
            )

            # Start all tasks
            self.task_manager.start_all_tasks()
            
            # Start an app task (assuming run_ui_controller is a coroutine function)
            await self.run_ui_controller()

            # Start all tasks (including app_task) in a loop
            while self.task_manager.is_running():
                current_view = self.ui_view.get_current_view()  # Adjust this method based on your implementation
                sleep_time = self.get_sleep_time_for_view(current_view)
                
                await asyncio.sleep(sleep_time)
                self.task_manager.start_all_tasks()

        except aiohttp.ClientError as e:
            log_message(f"An error occurred in App Main: {e}", level=logging.ERROR)
            self.exit_status = 1

        except asyncio.CancelledError:
            pass

        except KeyboardInterrupt:
            log_message("Keyboard interrupt detected. Exiting...")
            self.exit_status = 0

        except Exception as e:
            log_message(f"An error occurred in App Start {e}", level=logging.ERROR)
            self.exit_status = 1

        finally:
            await self.task_manager.stop_all_tasks()
            return self.exit_status
# -------------------------------------

# Helper Methods
    # Set Frame Rate - Set the frame rate of the application
    def set_frame_rate(self, frame_rate):
        frame_delay = 1 / frame_rate
        return frame_delay

    # Rate Limiting - Adjust the sleep time based on the current view for rate limiting
    # Rate limiting is used to prevent the application from using too much CPU
    def get_sleep_time_for_view(self, current_view):
        # Define sleep times based on different views or states
        if current_view == "game":
            return 0.01  # Full speed during the game
        elif current_view == "menu":
            return 0.1  # Slower during menu
        elif current_view == "lobby":
            return 0.1
        elif current_view == "login":
            return 0.1
        elif current_view == "splash":
            return 0.1
        else:
            return 0.05  # Default sleep time for other views


# -------------------------------------

# # View Methods - Basic view methods for displaying the splash screen and login screen
#     # Login Method
#     async def login(self):
#         try:
#             login_view = Login(self.stdscr)
#             while True:
#                 login_status = await login_view.run()

#                 if login_status is True:
#                     self.logged_in = True
#                     break
#                 elif login_status is False:
#                     continue
#                 elif login_status is None:
#                     break
#                 else:
#                     continue

#         except Exception as e:
#             log_message(f"Error logging in: {e}", level=logging.ERROR)
#             return False
#     # Splash Method
#     async def splash(self):
#         try:
#             splash_view = SplashView(self.stdscr)
#             splash_view.display_splash_screen()

#         except Exception as e:
#             log_message(f"Error displaying splash screen: {e}", level=logging.ERROR)
#             return False
# # -------------------------------------