# views/init_curses.py

import curses

def initialize_curses(stdscr):
    # Clear the screen
    stdscr.clear()
    # Hide the cursor
    curses.curs_set(0)
    # React to keys instantly without requiring Enter to be pressed
    curses.cbreak()
    # Make getch() non-blocking
    stdscr.nodelay(True)
    # Don't echo keyboard input
    curses.noecho()
    # Enable keypad mode
    stdscr.keypad(True)
    # Allow for color
    curses.start_color()

    # Define color pairs
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Example: White text on black background
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Example: Black text on white background
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)    # Example: Red text on black background
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Example: Green text on black background
    curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Example: Yellow text on black background
    curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)   # Example: Blue text on black background
    curses.init_pair(7, curses.COLOR_MAGENTA, curses.COLOR_BLACK)# Example: Magenta text on black background

    # Set a default color pair
    stdscr.attron(curses.color_pair(1))

def cleanup_curses(stdscr):
    # Make the cursor visible before cleanup
    curses.curs_set(1)
    # Clean up the terminal settings
    curses.nocbreak()
    # Make getch() blocking
    stdscr.nodelay(False)
    # Enable echo
    curses.echo()
    # Disable keypad mode
    stdscr.keypad(False)
    # Clear the screen
    stdscr.clear()
    # Refresh the screen
    stdscr.refresh()

