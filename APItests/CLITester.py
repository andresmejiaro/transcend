import aiohttp
import asyncio
import json
import websockets
import requests
import traceback
import re

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

        json_data = json.dumps(data) if data else None
            
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

    async def connect(self):
        await self.fetch_csrf_token()  # Fetch CSRF token before connecting
        headers = {"csrf": self.csrf_token} if self.csrf_token else {}
        self.websocket = await websockets.connect(self.ws_url, extra_headers=headers)

    async def send_message(self, command, data):
        message = {"command": command, "data": data}
        await self.websocket.send(json.dumps(message))

    async def close(self):
        if self.websocket:
            await self.websocket.close()

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

            print(f"Response headers: {response.headers}")

            # Extract and save the CSRF token from the Set-Cookie header
            csrf_cookie = response.headers.get('Set-Cookie')
            if csrf_cookie:
                csrf_token = csrf_cookie.split(';')[0].split('=')[1]
                if csrf_token:
                    self.csrf_token['csrftoken'] = csrf_token

            jwt_token = response.json().get("token")
            if jwt_token:
                return jwt_token
            else:
                return False

        except Exception as e:
            print(f"Failed to signup user. Exception: {e}")
            traceback.print_exc()
            return e
        
    def make_api_call(self, endpoint, method="GET", data=None):
        return self.websocket_handler.make_api_call(endpoint, method, data)

    async def connect(self):
        await self.websocket_handler.connect()

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
                        break
                else:
                    # Create a match
                    match_data = {'player1': f'{self.client_id}'}
                    match_response = self.make_api_call("match/create/", "POST", data=match_data)
                    match_json = json.loads(match_response)
                    match_id = match_json.get("match_id")

            print(f"Match ID: {match_id}")
            # Get the object and see if we have enough players
            match_response = self.make_api_call(f"match/{match_id}/", "GET")
            print(f"You will be playing in this match: {match_response}")

        except Exception as e:
            print(f"Error during play: {e}")

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
