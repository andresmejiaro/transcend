# main.py

import asyncio
import curses
import signal
import atexit
from utils.init_views import initialize_views
from utils.logger import initialize_logs_directory, initialize_logger
from utils.data_storage import initialize_data_directory, save_data, load_data
from network.http_api import http_api
from network.ws_api import websocket_api

initialize_data_directory()
initialize_logs_directory()
initialize_logger()

async def main(stdscr):
    # Set up the terminal
    curses.cbreak()
    curses.noecho()
    stdscr.keypad(True)
    curses.curs_set(0)

    # Initialize APIs
    http = http_api()
    ws = websocket_api()

    # Initialize views
    all_views = initialize_views(stdscr, http, ws)

    # Start with the splash screen
    current_view_data = next(view_data for view_data in all_views if view_data["name"] == "SplashScreen")

    current_view = current_view_data["view"]

    try:
        while True:
            current_view.update_screen()

            # Get user input for the current view
            user_input = await current_view.get_user_input()

            if user_input is None:
                break  # Exit the loop on None

            current_view.process_input(user_input, all_views)

            # Check if the view wants to switch
            new_view = current_view.get_next_view()

            if new_view:
                current_view = new_view

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        pass
    finally:
        # Clean up the terminal settings
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
