# cli.py

import asyncio
import websockets
import json
import requests
import time
import click
from APIclient import APIClient

API_BASE_URL = "http://localhost:8000/api"
TOKEN_FILE = "token.txt"
CLIENT_INFO_FILE = "client_info.txt"
COOKIES_FILE = "cookies.txt"
api_client = APIClient()


async def handle_websocket_messages(websocket_uri, message_queue):
    async with websockets.connect(websocket_uri) as websocket:
        while True:
            message = await websocket.recv()
            print(f"Received WebSocket message: {message}")
            await message_queue.put(message)


async def handle_user_input(websocket, message_queue):
    while True:
        user_input = input("Type a message to send: ")
        await websocket.send(user_input)

        if user_input.lower() == "exit":
            break


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
    with open(TOKEN_FILE, "w") as file:
        file.write(token)


def load_token():
    try:
        with open(TOKEN_FILE, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON in token.txt. File may be empty or corrupted.")
        return None


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
                save_cookies(cookie.split(';')[0].split('=')[1])
                save_token(jwt_token)

            return response
    else:
        return None


def get_token_expiration(response):
    if response.status_code == 200:
        json_response = response.json()
        expiration_timestamp = json_response.get('expires_at')
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

    token_expiration = get_token_expiration(response)
    if token_expiration and token_expiration < time.time():
        print("Token has expired. Refreshing...")
        response = authenticate(username, password, api_client.session)
        if response is None:
            print("Token refresh failed. Exiting.")
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

    try:
        async with websockets.connect(websocket_uri) as websocket:
            # Start tasks concurrently
            tasks = [
                handle_websocket_messages(websocket_uri, message_queue),
                handle_user_input(websocket, message_queue)
            ]

            await asyncio.gather(*tasks)
    except websockets.WebSocketException as e:
        print(f"WebSocket connection error: {e}")
    except KeyboardInterrupt:
        print("WebSocket connection closed.")


if __name__ == "__main__":
    asyncio.run(main())