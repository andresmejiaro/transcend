# app/function_views/splash_view.py

from utils.logger import log_message
from utils.data_storage import load_texture
import logging
import curses
import time

def display_splash_screen(stdscr):
    try:
        current_frame = 1

        # Calculate the delay to achieve 60 FPS
        frame_rate = 2
        frame_delay = 1 / frame_rate

        while True:
            stdscr.clear()

            # Get the terminal size
            rows, cols = stdscr.getmaxyx()

            if rows < 24 or cols < 80:
                stdscr.addstr(0, 0, "Terminal size is too small")

            else:
                # Load Logo frames
                logo_frame_1 = load_texture("logo.txt")
                logo_frame_2 = load_texture("logo2.txt")

                # Display the logo centered on the screen
                if current_frame == 1 and logo_frame_1:
                    logo = logo_frame_1
                elif current_frame == 2 and logo_frame_2:
                    logo = logo_frame_2
                else:
                    # Handle a case where both frames are not available
                    stdscr.addstr(0, 0, "Error loading logo frames")
                    stdscr.refresh()
                    break  # Exit the loop in case of an error

                logo_row = max(0, (rows - len(logo)) // 2)
                col = max(0, (cols - len(logo[0])) // 2)
                for i, line in enumerate(logo):
                    stdscr.addstr(logo_row + i, col, line)

                # Display a static message right under the logo
                message = "Welcome to the Game!\nPress Enter to start..."
                text_row = logo_row + len(logo) + 1  # Add 1 for spacing
                col = max(0, (cols - len(message.splitlines()[0])) // 2)
                for i, line in enumerate(message.splitlines()):
                    stdscr.addstr(text_row + i, col, line)

            # Refresh the screen
            stdscr.refresh()

            # Adjust the delay to achieve the desired frame rate
            time.sleep(frame_delay)

            # Toggle between frames
            current_frame = 1 if current_frame == 2 else 2

            # Wait for the user to press any key
            user_input = stdscr.getch()

            if user_input == curses.KEY_RESIZE:
                # Handle terminal resize by redrawing the splash screen
                continue
            elif user_input != -1:
                break  # Break the loop when any key is pressed

    except Exception as e:
        log_message(f"Error displaying splash screen: {e}", level=logging.ERROR)
