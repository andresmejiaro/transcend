# APIclient.py

from utils.data_storage import load_data, save_data
from utils.logger import log_message
from datetime import datetime
import logging
import json
import requests

API_BASE_URL = "http://localhost:8000/api"
DATA_DIR = "data"

class http_api:
    def __init__(self):
        self.session = requests.Session()
        self.client_id = None

    def close_session(self):
        self.session.close()

# Save/Load data using save_data and load_data
    def save_cookies(self, csrf_token, expires_datetime):
        cookies_dict = {"csrftoken": csrf_token, "expiry": expires_datetime.strftime("%a, %d %b %Y %H:%M:%S %Z")}
        save_data("cookies.json", cookies_dict)

    def save_token(self, token):
        save_data("token.json", token)

    def save_client_info(self, client_id, username):
        client_info = {"client_id": client_id, "username": username}
        save_data("client_info.json", client_info)

    def load_cookies(self):
        return load_data("cookies.json")

    def load_token(self):
        return load_data("token.json")

    def load_client_info(self):
        return load_data("client_info.json")
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

            response = self.session.request(method, url, headers=headers, data=json_data, cookies=cookies)

            return response
        
        except requests.exceptions.ConnectionError:
            log_message("Connection error.", level=logging.ERROR)
            return None
        
        except requests.exceptions.HTTPError as e:
            log_message(f"HTTP error: {e}", level=logging.ERROR)
            return None
        
        except requests.exceptions.Timeout:
            log_message("Request timed out.", level=logging.ERROR)
            return None
        
    def is_cookies_valid(self, cookies):
        try:
            if cookies and 'expiry' in cookies:
                expiry_str = cookies['expiry'].strip()  # Add .strip() here
                expiry_datetime = datetime.strptime(expiry_str.strip(), "%a, %d %b %Y %H:%M:%S")
                current_datetime = datetime.now()
                return current_datetime < expiry_datetime
            return False
        except Exception as e:
            log_message(f"Error checking if cookies are valid: {e}", level=logging.ERROR)
            return False
# -----------------------------
    
# Predifined Login/Register API calls
    def login(self, username, password):
        try:
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

                        return username
            else:
                log_message(f"Login failed: {response.text}", level=logging.ERROR)
                return False
        except Exception as e:
            log_message(f"Error logging in: {e}", level=logging.ERROR)
            return False

    def register(self, username, password, fullname, email):
        try:
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

                        return username
            else:
                log_message(f"Register failed: {response.text}", level=logging.ERROR)
                return False
        except Exception as e:
            log_message(f"Error registering: {e}", level=logging.ERROR)
            return False
# -----------------------------
                    
# Predifined API calls
    def get_client_id(self, username):
        try:
            endpoint = f"/get_user_id/{username}/"
            response = self.make_api_call("GET", endpoint)

            if response.status_code == 200:
                return response.json()["user_id"]
            else:
                log_message(f"Error getting client id: {response.text}", level=logging.ERROR)
                return False
        except Exception as e:
            log_message(f"Error getting client id: {e}", level=logging.ERROR)
            return False
        
    def get_client_info(self):
        try:
            username = self.load_client_info()["username"]
            endpoint = f"/user/info-me/{username}/"
            response = self.make_api_call("GET", endpoint)

            if response.status_code == 200:
                return response.json()
            else:
                log_message(f"Error getting client info: {response.text}", level=logging.ERROR)
                return False
        except Exception as e:
            log_message(f"Error getting client info: {e}", level=logging.ERROR)
            return False

    def get_list_friends(self):
        try:
            client_id = self.load_client_info()["client_id"]
            endpoint = f"/user/{client_id}/friendlist/"
            response = self.make_api_call("GET", endpoint)

            if response.status_code == 200:
                return response.json()
            else:
                log_message(f"Error getting list of friends: {response.text}", level=logging.ERROR)
                return False
        except Exception as e:
            log_message(f"Error getting list of friends: {e}", level=logging.ERROR)
            return False

    def add_friend(self, friend_username):
        try:
            client_id = self.load_client_info()["client_id"]
            friend_id = self.get_client_id(friend_username)

            endpoint = f"/user/{client_id}/addfriend/"
            data = {"friend_id": friend_id}

            response = self.make_api_call("POST", endpoint, data)

            if response.status_code == 200:
                return response.json()
            else:
                log_message(f"Error adding friend: {response.text}", level=logging.ERROR)
                return False
        except Exception as e:
            log_message(f"Error adding friend: {e}", level=logging.ERROR)
            return False
        
    def remove_friend(self, friend_username):
        try:
            client_id = self.load_client_info()["client_id"]
            friend_id = self.get_client_id(friend_username)

            endpoint = f"/user/{client_id}/removefriend/"
            data = {"friend_id": friend_id}

            response = self.make_api_call("POST", endpoint, data)

            if response.status_code == 200:
                return response.json()
            else:
                log_message(f"Error removing friend: {response.text}", level=logging.ERROR)
                return False
        except Exception as e:
            log_message(f"Error removing friend: {e}", level=logging.ERROR)
            return False

    def get_user_stats(self):
        try:
            client_id = self.load_client_info()["client_id"]
            endpoint = f"/user/{client_id}/stats/"
            response = self.make_api_call("GET", endpoint)

            if response.status_code == 200:
                return response.json()
            else:
                log_message(f"Error getting user stats: {response.text}", level=logging.ERROR)
                return False
        except Exception as e:
            log_message(f"Error getting user stats: {e}", level=logging.ERROR)
            return False
# -----------------------------
