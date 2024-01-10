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
from app.class_views.splash_view import SplashView


def set_frame_rate(frame_rate):
    frame_delay = 1 / frame_rate
    return frame_delay

def set_process_speed(process_speed):
    process_delay = 1 / process_speed
    return process_delay

class CLIApp:
    def __init__(self, stdscr):
        self.stdscr = stdscr  # The curses screen object
        self.ui_view = None  # The current view being displayed initialized to None
        self.exit_status = 0  # The exit status of the application - 0 is success, 1 is failure
        self.logged_in = True  # The logged in status of the application
        self.file_manager = FileManager()  # The file manager object - Used to load and save data to files
        self.task_manager = TaskManager()  # The task manager object - Used to create and manage tasks
        self.ui_controller = UIController(stdscr=self.stdscr, task_manager=self.task_manager)  # The UI controller object - Used to manage the UI and shared data between tasks
        # Adjust App Frame Rate - Adjust the frame rate of the application
        self.frame_rate = [30]
        self.process_speed = [10]

# Essential App Tasks - These tasks are essential to the application and will be created
    # Lobby Websocket Task - Connect to the lobby websocket and send and receive messages
    # async def websocket_receive(self, data):
    #     try:
    #         async with aiohttp.ClientSession() as session:
    #             token_info = self.file_manager.load_data('token.json')
    #             token = token_info['token']
    #             uri = LOBBY_URI_TEMPLATE.format(token=token)
    #             log_message(f"Connecting to websocket: {uri}", level=logging.INFO)
    #             async with session.ws_connect(uri) as ws:
    #                 try:
    #                     # Create a task to check the send_queue periodically
    #                     send_task = asyncio.create_task(self.websocket_send(data, ws))

    #                     async for msg in ws:
    #                         if msg.type == aiohttp.WSMsgType.TEXT:
    #                             async with data["receive_lock"]:
    #                                 await data["receive_queue"].put(msg.data)
    #                                 log_message(f"Received message: {msg.data}", level=logging.DEBUG)
    #                         elif msg.type == aiohttp.WSMsgType.ERROR:
    #                             break

    #                     log_message("Websocket task completed", level=logging.DEBUG)

    #                 except (asyncio.CancelledError, GeneratorExit):
    #                     log_message("Websocket task cancelled", level=logging.DEBUG)
    #                     raise
    #                 except Exception as e:
    #                     log_message(f"Websocket task error: {e}", level=logging.ERROR)
    #                     raise

    #     except asyncio.CancelledError:
    #         # Catch the cancellation when leaving the view
    #         pass
    #     except aiohttp.ClientError as e:
    #         log_message(f"An error occurred in Lobby Websocket Task: {e}", level=logging.ERROR)
    #         self.exit_status = 1
    #     except Exception as e:
    #         log_message(f"An error occurred in Lobby Websocket Task: {e}", level=logging.ERROR)
    #         self.exit_status = 1
    #     finally:
    #         # Cancel the send_task when the websocket task is cancelled
    #         if send_task:
    #             send_task.cancel()



    # async def websocket_send(self, send_data):
    #         try:
    #             ws = ws
    #             data = self.ui_controller.get_shared_data(send_data["task_name"])
    #             while True:
    #                 # Check for outgoing messages in the send_queue
    #                 while not data["send_queue"].empty():
    #                     log_message("Lobby has a message pending to send", level=logging.DEBUG)
    #                     async with data["send_lock"]:
    #                         message = await data["send_queue"].get()
    #                         await ws.send_str(message)
    #                         log_message(f"Sent message: {message}", level=logging.DEBUG)

    #                 # Sleep for a short duration before checking again
    #                 await asyncio.sleep(0.1)

    #         except asyncio.CancelledError:
    #             # If the task is cancelled, exit the loop
    #             log_message("Websocket send task cancelled", level=logging.DEBUG)
    #             raise
    #         except Exception as e:
    #             log_message(f"Websocket send task error: {e}", level=logging.ERROR)
    #             raise
        
    # async def connect_ws_task(self, data):
    #     try:
    #         async with aiohttp.ClientSession() as session:
    #             token_info = self.file_manager.load_data('token.json')
    #             token = token_info['token']
    #             uri = data['uri']
    #             formatted_uri = uri.format(token=token)
    #             log_message(f"Connecting to websocket: {formatted_uri}", level=logging.INFO)
    #             ws_data ={
    #                 "receive_queue": asyncio.Queue(),
    #                 "send_queue": asyncio.Queue(),
    #                 "receive_lock": asyncio.Lock(),
    #                 "send_lock": asyncio.Lock(),                    
    #             }
    #             self.ui_controller.add_shared_data(f'{data["task_name"]}', ws_data)
    #             async with session.ws_connect(formatted_uri) as ws:
    #                 try:
    #                     send_data = {
    #                         "task_name": f'{data["task_name"]}_send',
    #                         "uri": formatted_uri,
    #                         "ws": ws,
    #                     }
    #                     # Create a task to check the send_queue periodically
    #                     self.task_manager.create_task(task_name=f'{data["task_name"]}_send', task_func=self.websocket_send, data=send_data)
                        
    #                     async for msg in ws:
    #                         if msg.type == aiohttp.WSMsgType.TEXT:
    #                             async with ws_data["receive_lock"]:
    #                                 await ws_data["receive_queue"].put(msg.data)
    #                                 log_message(f"Received message: {msg.data}", level=logging.DEBUG)
    #                         elif msg.type == aiohttp.WSMsgType.ERROR:
    #                             break

    #                     log_message("Websocket task completed", level=logging.DEBUG)
                        
    #                 except (asyncio.CancelledError, GeneratorExit):
    #                     log_message("Websocket task cancelled", level=logging.DEBUG)
    #                     raise
    #                 except Exception as e:
    #                     log_message(f"Websocket task error: {e}", level=logging.ERROR)
    #                     raise
                        
    #     except (asyncio.CancelledError, GeneratorExit):
    #         log_message("Websocket task cancelled", level=logging.DEBUG)
    #         raise
    #     except aiohttp.ClientError as e:
    #         log_message(f"An error occurred in Lobby Websocket Task: {e}", level=logging.ERROR)
    #         self.exit_status = 1
    #     except Exception as e:
    #         log_message(f"An error occurred in Lobby Websocket Task: {e}", level=logging.ERROR)
    #         self.exit_status = 1
    
    
    # -------------------------------------

    # Keyboard Input Task - Get keyboard input and put it in the keyboard input queue
    async def keyboard_task(self, data):
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
    # -------------------------------------

    # Main Loop Task - Run the main loop of the application
    async def ui_draw_task(self, data):
        try:
            log_message("Launching UI", level=logging.DEBUG)
            while True:
                await self.ui_view.draw()

                await asyncio.sleep(set_frame_rate(self.frame_rate[0]))

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

    async def ui_handle_input_task(self, data):
        try:
            log_message("Launching UI", level=logging.DEBUG)
            # Start the UI with the splash screen
            # self.ui_view = SplashView(self.stdscr, self.ui_controller, self.frame_rate, self.process_speed)
            while True:
                await self.ui_view.process_input()

                next_view = self.ui_view.get_next_view()

                await asyncio.sleep(set_process_speed(self.process_speed[0]))

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




        except asyncio.CancelledError:
            # Catch the cancellation when leaving the view
            pass
        except aiohttp.ClientError as e:
            log_message(f"An error occurred in Lobby Websocket Task: {e}", level=logging.ERROR)
            self.exit_status = 1
        except Exception as e:
            log_message(f"An error occurred in Lobby Websocket Task: {e}", level=logging.ERROR)
            self.exit_status = 1


    # Entry Point - Initializes tasks and runs the main loop, additionally tasks will be created and started and stopped
    async def start(self):
        try:
            # Create keyboard data Queues and Locks which will be shared between tasks
            keyboard_data = {
                "receive_queue": asyncio.Queue(),
                "receive_lock": asyncio.Lock(),
            }

            # Create UI data Queues and Locks which will be shared between tasks
            ui_data = {
                "receive_queue": asyncio.Queue(),
                "send_queue": asyncio.Queue(),
                "receive_lock": asyncio.Lock(),
                "send_lock": asyncio.Lock(),
            }

            # Add shared data to the UI controller
            # self.ui_controller.add_shared_data("lobby", ws_data)
            self.ui_controller.add_shared_data("keyboard", keyboard_data)
            self.ui_controller.add_shared_data("UI", ui_data)
            
            tasks = [

                self.task_manager.create_task(task_name="keyboard", task_func=self.keyboard_task, data=keyboard_data),
                self.task_manager.create_task(task_name="UI", task_func=self.ui_handle_input_task, data=ui_data),
                self.task_manager.create_task(task_name="UI_draw", task_func=self.ui_draw_task, data=ui_data),
            ]

            # Initialize the UI starting view
            self.ui_view = SplashView(self.stdscr, self.ui_controller, self.frame_rate, self.process_speed, self.task_manager)

            # Start all tasks
            self.exit_status = await asyncio.gather(*tasks)

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
            # self.ui_controller.cleanup()

    # -------------------------------------
