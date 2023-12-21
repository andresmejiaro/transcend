# cli.py

import asyncio
import websockets
import json
import requests
import time
import click
import os
from APIclient import APIClient
from pong import PongGameClient
import signal

# Global variable to track KeyboardInterrupt
interrupted = False



API_BASE_URL = "http://localhost:8000/api"
TOKEN_FILE = "token.txt"
CLIENT_INFO_FILE = "client_info.txt"
COOKIES_FILE = "cookies.txt"
api_client = APIClient()

def handle_interrupt(signum, frame):
    global interrupted
    print("\nCtrl+C detected. Cleaning up and exiting.")
    interrupted = True

# Register the signal handler
signal.signal(signal.SIGINT, handle_interrupt)

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

def save_client_info(client_id, username):
    info = {"client_id": client_id, "username": username}
    with open(CLIENT_INFO_FILE, "w") as file:
        json.dump(info, file)

def load_client_info():
    try:
        with open(CLIENT_INFO_FILE, "r") as file:
            content = file.read()
            if content:
                return json.loads(content)
            else:
                return None
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON in client_info.txt. File may be empty or corrupted.")
        return None

def save_cookies(cookie):
    with open(COOKIES_FILE, "w") as file:
        file.write(cookie)

def load_cookies():
    try:
        with open(COOKIES_FILE, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("Cookies file not found.")
    except json.JSONDecodeError:
        print("Error decoding JSON in cookies.txt. File may be empty or corrupted.")
        return None

def save_token(token):
    with open(TOKEN_FILE, "a") as file:
        file.write(token + "\n")

def load_token():
    try:
        with open(TOKEN_FILE, "r") as file:
            # Read all lines and return as a list
            return file.read().strip().splitlines()
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print("Error decoding JSON in token.txt. File may be empty or corrupted.")
        return []

def authenticate(username, password, session):
    login_url = f"{API_BASE_URL}/user/login/"
    data = {"username": username, "password": password}

    response = session.post(login_url, json=data)

    if response.status_code == 200:
        json_response = response.json()
        if json_response['status'] == 'ok':
            print(f"Login successful. Welcome, {username}!")

            cookie = response.headers.get('Set-Cookie')
            jwt_token = json_response.get("token")

            if cookie and jwt_token:
                # Clear existing tokens and save the new one
                with open(TOKEN_FILE, "w"):
                    pass
                save_cookies(cookie.split(';')[0].split('=')[1])
                save_token(jwt_token)

            return response
    else:
        return None

def get_token_expiration(response):
    if response.status_code == 200:
        json_response = response.json()
        expiration_timestamp = json_response.get('exp')
        if expiration_timestamp:
            return int(expiration_timestamp)
    return None

def signup(username, password, fullname, email):
    signup_url = f"{API_BASE_URL}/user/signup/"
    data = {"username": username, "password": password, "fullname": fullname, "email": email}

    response = requests.post(signup_url, json=data)

    if response.status_code == 200:
        json_response = response.json()
        if json_response['status'] == 'ok':
            print(f"Signup successful. Welcome, {username}!")
            return json_response["token"]
    else:
        return None


async def main():
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    client_id = None

    global interrupted

    api_client.session = requests.Session()

    # Authenticate the user
    response = authenticate(username, password, api_client.session)
    print(response.json())

    if response is None:
        print("Authentication failed. Signing up...")
        fullname = input("Enter your full name: ")
        email = input("Enter your email address: ")

        # Sign up the user
        token = signup(username, password, fullname, email)
        if token:
            # Save client_id and username to a file
            client_id = api_client.get_client_id(username)
            save_client_info(client_id, username)
            save_token(token)
        else:
            print("Signup failed. Exiting.")
            return

    client_info = load_client_info()
    if client_info is None:
        client_id = api_client.get_client_id(username)
        save_client_info(client_id, username)

    client_id = client_info["client_id"]

    websocket_uri = f"ws://localhost:8001/ws/lobby2/?client_id={client_id}"
    print(f'Connecting to {websocket_uri}...')

    # Create an asyncio Queue to communicate between tasks
    message_queue = asyncio.Queue()

    pong_client = PongGameClient(websocket_uri_base="ws://localhost:8001/ws/pong")

    try:
        async with websockets.connect(websocket_uri) as websocket:
            gather_task = asyncio.gather(
                handle_websocket_messages(websocket, message_queue),
                handle_user_input(websocket, message_queue, pong_client)
            )

            while not interrupted:
                # Periodically check for KeyboardInterrupt
                await asyncio.sleep(1)

            await gather_task


    except Exception as e:
        print(f"Error in main: {e}")

    finally:
        # Explicitly cancel the tasks
        gather_task.cancel()

        try:
            # Wait for all tasks to be canceled
            await asyncio.gather(gather_task, return_exceptions=True)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Error during cleanup: {e}")

        await pong_client.disconnect()

        print("Exiting..")
        exit(0)


if __name__ == "__main__":
    asyncio.run(main())