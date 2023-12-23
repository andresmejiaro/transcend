# APIclient.py

from datetime import datetime
import json
import requests
import click

API_BASE_URL = "http://localhost:8000/api"
TOKEN_FILE = "./tmp_files/token.txt"
CLIENT_INFO_FILE = "./tmp_files/client_info.txt"
COOKIES_FILE = "./tmp_files/cookies.txt"


class http_api:
    def __init__(self):
        self.session = requests.Session()
        self.client_id = None

    def close_session(self):
        self.session.close()

# Open/Close .txt files (cookies, token, client_info) for saving/loading
    def save_cookies(self, csrf_token, expires_datetime):
        cookies_dict = {"csrftoken": csrf_token, "expiry": expires_datetime.strftime("%a, %d %b %Y %H:%M:%S %Z")}
        with open(COOKIES_FILE, "w") as file:
            file.write(json.dumps(cookies_dict))

    def save_token(self, token):
        with open(TOKEN_FILE, "w") as file:
            file.write(json.dumps(token))

    def save_client_info(self, client_id, username):
        with open(CLIENT_INFO_FILE, "w") as file:
            file.write(json.dumps({"client_id": client_id, "username": username}))

    def load_cookies(self):
        try:
            with open(COOKIES_FILE, "r") as file:
                return json.loads(file.read().strip())
        except FileNotFoundError:
            print("Cookies file not found.")
        except json.JSONDecodeError:
            print("Error decoding JSON in cookies.txt. File may be empty or corrupted.")
            return None

    def load_token(self):
        try:
            with open(TOKEN_FILE, "r") as file:
                return json.loads(file.read().strip())
        except FileNotFoundError:
            return None
        except json.JSONDecodeError:
            print("Error decoding JSON in token.txt. File may be empty or corrupted.")
            return None

    def load_client_info(self):
        try:
            with open(CLIENT_INFO_FILE, "r") as file:
                return json.loads(file.read().strip())
        except FileNotFoundError:
            print("Client info file not found.")
        except json.JSONDecodeError:
            print("Error decoding JSON in client_info.txt. File may be empty or corrupted.")
            return None
# -----------------------------

# API caller function
    def make_api_call(self, method, endpoint, data=None):
        try:
            url = API_BASE_URL + endpoint

            cookies = self.load_cookies()
            jwt_token = self.load_token()

            headers = {}
            if self.is_cookies_valid(cookies):
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {jwt_token['token']}",
                }
            else:
                # Refresh cookies and token if either is not valid
                print("Cookies or token not valid. Log in again please...")

            if data and isinstance(data, dict):
                json_data = json.dumps(data)
            else:
                json_data = data

            print(f'Making {method} request to {url} with data: {json_data}')

            response = self.session.request(method, url, headers=headers, data=json_data, cookies=cookies)

            return response
        
        except requests.exceptions.ConnectionError:
            print("Connection error. Is the server running?")
            return None
        
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error: {e}")
            return None
        
        except requests.exceptions.Timeout:
            print("Request timed out.")
            return None
        
    def is_cookies_valid(self, cookies):
        if cookies and 'expiry' in cookies:
            expiry_str = cookies['expiry'].strip()  # Add .strip() here
            expiry_datetime = datetime.strptime(expiry_str.strip(), "%a, %d %b %Y %H:%M:%S")
            current_datetime = datetime.now()
            return current_datetime < expiry_datetime
        return False
# -----------------------------
    
# Predifined Login/Register API calls
    def login(self, username, password):
        login_url = f"{API_BASE_URL}/user/login/"
        data = {"username": username, "password": password}

        response = self.session.post(login_url, json=data)

        if response.status_code == 200:
            json_response = response.json()
            if json_response['status'] == 'ok':

                jwt_token = json_response.get("token")
                cookies_dict = response.headers.get('Set-Cookie')

                if cookies_dict and jwt_token:
                    # Parse the expiration time from the 'Set-Cookie' header
                    expires_str = cookies_dict.split('expires=')[1].split(';')[0].strip()   
                    # Convert the expiration time to a datetime object
                    expires_datetime = datetime.strptime(expires_str, "%a, %d %b %Y %H:%M:%S %Z")
                    # Get the CSRF token from the 'Set-Cookie' header
                    csrf_token = cookies_dict.split('csrftoken=')[1].split(';')[0].strip()

                    # Save only the expiration date in a format for easy comparison
                    self.save_cookies(csrf_token, expires_datetime)
                    self.save_token({'token': jwt_token})

                    self.client_id = self.get_client_id(username)
                    self.save_client_info(self.client_id, username)

    def register(self, username, password, fullname, email):
        register_url = f"{API_BASE_URL}/user/signup/"
        data = {"username": username, "password": password, "fullname": fullname, "email": email}

        response = self.session.post(register_url, json=data)

        if response.status_code == 200:
            json_response = response.json()
            if json_response['status'] == 'ok':

                jwt_token = json_response.get("token")
                cookies_dict = response.headers.get('Set-Cookie')

                if cookies_dict and jwt_token:
                    # Parse the expiration time from the 'Set-Cookie' header
                    expires_str = cookies_dict.split('expires=')[1].split(';')[0].strip()   
                    # Convert the expiration time to a datetime object
                    expires_datetime = datetime.strptime(expires_str, "%a, %d %b %Y %H:%M:%S %Z")
                    # Get the CSRF token from the 'Set-Cookie' header
                    csrf_token = cookies_dict.split('csrftoken=')[1].split(';')[0].strip()

                    # Save only the expiration date in a format for easy comparison
                    self.save_cookies(csrf_token, expires_datetime)
                    self.save_token({'token': jwt_token})

                    self.client_id = self.get_client_id(username)
                    self.save_client_info(self.client_id, username)
# -----------------------------
                    
# Predifined API calls
    def get_client_id(self, username):
        endpoint = f"/get_user_id/{username}/"
        response = self.make_api_call("GET", endpoint)

        if response.status_code == 200:
            return response.json()["user_id"]
        else:
            raise click.ClickException("User not found.")
        
    def get_client_info(self):
        username = self.load_client_info()["username"]
        endpoint = f"/user/info-me/{username}/"
        response = self.make_api_call("GET", endpoint)

        if response.status_code == 200:
            return response.json()
        else:
            raise click.ClickException("User not found.")

    def get_list_friends(self):
        client_id = self.load_client_info()["client_id"]
        endpoint = f"/user/{client_id}/friendlist/"
        response = self.make_api_call("GET", endpoint)

        if response.status_code == 200:
            return response.json()
        else:
            raise click.ClickException("User not found.")

    def add_friend(self, friend_username):
        client_id = self.load_client_info()["client_id"]
        friend_id = self.get_client_id(friend_username)

        endpoint = f"/user/{client_id}/addfriend/"
        data = {"friend_id": friend_id}

        response = self.make_api_call("POST", endpoint, data)

        if response.status_code == 200:
            return response.json()
        else:
            raise click.ClickException("User not found.")
        
    def remove_friend(self, friend_username):
        client_id = self.load_client_info()["client_id"]
        friend_id = self.get_client_id(friend_username)

        endpoint = f"/user/{client_id}/removefriend/"
        data = {"friend_id": friend_id}

        response = self.make_api_call("POST", endpoint, data)

        if response.status_code == 200:
            return response.json()
        else:
            raise click.ClickException("User not found.")

    def get_user_stats(self):
        client_id = self.load_client_info()["client_id"]
        endpoint = f"/user/{client_id}/stats/"
        response = self.make_api_call("GET", endpoint)

        if response.status_code == 200:
            return response.json()
        else:
            raise click.ClickException("User not found.")
# -----------------------------