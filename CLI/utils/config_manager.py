# utils/config_manager.py

import os
import json
import curses
import logging

from utils.logger import log_message

class ConfigurationManager:
    def __init__(self):
        self.config_path = 'config.json'
        self.config_data = self.retrieve_configuration()
        self.stdscr = None

    def __str__(self):
        return "config_manager"

    def load_configuration_file(self, stdscr):
        # Check if the configuration file already exists
        self.stdscr = stdscr

        if os.path.exists(self.config_path):
            # Create directories
            try:
                self.check_and_create_directories()
                self.initialize_logger()
                self.initialize_curses_settings(self.stdscr)
                
            except KeyError:
                print('Error: Configuration data not found.')
                return None      
            except Exception as e:
                print(f'Error in Load Configuration: {e}')
                return None

# Configuration Mehots   
    def check_and_create_directories(self):
        # Check if the configuration file already exists
        if os.path.exists(self.config_path):
            # Create directories
            try:
                base_directory = os.getcwd()
                data_directory = os.path.join(base_directory, self.config_data['data']['data_directory'])
                log_directory = os.path.join(base_directory, self.config_data['logging']['log_directory'])
                db_directory = os.path.join(base_directory, self.config_data['database']['database_directory'])

                os.makedirs(data_directory, exist_ok=True)
                os.makedirs(log_directory, exist_ok=True)
                os.makedirs(db_directory, exist_ok=True)

            except KeyError:
                print('Error: Configuration data not found.')
                return None
            except Exception as e:
                print(f'Error in Load Configuration: {e}')
                return None

    def initialize_logger(self):
        try:
            log_file_path = os.path.join(self.config_data['logging']['log_directory'], 'app.log')
            log_format = self.config_data['logging']['log_format']
            log_level = self.config_data['logging']['log_level']
            log_date_format = self.config_data['logging']['log_date_format']
            
            if log_level == 'DEBUG':
                level = logging.DEBUG
            elif log_level == 'INFO':
                level = logging.INFO
            elif log_level == 'WARNING':
                level = logging.WARNING
            elif log_level == 'ERROR':
                level = logging.ERROR
            elif log_level == 'CRITICAL':
                level = logging.CRITICAL
            else:
                level = logging.NOTSET

            logging.basicConfig(
                filename=log_file_path,
                level=level,
                format=log_format,
                datefmt=log_date_format
            )

            log_message('Logger initialized Sucessfully!', level=logging.INFO)

        except KeyError:
            log_message('Error: Configuration data not found.', level=logging.ERROR)
            return None
        
    def initialize_curses_settings(self, stdscr):
        try:
            curses_settings = self.config_data['curses_settings']

            if curses_settings['sound_enabled']:
                curses.beep()
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

        except KeyError:
            log_message('Error: Configuration data not found.', level=logging.ERROR)
            return None

        except Exception as e:
            log_message(f'Error in Load Configuration: {e}', level=logging.ERROR)
            return None

    def reset_curses_settings(self, stdscr):
        try:
            # Reset the cursor
            curses.curs_set(1)
            # React to keys instantly without requiring Enter to be pressed
            curses.nocbreak()
            # Make getch() non-blocking
            stdscr.nodelay(False)
            # Echo keyboard input
            curses.echo()
            # Disable keypad mode
            stdscr.keypad(False)
            # Disable color
            curses.start_color()
            # Reset end the window
            curses.endwin()

        except Exception as e:
            log_message(f'Error in Load Configuration: {e}', level=logging.ERROR)
            return None

# Utilities
    def retrieve_configuration(self):
        try:
            with open(self.config_path, 'r') as config_file:
                print(f'Loading configuration from {self.config_path}')
                config_data = json.load(config_file)
                return config_data
            
        except FileNotFoundError:
            print(f'Config file ({self.config_path}) not found.')
            return None
        except json.JSONDecodeError:
            print(f'Error decoding JSON in config file ({self.config_path}).')
            return None
        except Exception as e:
            print(f'Error in retrieve_configuration: {e}')
            return None
        
    def cleanup(self):
        # Delete data files for the current session
        try:
            data_directory = self.config_data['data']['data_directory']
            for file in os.listdir(data_directory):
                file_path = os.path.join(data_directory, file)
                os.remove(file_path)

            self.reset_curses_settings(self.stdscr)

        except KeyError:
            log_message('Error: Configuration data not found.', level=logging.ERROR)
            return None
        except Exception as e:
            log_message(f'Error in Load Configuration: {e}', level=logging.ERROR)
            return None
