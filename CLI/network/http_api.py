# APIclient.py

import logging
import json
import requests

from utils.logger import log_message
from utils.url_macros import LOGIN, REGISTER, GET_CLIENT_ID, GET_CLIENT_INFO, GET_LIST_FRIENDS, ADD_FRIEND, REMOVE_FRIEND, GET_USER_STATS
from utils.file_manager import FileManager
from datetime import datetime

class http_api:
    def __init__(self):
        self.session = requests.Session()
        self.file_manager = FileManager()
        self.client_id = None

    def close_session(self):
        self.session.close()

# Save/Load data using FileManager
    def save_cookies(self, csrf_token, expires_datetime):
        cookies_dict = {"csrftoken": csrf_token, "expiry": expires_datetime.strftime("%a, %d %b %Y %H:%M:%S %Z")}
        self.file_manager.save_data("cookies.json", cookies_dict)

    def save_token(self, token):
        self.file_manager.save_data("token.json", token)

    def save_client_info(self, client_id, username):
        client_info = {"client_id": client_id, "username": username}
        self.file_manager.save_data("client_info.json", client_info)

    def load_cookies(self):
        return self.file_manager.load_data("cookies.json")

    def load_token(self):
        return self.file_manager.load_data("token.json")

    def load_client_info(self):
        return self.file_manager.load_data("client_info.json")

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

# API caller function
    def make_api_call(self, method, url, data=None):
        try:
            cookies = self.load_cookies()
            jwt_token = self.load_token()
            headers = self._get_request_headers(cookies, jwt_token)

            if data and isinstance(data, dict):
                json_data = json.dumps(data)
            else:
                json_data = data

            response = self.session.request(method, url, headers=headers, data=json_data, cookies=cookies, verify=False)

            return response
        
        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError, requests.exceptions.Timeout) as e:
            log_message(f"Error during API call: {e}", level=logging.ERROR)
            return None
        
    def _get_request_headers(self, cookies, jwt_token):
        headers = {}
        if self.is_cookies_valid(cookies):
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {jwt_token['token']}",
                }
        else:
            print("Cookies or token not valid. Log in again, please...")

        return headers

    def _handle_successful_login(self, response, username):
        jwt_token = response.json().get("token")
        cookies_dict = response.headers.get('Set-Cookie')

        if cookies_dict and jwt_token:
            expires_str = cookies_dict.split('expires=')[1].split(';')[0].strip()
            expires_datetime = datetime.strptime(expires_str, "%a, %d %b %Y %H:%M:%S %Z")
            csrf_token = cookies_dict.split('csrftoken=')[1].split(';')[0].strip()

            self.save_cookies(csrf_token, expires_datetime)
            self.save_token({'token': jwt_token})

            self.client_id = self.get_client_id(username)
            self.save_client_info(self.client_id, username)
# -----------------------------
    
# Predifined Login/Register API calls
    def login(self, username, password):
        try:
            url = LOGIN
            data = {"username": username, "password": password}
            response = self.make_api_call("POST", url, data)

            json_response = response.json()
            if  json_response and response.status_code == 200 and json_response.get('status') == 'ok':
                self._handle_successful_login(response, username)
                return username
            elif json_response:
                log_message(f"Login failed: {response.text}", level=logging.INFO)
                return json_response.get('message')
            else:
                log_message("No response from server.", level=logging.ERROR)
                return False

        except Exception as e:
            log_message(f"Error logging in: {e}", level=logging.ERROR)
            return json_response

    def register(self, username, password, fullname, email):
        try:
            url = REGISTER
            data = {"username": username, "password": password, "fullname": fullname, "email": email}
            response = self.make_api_call("POST", url, data)

            json_response = response.json()

            if response.status_code == 200 and json_response and json_response.get('status') == 'ok':
                self._handle_successful_login(response, username)
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
            url = GET_CLIENT_ID.format(username=username)
            response = self.make_api_call("GET", url)

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
            url = GET_CLIENT_INFO.format(username=username)
            response = self.make_api_call("GET", url)

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
            url = GET_LIST_FRIENDS.format(client_id=client_id)
            response = self.make_api_call("GET", url)

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

            url = ADD_FRIEND.format(client_id=client_id)
            data = {"friend_id": friend_id}

            response = self.make_api_call("POST", url, data)

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

            url = REMOVE_FRIEND.format(client_id=client_id)
            data = {"friend_id": friend_id}

            response = self.make_api_call("POST", url, data)

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
            url = GET_USER_STATS.format(client_id=client_id)
            response = self.make_api_call("GET", url)

            if response.status_code == 200:
                return response.json()
            else:
                log_message(f"Error getting user stats: {response.text}", level=logging.ERROR)
                return False
        except Exception as e:
            log_message(f"Error getting user stats: {e}", level=logging.ERROR)
            return False
# -----------------------------
