# main.py

import sys
import logging
import asyncio
import curses
import click
import json
import sqlite3
from getpass import getpass
from cryptography.fernet import Fernet

from app.app import CLIApp
from utils.logger import log_message
from utils.config_manager import ConfigurationManager
from utils.file_manager import FileManager

async def main(stdscr, username, password):
    exit_status = 0
    try:
        config_manager = ConfigurationManager()
        file_manager = FileManager()

        file_manager.save_data("user.json", {"username": username, "password": password})

        config_manager.load_configuration_file(stdscr)

        try:
            app = CLIApp(stdscr)
            exit_status = await app.start()

        except Exception as e:
            log_message(f'Error starting the App: {e}', logging.ERROR)
            exit_status = 1

        finally:
            config_manager.cleanup()
            sys.exit(exit_status)
            

            
    except KeyError:
        log_message('KeyError in main.', logging.ERROR)
        exit_status = 1

    except Exception as e:
        log_message(f'Error in main: {e}', logging.ERROR)
        exit_status = 1

    except KeyboardInterrupt:
        log_message('Keyboard interrupt detected.')
        exit_status = 0



# Boot Launch   
def run_main_with_username_password(username, password):
    exit_status = 0
    try:
        print('Boot Launch')

        loop = asyncio.get_event_loop()
        loop.set_debug(True)

        exit_status = curses.wrapper(lambda stdscr: loop.run_until_complete(main(stdscr, username, password)))
        
        loop.close()

        log_message(f'Exit Status: {exit_status}', logging.INFO)
        return exit_status
    
    except KeyboardInterrupt:
        log_message('Keyboard interrupt detected.')
        exit_status = 0
        return exit_status
    
    except Exception as e:
        log_message(f'Error: Boot Launch {e}')
        exit_status = 1
        return exit_status


# click CLI, commented out during development
# @click.command()
# @click.option('--username', prompt='Enter your username', help='Username')
# @click.option('--password', prompt='Enter your password', help='Password')

def cli():
    username = 'splix'
    password = '123'
    try:
        exit_status = run_main_with_username_password(username, password)
        sys.exit(exit_status)
        
    except Exception as e:
        print(f'Error: CLI {e}')
        sys.exit(exit_status)
        
if __name__ == "__main__":
    cli()
