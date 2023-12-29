# views/init_curses.py

import curses

def intialize_curses(stdscr):
    # Initialize Curses
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
    # Enable color mode    
    curses.start_color()
    # Use default colors
    curses.use_default_colors()
    # Enable keypad mode
    stdscr.keypad(True)

def cleanup_curses(stdscr):
    # Clean up the terminal settings
    curses.nocbreak()
    # Enable echo
    curses.echo()
    # Disable keypad mode
    stdscr.keypad(False)
    # Make the cursor visible before cleanup
    curses.curs_set(1)
    # Clear the screen
    stdscr.clear()
    # Refresh the screen
    stdscr.refresh()
