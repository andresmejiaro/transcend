# main.py

import asyncio
import curses
import signal
import atexit
import logging
from utils.init_views import initialize_views
from utils.logger import initialize_logs_directory, initialize_logger
from utils.data_storage import initialize_data_directory, save_data, load_data
from utils.logger import log_message
from network.http_api import http_api
from network.ws_api import websocket_api

initialize_data_directory()
initialize_logs_directory()
initialize_logger()

async def get_user_input_with_timeout(current_view, timeout):
    try:
        user_input = await asyncio.wait_for(current_view.get_user_input(), timeout=timeout)
        return user_input
    except asyncio.TimeoutError:
        return None  # Return None if no input within the timeout

async def connect_to_lobby_websocket(ws):
    try:
        is_lobby_connected = await ws.connected("lobby")

        if not is_lobby_connected:
            client_info = load_data("client_info.json")
            if client_info:
                await ws.connect("lobby", f"ws://localhost:8001/ws/lobby2/?client_id={client_info['client_id']}")         
            else:
                log_message("Client info not found", level=logging.ERROR)
        else:
            log_message("Lobby WebSocket already connected", level=logging.INFO)

    except Exception as e:
        log_message(f"Error connecting to lobby WebSocket: {e}", level=logging.ERROR)

async def update_lobby_messages(ws, current_view):
    try:
        while True:
            message = await ws.receive_messages_forever("lobby")
            current_view.handle_lobby_message(message)
    except asyncio.CancelledError:
        log_message("Cancelled lobby message loop", level=logging.INFO)
        pass


async def main(stdscr):
    # Set up the terminal
    curses.cbreak()
    curses.noecho()
    stdscr.keypad(True)
    curses.curs_set(0)

    http = http_api()
    ws = websocket_api()

    all_views = initialize_views(stdscr, http, ws)

    # Start with the splash screen
    current_view_data = next(view_data for view_data in all_views if view_data["name"] == "SplashScreen")
    current_view = current_view_data["view"]

    try:
        while True:
            current_view.update_screen(all_views)

            # Get user input for the current view
            user_input = await get_user_input_with_timeout(current_view, timeout=0.1)

            if user_input is None:
                continue  # Exit the loop on None

            current_view.process_input(user_input)

            # Check if the view wants to switch
            new_view = current_view.get_next_view()

            log_message(f"Current view: {current_view}, Next view: {new_view if new_view else None}", level=logging.INFO)

            if new_view:
                current_view = new_view

                # Connect to the lobby WebSocket after a successful login
                home_view_instance = next(view_data["view"] for view_data in all_views if view_data["name"] == "Home")

                if isinstance(current_view, type(home_view_instance)):
                    await connect_to_lobby_websocket(ws)

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        pass
    finally:
        # Clean up the terminal settings
        await ws.disconnect("lobby")
        curses.nocbreak()
        curses.echo()
        stdscr.keypad(False)
        
        # Make the cursor visible before cleanup
        curses.curs_set(1)

        curses.endwin()  # Cleanup curses on exit

if __name__ == "__main__":
    # Set up signal handling for Ctrl+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Register cleanup function for atexit
    atexit.register(curses.endwin)

    # Run the main function using curses.wrapper to handle initialization and cleanup
    asyncio.run(curses.wrapper(main))
