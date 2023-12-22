# cli.py

import asyncio
import websockets
import json
import requests
import time
import click
import os
from http_api import http_api
import signal

api_client = http_api()


async def handle_websocket_messages(websocket, message_queue):
    try:
        while websocket.open:
            message = await websocket.recv()
            print(f"Received WebSocket message: {message}")

            try:
                data = json.loads(message)

                message_type = data.get("type")

                if message_type == "user_joined":
                    user_data = data.get("data", {}).get("online_users", {})
                    for user_id, username in user_data.items():
                        print(f"User {username} (ID: {user_id}) joined the lobby")

                await message_queue.put(data)
            except json.JSONDecodeError:
                print(f"Received non-JSON message: {message}")

    except websockets.exceptions.ConnectionClosed as e:
        print(f"WebSocket connection closed: {e}")
    except Exception as ex:
        print(f"Error in handle_websocket_messages: {ex}")

async def handle_user_input(lobby_websocket, message_queue, pong_client):
    while True:
        try:
            # Use asyncio.to_thread() to run input() in a separate thread
            user_input = await asyncio.to_thread(input, "Enter a command: ")

            if user_input == "play_pong":
                match_id = await asyncio.to_thread(input, "Enter the match ID you want to join or create: ")
                asyncio.create_task(pong_client.play_pong(match_id))
            elif user_input == "exit":
                print("Exiting...")
                # Close the WebSocket connection
                await lobby_websocket.close()
                break

            await lobby_websocket.send(user_input)

        except Exception as e:
            print(f"Error in handle_user_input: {e}")


async def main():
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    # Create a new user
    api_client.login(username, password)
    matches = api_client.make_api_call("GET", "/match/")
    print(matches.json().get("data", {}))








if __name__ == "__main__":
    asyncio.run(main())