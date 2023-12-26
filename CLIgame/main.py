# main.py

import asyncio
import curses
import signal
import atexit
from app.home.splash_screen import SplashScreen
from utils.input_handler import get_user_ch
from utils.logger import initialize_logs_directory, initialize_logger
from utils.data_storage import initialize_data_directory, save_data, load_data

initialize_data_directory()
initialize_logs_directory()
initialize_logger()

async def main(stdscr):
    # Set up the terminal
    curses.cbreak()
    curses.noecho()
    stdscr.keypad(True)

    # Hide the cursor at the beginning
    curses.curs_set(0)

    main_menu = SplashScreen(stdscr)

    current_view = main_menu

    try:
        while True:
            current_view.update_screen()
            
            user_input = await get_user_ch(stdscr)
            if user_input is None:
                break  # Exit the loop on None

            current_view.process_input(user_input)

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