# app/views/base_view.py

from abc import ABC, abstractmethod

class BaseView(ABC):
    def __init__(self, stdscr):
        self.stdscr = stdscr

    @abstractmethod
    async def get_user_input(self):
        """Get user input for the view."""
        pass

    @abstractmethod
    async def process_inputs(self, user_input):
        """Process user input for the view."""
        pass

    @abstractmethod
    async def get_send_message_queue(self):
        """Get the send message queue for the view."""
        pass

    @abstractmethod
    async def process_lobby_recv_message(self, message):
        """Process a message received from the lobby."""
        pass

    @abstractmethod
    async def update_screen(self):
        """Update the screen based on the view's logic."""
        pass

    @abstractmethod
    async def get_next_view(self):
        """
        Check conditions and return the next view to switch to.
        Return None if no switch is needed.
        """
        pass

    @abstractmethod
    async def cleanup(self):
        """Cleanup the view."""
        pass
