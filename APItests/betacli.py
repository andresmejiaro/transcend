import aiohttp
import asyncio
import json
import websockets
import requests
import traceback
import re
import curses
import asyncio

BASE_URL = "http://localhost:8000/api/"
WS_URL = "ws://localhost:8001/ws/"

class WebSocketHandler:
    def __init__(self, ws_url, jwt_token, cookies, username):
        self.ws_url = ws_url
        self.jwt_token = jwt_token
        self.username = username
        self.websocket = None
        self.csrf_token = cookies

    def make_api_call(self, endpoint, method="GET", data=None):

        url = BASE_URL + endpoint

        print(f"Making API call to {url}")

        headers = {}
        if self.jwt_token:
            headers = {
                "Content-Type": "application/json",
                "X-CSRFToken": self.csrf_token['csrftoken'],
                "Authorization": f"Bearer {self.jwt_token}",
            }

        if data and isinstance(data, dict):
            json_data = json.dumps(data)
        else:
            json_data = data
            
        print (f"Headers: {headers}")
        print (f"Data: {data}")
        print (f'Cookies {self.csrf_token}')

        if method == "GET":
            response = requests.get(url, headers=headers, data=json_data, cookies=self.csrf_token)
        elif method == "POST":
            response = requests.post(url, headers=headers, data=json_data, cookies=self.csrf_token)
        elif method == "PUT":
            response = requests.put(url, headers=headers, data=json_data, cookies=self.csrf_token)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, data=json_data, cookies=self.csrf_token)
        else:
            print(f"Unsupported HTTP method: {method}")
            return False
        
        print(f"Response: {response}")
        
        response_json = response.json()
        print(f"Response JSON: {response_json}")
        return response_json    

    async def ws_connect(self, endpoint, query_params=None):
        url = self.ws_url + endpoint
        if query_params:
            url += "?" + query_params

        print(f"Connecting to websocket at {url}")
        self.websocket = await websockets.connect(url)
        print(f"Connected to websocket at {url}")

        if self.websocket:
            asyncio.get_event_loop().create_task(self.recieve())

    async def send_message(self, command, data):
        payload = {
            "command": command,
            "data": data,
        }
        await self.websocket.send(json.dumps(payload))

    async def close(self):
        await self.websocket.close()

    async def recieve(self):
        message = await self.websocket.recv()

        type = message.get("type")
        data = message.get("data")

        if type == "player_list":
            print(f"Player list: {data}")
        elif type == "update_buffer":
            self.draw(data)

    def draw(self, data):
        self.screen.clear()

        ball = data.get("ball")
        left_paddle = data.get("leftPaddle")
        right_paddle = data.get("rightPaddle")
        score_update = data.get("score_update")

        # Draw ball
        ball_x, ball_y = int(ball["position"]["x"]), int(ball["position"]["y"])
        self.screen.addch(ball_y, ball_x, 'o')

        # Draw left paddle
        left_paddle_x, left_paddle_y = int(left_paddle["position"]["x"]), int(left_paddle["position"]["y"])
        for i in range(left_paddle_y, left_paddle_y + int(left_paddle["size"]["y"])):
            self.screen.addch(i, left_paddle_x, '|')

        # Draw right paddle
        right_paddle_x, right_paddle_y = int(right_paddle["position"]["x"]), int(right_paddle["position"]["y"])
        for i in range(right_paddle_y, right_paddle_y + int(right_paddle["size"]["y"])):
            self.screen.addch(i, right_paddle_x, '|')

        self.screen.refresh()


class PongClient:
    def __init__(self, username, password, fullname, email):
        self.username = username
        self.password = password
        self.email = email
        self.csrf_token = {}
        self.jwt_token = self.signup_user(username, password, fullname, email)
  
        if not self.jwt_token:
            print("Failed to signup user")
            return None

        self.websocket_handler = WebSocketHandler(WS_URL, jwt_token=self.jwt_token, cookies=self.csrf_token, username=username)
        self.client_id = None

    def signup_user(self, username, password, fullname, email, cookie=None):
        try:
            signup_url = BASE_URL + "user/signup/"
            headers = {
                "Content-Type": "application/json",
            }
            payload = {
                "username": username,
                "password": password,
                "email": email,
                "fullname": fullname,
                "is_superuser": False,
            }

            response = requests.post(signup_url, json=payload, headers=headers)

            # Extract and save the CSRF token from the Set-Cookie header
            csrf_cookie = response.headers.get('Set-Cookie')
            if csrf_cookie:
                csrf_token = csrf_cookie.split(';')[0].split('=')[1]
                if csrf_token:
                    self.csrf_token['csrftoken'] = csrf_token

            jwt_token = response.json().get("token")
            if jwt_token:
                print(f"Successfully signed up user {username}")
                return jwt_token
            else:
                return False

        except Exception as e:
            print(f"Failed to signup user. Exception: {e}")
            traceback.print_exc()
            return e
        
    def make_api_call(self, endpoint, method="GET", data=None):
        return self.websocket_handler.make_api_call(endpoint, method, data)

    async def connect(self, endpoint, query_params=None):
        await self.websocket_handler.ws_connect(endpoint, query_params)

    async def send_message(self, command, data):
        await self.websocket_handler.send_message(command, data)

    async def close(self):
        await self.websocket_handler.close()
   
    async def play(self):
        try:
            # Get the user ID
            response = self.make_api_call(f'get_user_id/{self.username}/', "GET")
            self.client_id = response.get("user_id")

            # Check if there is an existing match missing player 2 so we can join it
            list_of_matches = self.make_api_call("match/", "GET")

            if list_of_matches and 'data' in list_of_matches:
                matches_data = list_of_matches['data']
                for match in matches_data:
                    if match.get("player2") is None:
                        match_id = match.get("id")
                        match_data = {'player2': f'{self.client_id}'}
                        match_response = self.make_api_call(f"match/{match_id}/", "PUT", data=match_data)
                        break
                else:
                    # Create a match
                    match_data = {'player1': f'{self.client_id}'}
                    match_response = self.make_api_call("match/create/", "POST", data=match_data)
                    match_id = match_response.get("match_id")

            print(f"Match ID: {match_id}")
            # Get the object and see if we have enough players
            match_response = self.make_api_call(f"match/{match_id}/", "GET")
            print(f"You will be playing in this match: {match_response}")
            # Get the player IDs
            match = match_response.get("data")
            player_1_id = match.get("player1")
            player_2_id = match.get("player2")

            # Join the match
            print(f"Joining match {match_id}")
            await self.connect(f'pong/{match_id}/', query_params=f"client_id={self.client_id}&player_1_id={player_1_id}&player_2_id={player_2_id}")

            await self.game()

        except Exception as e:
            print(f"Error during play: {e}")

    async def game(self):
        try:
            while True:
                command = input("Enter a command: ")

                if command == "move_up":
                    await self.send_message("up", {})
                elif command == "move_down":
                    await self.send_message("down", {})
                elif command == "quit":
                    break
                else:
                    print("Invalid command. Please try again.")

        except KeyboardInterrupt:
            print("Exiting.")
            await self.close()

        except Exception as e:
            print(f"Failed to run client. Exception: {e}")
            traceback.print_exc()
            await self.close()

    async def listen(self):
        try:
            while True:
                command = input("Enter a command: ")

                if command == "play":
                    await self.play()
                elif command == "quit":
                    break
                else:
                    print("Invalid command. Please try again.")

        except KeyboardInterrupt:
            print("Exiting.")
            await self.close()

        except Exception as e:
            print(f"Failed to run client. Exception: {e}")
            traceback.print_exc()
            await self.close()


if __name__ == "__main__":
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    email = input("Enter your email: ")
    fullname = input("Enter your fullname: ")

    client = PongClient(username, password, fullname, email)

    if not client:
        print("Failed to initialize client")
        exit(1)

    try:
        asyncio.get_event_loop().run_until_complete(client.listen())

    except KeyboardInterrupt:
        print("Exiting.")
        exit(0)

    except Exception as e:
        print(f"Failed to run client. Exception: {e}")
        exit(1)

    finally:
        if client.websocket_handler:
            asyncio.get_event_loop().run_until_complete(client.websocket_handler.close())

        exit(0)
