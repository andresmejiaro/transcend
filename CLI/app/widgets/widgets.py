import urwid
import time
from utils.logger import log_message
import logging

class Widget:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.last_frame_time = time.time()
        self.update_terminal_size()

        # Create a pile to hold widgets
        self.top = urwid.Pile([])

    def update_terminal_size(self):
        try:
            self.rows, self.cols = self.stdscr.getmaxyx()
        except Exception as e:
            log_message(f"Error getting terminal size: {e}", level=logging.ERROR)

    def draw_screen(self):
        urwid.MainLoop(self.top).run()

    def _add_widget(self, widget):
        self.top.contents.append((widget, self.top.options()))

    def _clear_widgets(self):
        self.top.contents = []

    def print_screen_too_small(self, size_required=(30, 80)):
        text = f"Screen too small! Please resize to at least {size_required[0]} rows and {size_required[1]} columns."
        widget = urwid.Text(text, align='center')
        self._clear_widgets()
        self._add_widget(widget)
        self.draw_screen()

    def print_header(self, header):
        widget = urwid.Text(header, align='center')
        self._clear_widgets()
        self._add_widget(widget)
        self.draw_screen()

    def print_animated_logo(self, logo, frame_rate):
        text = "\n".join(logo)
        widget = urwid.Text(text, align='center')
        self._clear_widgets()
        self._add_widget(widget)
        self.draw_screen()
        time.sleep(1 / frame_rate)

    def print_message_bottom(self, message):
        widget = urwid.Text(message, align='center')
        self._clear_widgets()
        self._add_widget(widget)
        self.draw_screen()

    def print_frame_rate(self):
        try:
            current_time = time.time()
            frame_rate = 1 / (current_time - self.last_frame_time)
            self.last_frame_time = current_time

            text = f"Frame Rate: {frame_rate:.2f} FPS"
            widget = urwid.Text(text, align='right')
            self._clear_widgets()
            self._add_widget(widget)
            self.draw_screen()

        except Exception as e:
            log_message(f"Error printing frame rate: {e}", level=logging.ERROR)

    def print_current_time(self):
        current_time = time.strftime("%H:%M:%S")
        text = f"Current Time: {current_time}"
        widget = urwid.Text(text, align='right')
        self._clear_widgets()
        self._add_widget(widget)
        self.draw_screen()
