# main.py

import sys
import logging
import asyncio
import curses
import click

from app.app import CLIApp
from utils.logger import log_message
from utils.config_manager import ConfigurationManager
from utils.file_manager import FileManager
from network.http_api import http_api

api = http_api()

async def main(stdscr):
    exit_status = 0
    try:
        config_manager = ConfigurationManager()
        config_manager.load_configuration_file(stdscr)

        try:
            app = CLIApp(stdscr)
            exit_status = await app.start()

        except Exception as e:
            log_message(f'Error starting the App: {e}', logging.ERROR)
            exit_status = 1
        finally:
            # config_manager.cleanup()
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
    finally:
        log_message(f'Exit Status: {exit_status}', logging.INFO)
        sys.exit(exit_status)


def cli():
    exit_status = 0
    try:
        loop = asyncio.get_event_loop()
        loop.set_debug(True)

        exit_status = curses.wrapper(lambda stdscr: loop.run_until_complete(main(stdscr)))
        # loop.close()

        log_message(f'Exit Status: {exit_status}', logging.INFO)

    except KeyboardInterrupt:
        log_message('Keyboard interrupt detected.')
        print('Keyboard interrupt detected.')
        exit_status = 0
    except Exception as e:
        log_message(f'Error: Boot Launch {e}')
        print(f'Error: Boot Launch {e}')
        exit_status = 1

    finally:
        log_message(f'Exit Status: {exit_status}', logging.INFO)
        sys.exit(exit_status)


def login_user(username, password):
    try:
        response = api.login(username, password)

    except Exception as e:
        print(f"Unable to reach the server: {e}")
        sys.exit(1)

    if response == "User not found":
        # Unsuccessful login
        print(f"Login failed: {response}")
    elif response == username:
        # Successful login
        print(f"Login successful. Welcome, {username}!")
        cli()  # Start the CLI
    else:
        print("Server did not respond.")
        sys.exit(1)


def register_user(username, password, full_name, email):
    try:
        response = api.register(username, password, full_name, email)

    except Exception as e:
        print(f"Unable to reach the server: {e}")
        sys.exit(1)

    if response == "User not found":
        # Unsuccessful login
        print(f"Login failed: {response}")
    elif response == username:
        # Successful login
        print(f"Login successful. Welcome, {username}!")
        cli()  # Start the CLI
    else:
        print("Server did not respond.")
        sys.exit(1)


@click.command()
@click.option('--login', is_flag=True, help='Login to the CLI')
@click.option('--register', is_flag=True, help='Register a new user')
def get_credentials(login, register):
    if login:
        print('Login')
        username = click.prompt('Enter your username', type=str)
        password = click.prompt('Enter your password', type=str, hide_input=True)
        login_user(username, password)
    elif register:
        print('Register')
        username = click.prompt('Choose a username', type=str)
        password = click.prompt('Choose a password', type=str, hide_input=True)
        full_name = click.prompt('Enter your full name', type=str)
        email = click.prompt('Enter your email', type=str)
        register_user(username, password, full_name, email)
    else:
        print('No option selected!')
        print('Please launch the CLI with either --login or --register')


if __name__ == "__main__":
    get_credentials()
