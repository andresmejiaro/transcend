# app/widgets/widgets.py

import curses
import time
import logging

from utils.logger import log_message
from utils.file_manager import FileManager

class Widget:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.file_manager = FileManager()
        self.last_frame_time = time.time()
        self.update_terminal_size()
        self.color_counter = 1

    def update_terminal_size(self):
        try:
            self.rows, self.cols = self.stdscr.getmaxyx()
            
        except Exception as e:
            log_message(f"Error getting terminal size: {e}", level=logging.ERROR)

    def _clear_screen(self):
        self.stdscr.clear()

    def _refresh_screen(self):
        self.stdscr.refresh()

    def _addstr(self, row, col, text, attr=0):
        try:
            self.stdscr.addstr(row, col, text, attr)
            
        except curses.error as e:
            log_message(f"Error adding string at ({row}, {col}): {e}", level=logging.ERROR)

    def print_logo_centered(self, logo):
        logo_height = len(logo)
        logo_width = len(logo[0])

        row = self.rows // 2 - logo_height // 2
        col = self.cols // 2 - logo_width // 2

        for frame_line in logo:
            self._addstr(row, col, frame_line, curses.color_pair(self.color_counter))
            row += 1

        # Increment the color counter for the next call
        self.color_counter = (self.color_counter % 6) + 1

    def print_screen_too_small(self, size_required=(30, 120)):
        self._clear_screen()
        self._addstr(0, 0, f"Screen too small! Please resize to at least {size_required[0]} rows and {size_required[1]} columns.", curses.color_pair(3) | curses.A_BLINK)
        self._refresh_screen()

    def print_header(self, header):
        col = self.cols // 2 - len(header) // 2
        self._addstr(1, col, header)

    def print_animated_logo(self, logo, frame_rate):
        logo_height = len(logo)
        logo_width = len(logo[0])

        row = self.rows // 2 - logo_height // 2
        col = self.cols // 2 - logo_width // 2

        for frame_line in logo:
            self._addstr(row, col, frame_line)
            row += 1

        time.sleep(1 / frame_rate)

    def print_message_bottom(self, message):
        # Print message 1 row above the bottom of the screen
        row = self.rows - 2
        col = self.cols // 2 - len(message) // 2
        self._addstr(row, col, message, curses.color_pair(6) | curses.A_BOLD)

    def print_frame_rate(self):
        try:
            current_time = time.time()
            frame_rate = 1 / (current_time - self.last_frame_time)
            self.last_frame_time = current_time

            self._addstr(1, self.cols - 21, f"Frame Rate: {frame_rate:.2f} FPS", curses.color_pair(3) | curses.A_DIM | curses.A_BOLD)

        except Exception as e:
            log_message(f"Error printing frame rate: {e}", level=logging.ERROR)

    def print_current_time(self):
        try:
            current_time = time.strftime("%H:%M:%S")
            self._addstr(0, self.cols - 22, f"Current Time: {current_time}", curses.color_pair(3) | curses.A_DIM | curses.A_BOLD)

        except Exception as e:
            log_message(f"Error printing current time: {e}", level=logging.ERROR)



    async def print_input_box(self, prompt, input_text, location="bottom"):
        try:
            # We will get inputs from the keyboard directly and print them on screen storing it in input_text
            # We will also print the prompt on the screen at the required location
            self.stdscr.nodelay(False)
            while True:
                # Clear the screen
                self._clear_screen()
                self.update_terminal_size()
                if self.rows < 3 or self.cols < 50:
                    self.print_screen_too_small(size_required=(3, 50))
                    continue

                # Print the prompt with resizing
                if location == "bottom":
                    row = self.rows - 1
                    self._addstr(row, 0, prompt, curses.color_pair(6) | curses.A_DIM | curses.A_BOLD)
                    self._addstr(row, len(prompt), input_text, curses.color_pair(6) | curses.A_BOLD)
                elif location == "top":
                    row = 0
                    self._addstr(row, 0, prompt, curses.color_pair(6) | curses.A_DIM | curses.A_BOLD)
                    self._addstr(row, len(prompt), input_text, curses.color_pair(6) | curses.A_BOLD)
                elif location == "center":
                    row = self.rows // 2
                    self._addstr(row, 0, prompt, curses.color_pair(6) | curses.A_DIM | curses.A_BOLD)
                    self._addstr(row, len(prompt), input_text, curses.color_pair(6) | curses.A_BOLD)
                else:
                    raise ValueError(f"Invalid location: {location}")

                # Refresh the screen
                self._refresh_screen()

                # Get input from the keyboard
                key = self.stdscr.getch()
                if len(input_text) > 100:
                    input_text = input_text[:-1]

                # If the user presses enter, return the input text
                if key == curses.KEY_ENTER or key in [10, 13]:
                    if input_text == "":
                        continue
                    if input_text == "help":
                        input_text = ""
                        # self.display_help()
                        continue
                    
                    self.stdscr.nodelay(True)
                    return input_text

                # If the user presses backspace, remove the last character from input_text
                elif key == curses.KEY_BACKSPACE or key == 127:
                    input_text = input_text[:-1]

                # If the user presses escape, return None
                elif key == 27:
                    return None
                
                # If the user presses any printable character, add it to input_text
                elif key >= 32 and key <= 126:
                    input_text += chr(key)
                    
                # If the user presses any other key, continue
                else:
                    continue
            
        except Exception as e:
            log_message(f"Error printing input box: {e}", level=logging.ERROR)
            self.stdscr.nodelay(True)
        
        
        
        # row = self.rows - 1
        # self._addstr(row, 0, prompt, curses.color_pair(6) | curses.A_DIM | curses.A_BOLD)
        # col = 0 + len(prompt)
        # self._addstr(row, col, input_text, curses.color_pair(6) | curses.A_DIM | curses.A_BOLD | curses.A_BLINK)



    def scaler(self, prior, priorMax, posMax):
        return int(posMax * prior / priorMax)

    def rectdrawer(self, dictCanvas: dict, obj:str, stdscr, 
                enclousure = {"xl" : 0,"xh": 858,"yl": 0,"yh": 525}):
        height,width = stdscr.getmaxyx()
        startY = self.scaler(dictCanvas[obj]["position"]["y"],enclousure["yh"],height)
        endY = self.scaler(dictCanvas[obj]["position"]["y"] + dictCanvas[obj]["size"]["y"],enclousure["yh"],height)
        startX = self.scaler(dictCanvas[obj]["position"]["x"],enclousure["xh"],width)
        endX = self.scaler(dictCanvas[obj]["position"]["x"] + dictCanvas[obj]["size"]["x"],enclousure["xh"],width)
        for i in range(round(startY), round(endY)):
            for j in range(round(startX), round(endX)):
                stdscr.addstr(i, j, "x")

    def print_score(self, left_score, right_score):
        score = f"{left_score} - {right_score}"
        row = self.rows - 1
        col = self.cols // 2 - len(score) // 2
        self._addstr(row, col, score, curses.color_pair(6) | curses.A_BOLD)
        
    def print_usernames(self, left_username, right_username):
        # We'll print the score at the bottom center of the screen
        usernames = f"{left_username} - {right_username}"
        row = self.rows - 2
        col = self.cols // 2 - len(usernames) // 2
        self._addstr(row, col, usernames, curses.color_pair(6) | curses.A_BOLD)