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
    return 1 / frame_rate

def set_process_speed(process_speed):
    return 1 / process_speed

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
        self.frame_rate = [1]
        self.process_speed = [1]

# Essential App Tasks - These tasks are essential to the application and will be created
    # Keyboard Input Task - Get keyboard input and put it in the keyboard input queue
    async def keyboard_task(self, data):
        try:
            log_message("Keyboard Input Task started", level=logging.DEBUG)
            while True:
                key = self.stdscr.getch()
                if key != curses.ERR:
                #     async with data["receive_lock"]:
                #         await data["receive_queue"].put(key)
                #         log_message(f"Received key: {key}", level=logging.DEBUG)
                    await self.ui_view.process_keyboard_input(key)

                await asyncio.sleep(0.001)

        except asyncio.CancelledError:
            log_message("Keyboard Task cancelled", level=logging.DEBUG)
        except Exception as e:
            log_message(f"An error occurred in Keyboard Input Task: {e}", level=logging.ERROR)
            self.exit_status = 1

    # Draw Loop Task - Allows us to set a frame rate and have each class view control it
    async def ui_draw_task(self, data):
        try:
            log_message("Launching UI", level=logging.DEBUG)
            while True:
                await self.ui_view.draw()

                await asyncio.sleep(set_frame_rate(self.frame_rate[0]))

        except asyncio.CancelledError:
            log_message("UI Task cancelled", level=logging.DEBUG)
        except KeyboardInterrupt:
            # Catch the keyboard interrupt
            log_message("Keyboard interrupt detected. Exiting...")
            self.exit_status = 0
        except Exception as e:
            log_message(f"An error occurred in UI Task: {e}", level=logging.ERROR)
            self.exit_status = 1

    # UI Input Task - Allows us to set a process speed and have each class view control it
    async def ui_handle_input_task(self, data):
        try:
            log_message("Launching UI", level=logging.DEBUG)
            while True:
                await self.ui_view.process_input()

                next_view = self.ui_view.get_next_view()

                await asyncio.sleep(set_process_speed(self.process_speed[0]))

                if next_view == "exit":
                    log_message("Exiting UI", level=logging.DEBUG)
                    # await self.task_manager.stop_all_tasks()
                    self.task_manager.is_running = False
                    raise asyncio.CancelledError
                    # break
                
                elif next_view is not None:
                    self.ui_view = next_view
                    continue

        except asyncio.CancelledError:
            log_message("UI Task cancelled", level=logging.DEBUG)
        except KeyboardInterrupt:
            # Catch the keyboard interrupt
            log_message("Keyboard interrupt detected. Exiting...")
            self.exit_status = 0
        except Exception as e:
            log_message(f"An error occurred in UI Task: {e}", level=logging.ERROR)
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
            self.ui_controller.add_shared_data("keyboard", keyboard_data)
            self.ui_controller.add_shared_data("UI", ui_data)
            
            tasks = [

                self.task_manager.create_task(task_name="UI_draw", task_func=self.ui_draw_task, data=ui_data),
                self.task_manager.create_task(task_name="UI", task_func=self.ui_handle_input_task, data=ui_data),
                self.task_manager.create_task(task_name="keyboard", task_func=self.keyboard_task, data=keyboard_data),
            ]

            # Initialize the UI starting view
            self.ui_view = SplashView(self.stdscr, self.ui_controller, self.frame_rate, self.process_speed, self.task_manager)

            # Start all tasks
            while self.task_manager.is_running():
                await asyncio.sleep(0.001)
                self.task_manager.start_all_tasks()

            # self.exit_status = await asyncio.gather(*tasks)

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
            # self.task_manager.stop_all_tasks()
            return self.exit_status

