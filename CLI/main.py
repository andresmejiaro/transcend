# main.py

import sys
import logging
import asyncio
import curses

from app.app import CLIApp
from utils.data_storage import initialize_data_directory
from utils.init_curses import initialize_curses, cleanup_curses
from utils.logger import initialize_logs_directory, initialize_logger, log_message

async def main(stdscr):
    try:
        initialize_data_directory()
        initialize_logs_directory()
        initialize_logger()
        initialize_curses(stdscr)

        log_message("Starting application", level=logging.DEBUG)
        cli = CLIApp(stdscr)
        log_message("CLIApp initialized", level=logging.DEBUG)
        exit_status = await cli.run()

    except KeyboardInterrupt:
        log_message("Keyboard interrupt detected. Exiting...")
        exit_status = 0

    except Exception as e:
        log_message("An error occurred:", level=logging.ERROR)
        logging.exception(e)
        exit_status = 1

    finally:
        cleanup_curses(stdscr)
        return exit_status

if __name__ == "__main__":
    try:
        exit_status = curses.wrapper(lambda stdscr: asyncio.run(main(stdscr), debug=True))
    except KeyboardInterrupt:
        log_message("Keyboard interrupt detected. Exiting...", level=logging.DEBUG)
        exit_status = 0
    except Exception as e:
        log_message("An error occurred:", level=logging.ERROR)
        logging.exception(e)
        exit_status = 1
    finally:
        sys.exit(exit_status)
