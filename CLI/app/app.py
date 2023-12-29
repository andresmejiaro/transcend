# app/app.py

from utils.logger import log_message
from utils.data_storage import load_data, load_texture, load_gif, save_data
from utils.url_macros import LOBBY_URI_TEMPLATE
from network.http_api import http_api
from app.function_views.splash_view import display_splash_screen
from app.class_views.login_view import Login
import logging
import asyncio
import curses
import aiohttp

class CLIApp:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.current_view = None
        self.exit_status = 0
        self.logged_in = False
        self.tasks = []
        self.api = http_api()


    async def lobby_websocket_send_and_receive_task(self, stdscr, messages_receive_queue, messages_send_queue):
        async with aiohttp.ClientSession() as session:
            client_info = load_data('client_info.json')
            client_id = client_info['client_id']
            await log_message(f"Connecting to websocket: {client_id}", level=logging.DEBUG)
            uri = LOBBY_URI_TEMPLATE.format(client_id=client_id)
            async with session.ws_connect(uri) as ws:
                try:
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            log_message(f"Received message: {msg.data}", level=logging.DEBUG)
                            await messages_receive_queue.put(msg.data)
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            break

                        # Send messages
                        while not messages_send_queue.empty():
                            message = await messages_send_queue.get()
                            log_message(f"Sending message: {message}", level=logging.DEBUG)
                            await ws.send_str(message)

                        await asyncio.sleep(0.1)

                    log_message("Websocket task completed", level=logging.DEBUG)

                except asyncio.CancelledError:
                    log_message("Websocket task cancelled", level=logging.DEBUG)
                    raise

                except Exception as e:
                    log_message(f"Websocket task error: {e}", level=logging.ERROR)
                    raise

    async def login(self):
        try:
            log_message("Running login view", level=logging.DEBUG)
            login_view = Login(self.stdscr, self.api)
            while True:
                login_status = await login_view.run()

                if login_status is True:
                    log_message("Login successful", level=logging.DEBUG)
                    self.logged_in = True
                    break
                elif login_status is False:
                    log_message("Login failed", level=logging.DEBUG)
                    continue
                else:
                    log_message("Login returned None, retrying...", level=logging.WARNING)
                    continue

        except Exception as e:
            log_message(f"Error logging in: {e}", level=logging.ERROR)
            return False

    async def run_main_loop(self, messages_receive_queue, messages_send_queue):
        try:
            # Set the frame delay
            frame_delay = 1/30
            while True:
                # Get the next message from the queue
                while not messages_receive_queue.empty():
                    message = await messages_receive_queue.get()
                    log_message(f"Message received: {message}", level=logging.DEBUG)

                # Update the current view
                if self.current_view is not None:
                    await self.current_view.update()

                # Render the current view
                if self.current_view is not None:
                    await self.current_view.render()

                # Get the next message from the queue
                while not messages_send_queue.empty():
                    message = await messages_send_queue.get()
                    log_message(f"Message sent: {message}", level=logging.DEBUG)

                await asyncio.sleep(frame_delay)

        except asyncio.CancelledError:
            # Catch the cancellation when leaving the view
            pass

        except Exception as e:
            log_message(f"An error occurred in Main Loop Task: {e}", level=logging.ERROR)
            self.exit_status = 1


    async def run(self):
        try:
            display_splash_screen(self.stdscr)

            await self.login()

            log_message("Logged in successfully", level=logging.DEBUG)

            # Create the queues for sending and receiving messages to the lobby websocket
            if self.logged_in:
                messages_receive_queue = asyncio.Queue()
                messages_send_queue = asyncio.Queue()

                # Create the task for sending and receiving messages to the lobby websocket
                lobby_websocket_task = asyncio.create_task(self.lobby_websocket_send_and_receive_task(self.stdscr, messages_receive_queue, messages_send_queue))

                main_loop_task = asyncio.create_task(self.run_main_loop(messages_receive_queue, messages_send_queue))
                # Keep list of tasks that are running
                self.tasks = [lobby_websocket_task, main_loop_task]

                # Use asyncio.gather to run tasks concurrently
                await asyncio.gather(lobby_websocket_task, main_loop_task)

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
