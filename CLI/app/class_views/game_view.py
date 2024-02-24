# app/views/home_page.py

import curses
import logging
import json
import asyncio
import aiohttp

from utils.logger import log_message
from utils.url_macros import LOBBY_URI_TEMPLATE, PONG_URI_TEMPLATE
from utils.file_manager import FileManager
from utils.task_manager import TaskManager
from app.widgets.widgets import Widget
from app.widgets.nav_bar import NavBar

class GamePage(Widget):
    def __init__(self, stdscr, ui_controller, frame_rate, process_speed, task_manager, home_page, match_id):
        super().__init__(stdscr)
        self.file_manager = FileManager()
        self.task_manager = task_manager
        self.ui_controller = ui_controller
        
        self.home_page = home_page
        
        self.frame_rate = frame_rate
        
        self.process_speed = process_speed
        
        self.next_view = None
        
        self.connected_users = {}
        
        self.nav_bar_items = ["Home", "Exit"]
        self.nav_bar = NavBar(stdscr, self.nav_bar_items)
        
        self.token = None
        self.game_state = None
        self.match_id = match_id
            
    def __str__(self):
        # Return a string representing the current view
        return "game"
    
    async def draw(self):
        try:
            self.frame_rate[0] = 1
            
            self._clear_screen()
            
            self.current_fram = self.ui_controller.get_message_from_websocket(f'{self.match_id}')
            
            self.update_terminal_size()
            
            if self.rows < 30 or self.cols < 120:
                self.print_screen_too_small()
                return
            
            # self.print_current_time()
            self.print_frame_rate()
            self.print_header("Game")

            
            self._refresh_screen()
            
        except Exception as e:
            log_message(f"Error displaying splash screen: {e}", level=logging.ERROR)
            self.next_view = self
            
    # Input Processing Handler
    async def process_input(self):
        try:
            self.process_speed[0] = 100

            user_input = await self.ui_controller.check_and_process_inputs_filterd([f'{self.match_id}', "keyboard", "lobby"])

            if user_input:
                task_name = user_input.get("task_name")
                input_data = user_input.get("data")

                if task_name == "lobby":
                    self.process_lobby_input(input_data)
                    pass
                elif task_name == "keyboard":
                    self.process_keyboard_input(input_data)
                    pass
                elif task_name == f'{self.match_id}':
                    self.process_game_input(input_data)
                    pass
                    
        except Exception as e:
            log_message(f"Error processing input: {e}", level=logging.ERROR)
             
    def get_next_view(self):
        return self.next_view
    
    def cleanup(self):
        pass
    

            

     