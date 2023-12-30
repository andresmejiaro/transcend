# app/app.py

import logging
import asyncio
import curses
import aiohttp

from utils.logger import log_message
from utils.data_storage import load_data, load_texture, load_gif, save_data
from utils.url_macros import LOBBY_URI_TEMPLATE
from network.http_api import http_api
from app.class_views.login_view import Login
from app.class_views.home_view import HomePage

from app.class_views.splash_view import SplashView

class CLIApp:
    def __init__(self, stdscr):
        self.stdscr = stdscr        # The curses screen object
        self.current_view = None    # The current view being displayed
        self.exit_status = 0    
        self.logged_in = False
        self.tasks = []             # List of tasks that are running
        self.api = http_api()
        self.recieve_message_lock = asyncio.Lock()
        self.send_message_lock = asyncio.Lock()
        self.keyboard_input_lock = asyncio.Lock()
        self.frame_rate = 10
        
# Lobby Websocket Task - Connect to the lobby websocket and send and receive messages throught the duration of the application
    async def lobby_websocket_send_and_receive_task(self, stdscr, messages_receive_queue, messages_send_queue):
        async with aiohttp.ClientSession() as session:
            client_info = load_data('client_info.json')
            client_id = client_info['client_id']
            uri = LOBBY_URI_TEMPLATE.format(client_id=client_id)
            async with session.ws_connect(uri) as ws:
                try:
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            async with self.recieve_message_lock:
                                await messages_receive_queue.put(msg.data)
                                log_message(f"Received message: {msg.data}", level=logging.DEBUG)
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            break

                        # Send messages
                        while not messages_send_queue.empty():
                            async with self.send_message_lock:
                                message = await messages_send_queue.get()
                                await ws.send_str(message)
                                log_message(f"Sent message: {message}", level=logging.DEBUG)

                        await asyncio.sleep(1)

                    log_message("Websocket task completed", level=logging.DEBUG)

                except asyncio.CancelledError:
                    log_message("Websocket task cancelled", level=logging.DEBUG)
                    raise

                except Exception as e:
                    log_message(f"Websocket task error: {e}", level=logging.ERROR)
                    raise

# Keyboard Input Task - Get keyboard input and put it in the keyboard input queue
    async def keyboard_input_task(self, keyboard_input_queue):
        try:
            while True:
                key = self.stdscr.getch()
                if key != curses.ERR:
                    # Convert the key code to the key name
                    key_name = curses.keyname(key).decode('utf-8')

                    async with self.keyboard_input_lock:
                        await keyboard_input_queue.put(key_name)
                        log_message(f"Key pressed: {key_name}, added to queue", level=logging.DEBUG)

                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            # Catch the cancellation when leaving the view
            pass

        except Exception as e:
            log_message(f"An error occurred in Keyboard Input Task: {e}", level=logging.ERROR)
            self.exit_status = 1

# Splash and Login Method
    async def login(self):
        try:
            login_view = Login(self.stdscr, self.api)
            while True:
                login_status = await login_view.run()

                if login_status is True:
                    self.logged_in = True
                    break
                elif login_status is False:
                    continue
                elif login_status is None:
                    break
                else:
                    continue

        except Exception as e:
            log_message(f"Error logging in: {e}", level=logging.ERROR)
            return False

    async def splash(self):
        try:
            splash_view = SplashView(self.stdscr)
            await splash_view.display_splash_screen()

        except Exception as e:
            log_message(f"Error displaying splash screen: {e}", level=logging.ERROR)
            return False
# -------------------------------------

# Main Loop Task - Run the main loop of the application
    async def run_main_loop(self):
        try:
            while True:
                await self.current_view.update_screen()

                await self.current_view.process_lobby_recv_message()

                await self.current_view.process_inputs()

                next_view = await self.current_view.get_next_view()

                if next_view is not None:
                    self.current_view = next_view
                    continue

                await asyncio.sleep(self.set_frame_rate(self.frame_rate))

        except asyncio.CancelledError:
            log_message("Main Loop Task cancelled", level=logging.DEBUG)
            await self.current_view.cleanup()

        except KeyboardInterrupt:
            # Catch the keyboard interrupt
            log_message("Keyboard interrupt detected. Exiting...")
            await self.current_view.cleanup()
            self.exit_status = 0

        except Exception as e:
            log_message(f"An error occurred in Main Loop Task: {e}", level=logging.ERROR)
            await self.current_view.cleanup()
            self.exit_status = 1
# -------------------------------------

# Entry Point - Initializes the application and runs the main loop
    async def run(self):
        try:
            await self.splash()
            await self.login()

            # Create the queues for sending and receiving messages to the lobby websocket
            if self.logged_in:
                messages_receive_queue = asyncio.Queue()
                messages_send_queue = asyncio.Queue()
                keyboard_input_queue = asyncio.Queue()

                # Create an instance of HomePage with parameters
                self.current_view = HomePage(
                    stdscr=self.stdscr,
                    messages_send_queue=messages_send_queue,
                    messages_receive_queue=messages_receive_queue,
                    send_message_lock=self.send_message_lock,
                    receive_message_lock=self.recieve_message_lock,
                    keyboard_input_queue=keyboard_input_queue,
                    keyboard_input_lock=self.keyboard_input_lock
                    )

                # Create the task for sending and receiving messages to the lobby websocket and the main loop task
                lobby_websocket_task = asyncio.create_task(self.lobby_websocket_send_and_receive_task(self.stdscr, messages_receive_queue, messages_send_queue))
                main_loop_task = asyncio.create_task(self.run_main_loop())
                keyboard_input_task = asyncio.create_task(self.keyboard_input_task(keyboard_input_queue))
                
                # Keep list of tasks that are running so they can be cancelled when exiting
                self.tasks = [lobby_websocket_task, main_loop_task, keyboard_input_task]

                # Use asyncio.gather to run tasks concurrently and wait for them to complete
                # For temporary websocket connections inside the main loop we will handle withing the main loop eg(pong game, chat rooms, etc)
                await asyncio.gather(lobby_websocket_task, main_loop_task, keyboard_input_task)

        except asyncio.CancelledError:
            # Catch the cancellation when leaving the view
            pass

        except KeyboardInterrupt:
            # Catch the keyboard interrupt
            log_message("Keyboard interrupt detected. Exiting...")
            self.exit_status = 0

        except Exception as e:
            log_message(f"An error occurred in App Main {e}", level=logging.ERROR)
            self.exit_status = 1

        finally:
            # Cancel all tasks
            for task in self.tasks:
                task.cancel()

            return self.exit_status
# -------------------------------------

# Helper Methods
    def set_frame_rate(self, frame_rate):
        frame_delay = 1 / frame_rate
        return frame_delay