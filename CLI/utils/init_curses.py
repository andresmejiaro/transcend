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
