# app/views/base_view.py

from abc import ABC, abstractmethod

class BaseView(ABC):
    def __init__(self, stdscr):
        self.stdscr = stdscr

    @abstractmethod
    def update_screen(self):
        """Update the screen based on the view's logic."""
        pass

    @abstractmethod
    def process_input(self):
        """Process user input for the view."""
        pass

    @abstractmethod
    def get_next_view(self):
        """
        Check conditions and return the next view to switch to.
        Return None if no switch is needed.
        """
        pass

    async def run_async(self):
        """
        An optional asynchronous entry point for views.
        Implement this method if a view needs to perform async operations.
        """
        pass
