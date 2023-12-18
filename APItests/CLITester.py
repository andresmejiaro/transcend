import aiohttp
import asyncio
import json
import websockets
import requests
import traceback

BASE_URL = "http://localhost:8000/api/"
WS_URL = "ws://localhost:8001/ws/"


class WebSocketHandler:
    def __init__(self, ws_url, jwt_token, username):
        self.ws_url = ws_url
        self.jwt_token = jwt_token
        self.username = username
        self.websocket = None
        self.csrf_token = None

    async def make_api_call(self, endpoint, method="GET", data=None):
        url = BASE_URL + endpoint
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.jwt_token}",
        }

        if self.csrf_token:
            headers["X-CSRFToken"] = self.csrf_token

        try:
            async with aiohttp.ClientSession() as session:
                if data:
                    data_str = json.dumps(data)  # Convert data to JSON string
                else:
                    data_str = None

                print(f"Making {method} request to {url} with data: {data_str} and headers: {headers}")

                if method == "GET":
                    response = await session.get(url, headers=headers, data=data_str)
                elif method == "POST":
                    response = await session.post(url, headers=headers, data=data_str)
                elif method == "PUT":
                    response = await session.put(url, headers=headers, data=data_str)
                elif method == "DELETE":
                    response = await session.delete(url, headers=headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                return response

        except Exception as e:
            print(f"Error making API call: {e}")
            return None

    async def fetch_csrf_token(self):
        csrf_url = BASE_URL + "get_csrf_token/"
        response = await self.make_api_call(csrf_url)
        if response and response.status == 200:
            data = await response.json()
            csrf_token = data.get("csrf_token")
            return csrf_token
        else:
            print("Failed to fetch CSRF token.")
            return None

    async def connect(self):
        self.csrf_token = await self.fetch_csrf_token()
        headers = {"X-CSRFToken": self.csrf_token} if self.csrf_token else {}
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
        self.jwt_token = self.signup_user(username, password, fullname, email)
        self.websocket_handler = WebSocketHandler(WS_URL, self.jwt_token, username)
        self.client_id = None

        if not self.jwt_token:
            print("Failed to initialize client")
            exit(1)

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

            jwt_token = response.json().get("token")
            if jwt_token:
                print(f"Successfully signed up user {username}")
                return jwt_token
            else:
                print(f"Failed to signup user. Status code: {response.status_code}")
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
            response = await self.make_api_call(f"get_user_id/{self.username}", "GET")

            if response.status == 200:
                user_data = await response.json()
                self.client_id = user_data.get("user_id")
                print(f"Client ID: {self.client_id}")

                match_data = {
                    "player1": self.client_id,
                    "player2": None,
                    "player1_score": 0,
                    "player2_score": 0,
                    "winner": None,
                    "date_played": None,
                    "active": True,
                }

                print(f"Creating match with data: {match_data}")

                match_response = await self.make_api_call(
                    "match/create/" + "?username=" + self.username, "POST", data=match_data
                )

                if match_response and match_response.status == 200:
                    match = await match_response.json()
                    if "error" in match:
                        print(f"Error creating match: {match['error']}")
                    else:
                        print(f"Created match: {match}")
                else:
                    print("Failed to create match")

            else:
                print(f"Failed to get user data. Status code: {response.status}")

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
