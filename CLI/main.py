# main.py

from app.app import CLIApp
from utils.logger import initialize_logs_directory, initialize_logger, log_message
from utils.data_storage import initialize_data_directory
from utils.init_curses import intialize_curses, cleanup_curses
import logging
import asyncio
import curses

async def main(stdscr):
    try:
        initialize_data_directory()
        initialize_logs_directory()
        initialize_logger()
        intialize_curses(stdscr)

        cli = CLIApp(stdscr)
        exit_status = await cli.run()

    except KeyboardInterrupt:
        log_message("Keyboard interrupt detected. Exiting...")
        exit_status = 0

    except Exception as e:
        log_message(f"An error occurred: {e}", level=logging.ERROR)
        exit_status = 1

    finally:
        cleanup_curses(stdscr)
        return exit_status


if __name__ == "__main__":
    try:
        exit_status = 0
        curses.wrapper(lambda stdscr: asyncio.run(main(stdscr)))

    except KeyboardInterrupt:
        log_message("Keyboard interrupt detected. Exiting...")
        exit_status = 0

    except Exception as e:
        log_message(f"An error occurred: {e}", level=logging.ERROR)
        exit_status = 1

    finally:
        exit(exit_status)

        

