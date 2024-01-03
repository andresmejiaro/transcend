# app/app.py

import logging
import asyncio
import curses
import aiohttp
import functools

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
        self.ui_view = None         # The current view being displayed initialized to None
        self.exit_status = 0        # The exit status of the application - 0 is success, 1 is failure (will expand on this later)
        self.logged_in = True       # The logged in status of the application 
        self.file_manager = FileManager()   # The file manager object - Used to load and save data to files
        self.task_manager = TaskManager()   # The task manager object - Used to create and manage tasks

        # Adjust App Frame Rate - Adjust the frame rate of the application
        self.frame_rate = [60]

# Essential App Tasks - These tasks are essential to the application and will be created and started in the main loop
    # Lobby Websocket Task - Connect to the lobby websocket and send and receive messages throught the duration of the application
    async def lobby_websocket_send_and_receive_task(self, data):
        try:
            async with aiohttp.ClientSession() as session:
                token_info = self.file_manager.load_data('token.json')
                token = token_info['token']
                uri = LOBBY_URI_TEMPLATE.format(token=token)
                log_message(f"Connecting to websocket: {uri}", level=logging.INFO)
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
                    
        except asyncio.CancelledError:
            # Catch the cancellation when leaving the view
            pass
        except aiohttp.ClientError as e:
            log_message(f"An error occurred in Lobby Websocket Task: {e}", level=logging.ERROR)
            self.exit_status = 1
        except Exception as e:
            log_message(f"An error occurred in Lobby Websocket Task: {e}", level=logging.ERROR)
            self.exit_status = 1

    # Keyboard Input Task - Get keyboard input and put it in the keyboard input queue
    async def keyboard_input_task(self, data):
        try:
            log_message("Keyboard Input Task started", level=logging.DEBUG)
            while True:
                key = self.stdscr.getch()
                if key != curses.ERR:
                    # Convert the key code to the key name
                    # key_name = curses.keyname(key).decode('utf-8')

                    async with data["receive_lock"]:
                        await data["receive_queue"].put(key)
                        log_message(f"Received key: {key}", level=logging.DEBUG)

                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            # Catch the cancellation when leaving the view
            pass

        except Exception as e:
            log_message(f"An error occurred in Keyboard Input Task: {e}", level=logging.ERROR)
            self.exit_status = 1

    # Main Loop Task - Run the main loop of the application
    async def launch_UI(self):
        try:
            log_message("Launching UI", level=logging.DEBUG)
            # Start the UI with the splash screen
            self.ui_view = SplashView(self.stdscr, self.ui_controller, self.frame_rate)
            while True:
                await self.ui_view.draw()
                await self.ui_view.process_input()

                next_view = self.ui_view.get_next_view()
                
                await asyncio.sleep(self.set_frame_rate(self.frame_rate[0]))

                if next_view == "exit":
                    log_message("Exiting UI", level=logging.DEBUG)
                    break
                elif next_view is not None:
                    self.ui_view = next_view
                    continue

        except asyncio.CancelledError:
            log_message("UI Task cancelled", level=logging.DEBUG)
            await self.ui_view.cleanup()
        except KeyboardInterrupt:
            # Catch the keyboard interrupt
            log_message("Keyboard interrupt detected. Exiting...")
            await self.ui_view.cleanup()
            self.exit_status = 0
        except Exception as e:
            log_message(f"An error occurred in UI Task: {e}", level=logging.ERROR)
            await self.ui_view.cleanup()
            self.exit_status = 1

# -------------------------------------

# Entry Point - Initializes tasks and runs the main loop, additionaly tasks will be created and started and stopped as needed in the main loop
    async def start(self):
        try:
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
            self.ui_controller = UIController(stdscr=self.stdscr)

            self.ui_controller.add_shared_data("lobby", lobby_ws_data)
            self.ui_controller.add_shared_data("keyboard", keyboard_input_data)

            # Start all tasks
            await asyncio.gather(
                self.task_manager.start_task_by_name("lobby"),
                self.task_manager.start_task_by_name("keyboard"),
                await self.launch_UI(),
            )

        except aiohttp.ClientError as e:
            log_message(f"AIOHTTP ERROR in app.start: {e}", level=logging.ERROR)
            self.exit_status = 1
        except asyncio.CancelledError as e:
            log_message(f"Asyncio ERROR in app.start: {e}", level=logging.ERROR)
            self.exit_status = 1
        except KeyboardInterrupt:
            log_message("Keyboard interrupt detected. Exiting...")
            self.exit_status = 0
        except Exception as e:
            log_message(f"ERROR in app.start {e}", level=logging.ERROR)
            self.exit_status = 1
        finally:
            await self.task_manager.stop_all_tasks()
            await self.ui_controller.cleanup()
            return self.exit_status
# -------------------------------------

# Helper Methods
    # Set Frame Rate - Set the frame rate of the application
    def set_frame_rate(self, frame_rate):
        frame_delay = 1 / frame_rate
        return frame_delay
# # -------------------------------------
