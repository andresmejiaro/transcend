# landing_page_handler.py

import asyncio

BASE_API_URL = "http://localhost:8001/api"

class LandingPageHandler:
    def __init__(self, api_client, websocket_manager, curses_ui):
        self.api_client = api_client
        self.websocket_manager = websocket_manager
        self.curses_ui = curses_ui

    def handle_landing_page(self):
        lobby_weboscket = self.connect_to_lobby_websocket()
        self.listen_for_notifications()

        return lobby_weboscket

    def connect_to_lobby_websocket(self):
        url = BASE_API_URL + "/lobby2/"
        query_params = {"client_id": self.api_client.client_id}

        websocket = self.websocket_manager.connect(url, query_params=query_params)

        return websocket


    def listen_for_notifications(self):
        asyncio.ensure_future(self._notification_listener())

    async def _notification_listener(self):
        while True:
            notification = await self.websocket_manager.receive_notification()
            # Process the notification
            # For example, update the UI with online users or display a notification
            online_users = ["User1", "User2", "User3"]  # Replace with actual online users
            self.curses_ui.update_online_users(online_users)

            self.curses_ui.display_notification(notification)

    def print_to_debug_file(self, message):
        with open("./debbug.txt", "a") as file:
            file.write(message + "\n")
