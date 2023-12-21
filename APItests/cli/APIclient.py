# APIclient.py

import json
import requests
import click

API_BASE_URL = "http://localhost:8000/api"
TOKEN_FILE = "token.txt"
COOKIES_FILE = "cookies.txt"


class APIClient:
    def __init__(self):
        self.session = requests.Session()

    def save_cookies(self, cookies):
        with open(COOKIES_FILE, "w") as file:
            file.write(cookies)

    def load_cookies(self):
        try:
            with open(COOKIES_FILE, "r") as file:
                return file.read().strip()
        except FileNotFoundError:
            print("Cookies file not found.")
        except json.JSONDecodeError:
            print("Error decoding JSON in cookies.txt. File may be empty or corrupted.")
            return None

    def save_token(self, token):
        with open(TOKEN_FILE, "w") as file:
            file.write(token)

    def load_token(self):
        try:
            with open(TOKEN_FILE, "r") as file:
                return file.read().strip()
        except FileNotFoundError:
            return None

    def make_api_call(self, method, endpoint, data=None):
        url = API_BASE_URL + endpoint
        cookies = self.load_cookies()
        jwt_token = self.load_token()
        cookie_dict = {}
        
        print(f"Making API call to {url}, cookies: {cookies}, jwt_token: {jwt_token}")

        click.echo(f"Making API call to {url}")

        headers = {}
        if jwt_token:
            headers = {
                "Content-Type": "application/json",
                "X-CSRFToken": cookies,
                "Authorization": f"Bearer {jwt_token}",
            }

        if data and isinstance(data, dict):
            json_data = json.dumps(data)
        else:
            json_data = data

        cookie_dict["csrftoken"] = cookies
        response = self.session.request(method, url, headers=headers, data=json_data, cookies=cookie_dict)

        return response

    def authenticate(self, username, password):
        endpoint = "/user/login/"
        data = {"username": username, "password": password}
        response = self.make_api_call("POST", endpoint, data)

        if response.status_code == 200:
            self.jwt_token = response.json()["access"]
            return self.jwt_token
        else:
            raise click.ClickException("Authentication failed. Please check your credentials.")

    def get_client_id(self, username):
        endpoint = f"/get_user_id/{username}/"
        response = self.make_api_call("GET", endpoint)

        print(response.json())

        if response.status_code == 200:
            return response.json()["user_id"]
        else:
            raise click.ClickException("User not found.")