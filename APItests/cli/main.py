# main.py

import json
import asyncio
import websockets
from http_api import http_api
from websocket_api import websocket_api
from views import View

# API callers for HTTP and Websocket
api_client = http_api()
websocket_manager = websocket_api()

# Global variables
# Keeps all the loops running until the user exits
keep_running = True

async def handle_lobby_websocket(websocket, online_users):
    global keep_running
    try:
        while keep_running:
            received_str = await websocket_manager.receive(websocket)
            try:
                received = json.loads(received_str)
                # Print the recieved message with proper indentation for Json readability
                # print(json.dumps(received, indent=4))
                type = received.get("type")

                if type == "user_joined":
                    online_users_data = received.get("data", {}).get("online_users", {})
                    for client_id, username in online_users_data.items():
                        online_users[client_id] = username

                elif type == "user_left":
                    client_id = received.get("data", {}).get("client_id")
                    online_users.pop(client_id, None)
                        

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")

    except websockets.exceptions.ConnectionClosedOK:
        print("Connection closed")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await websocket_manager.close(websocket)

async def main():
    try:
        global keep_running
        print("Welcome to the Pong Game!")
        print("Type 'login' or 'register' to start")
        input_str = input("Enter command: ")

        if input_str == "login":
            username = input("Enter your username: ")
            password = input("Enter your password: ")
            api_client.login(username, password)

        elif input_str == "register":
            username = input("Enter your username: ")
            password = input("Enter your password: ")
            fullname = input("Enter your fullname: ")
            email = input("Enter your email: ")
            api_client.register(username, password, fullname, email)

        lobby_websocket = await websocket_manager.connect("ws://localhost:8001/ws/lobby2/", {"client_id": api_client.client_id})
        online_users = {}
        asyncio.create_task(handle_lobby_websocket(lobby_websocket, online_users))

        views = View(api_client, websocket_manager, lobby_websocket)

        # views.home_page(online_users)

        while keep_running:
            if input_str == "exit":
                keep_running = False
            elif input_str == "home":
                views.home_page(online_users)
            elif input_str == "stats":
                views.see_my_stats()
            elif input_str == "friendlist":
                views.see_friend_list()
            elif input_str == "addfriend":
                views.add_friend()
            elif input_str == "removefriend":
                views.remove_friend()
            elif input_str == "playfriend":
                views.play_pong_with_friend()
            elif input_str == "playai":
                views.play_pong_against_ai()
            elif input_str == "online users":
                await websocket_manager.send(lobby_websocket, {"command": "list_of_users"})
            elif input_str == "invites":
                await websocket_manager.send(lobby_websocket, {"command": "list_received_invites"})

            # print(f'Online users: {online_users}')
            input_str = input("Enter command: ")

            await asyncio.sleep(1)

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("Ctrl+C pressed. Cleaning up...")
        keep_running = False

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass  # Suppress the second KeyboardInterrupt error during exit
    finally:
        print("Exiting...")
