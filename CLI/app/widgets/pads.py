# app/widgets/pads.py

import curses
import logging

from utils.logger import log_message

class Pad:
    def __init__(self, height, width):
        self.pad = curses.newpad(height, width)

    def refresh(self, pminrow, pmincol, sminrow, smincol, smaxrow, smaxcol):
        self.pad.refresh(pminrow, pmincol, sminrow, smincol, smaxrow, smaxcol)

    def addstr(self, row, col, text, attr=0):
        try:
            self.pad.addstr(row, col, text, attr)
        except curses.error as e:
            log_message(f"Error adding string at ({row}, {col}): {e}")