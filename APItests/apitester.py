import requests
import random
import string
import json
import argparse


# For PUT DELETE POST
# python3 apitester.py <endpoint> <method> --data <data>
# python3 apitester.py tournament/1/ PUT --data '{"name": "test", "type": "test", "start_date": "2021-04-20T00:00:00Z", "end_date": "2021-04-20T00:00:00Z", "round": 1, "players": [1, 2, 3], "observers": [1, 2, 3]}'
# python3 apitester.py tournament/1/ DELETE
# For GET
# python3 apitester.py <endpoint> <method>
# python3 apitester.py tournament/1/ GET

BASE_URL = "http://localhost:8000/api/"  # Replace with your actual base URL

def get_cookie():
    # Fetch CSRF token
    csrf_token_url = BASE_URL + "user/csrftoken/"
    csrf_token_response = requests.get(csrf_token_url)
    print(csrf_token_response.cookies)

    return csrf_token_response.cookies

def signup_user(username, password, fullname, email, cookie=None):
    # Fetch CSRF token
    csrf_token = cookie.get('csrftoken')

    # Signup URL and data
    signup_url = BASE_URL + "user/signup/"
    headers = {
    "Content-Type": "application/json",
    "X-CSRFToken": csrf_token,
    }
    payload = {
    "username": username,
    "password": password,
    "email": email,
    "fullname": fullname,
    "is_superuser": True,
    }

    # Make the signup request

    response = requests.request("POST", signup_url, json=payload, headers=headers, cookies=cookie)

    jwt_token = response.json().get("token")
    if jwt_token:
        return jwt_token
    else:
        print(f"Failed to signup user. Status code: {response.status_code}")
        return False

def make_api_call(endpoint, method="GET", data=None, jwt_token=None, cookies=None, username=None):
    url = BASE_URL + endpoint

    csrf_token = cookies.get('csrftoken')

    headers = {}
    if jwt_token:
        headers = {
            "Content-Type": "application/json",
            "X-CSRFToken": csrf_token,
            "Authorization": f"Bearer {jwt_token}",
        }
    payload = {
        'token': jwt_token,
        "username": username
    }

    # print(f"Making {method} request to {url} with data: {data} and headers: {headers} with JWT token: {jwt_token}")

    if method == "GET":
        response = requests.get(url, json=data, headers=headers, cookies=cookies, params=payload)
    elif method == "POST":
        response = requests.post(url, json=data, headers=headers, cookies=cookies, params=payload)
    elif method == "PUT":
        response = requests.put(url, json=data, headers=headers, cookies=cookies, params=payload)
    elif method == "DELETE":
        response = requests.delete(url, headers=headers, cookies=cookies, params=payload)
    else:
        print(f"Unsupported HTTP method: {method}")
        return False
        
    return response


def main():
    parser = argparse.ArgumentParser(description='Make API requests.')
    parser.add_argument('endpoint', type=str, help='API endpoint')
    parser.add_argument('method', type=str, help='HTTP method (GET, POST, PUT, DELETE)')
    parser.add_argument('--data', type=str, help='Data to bsent in the request (for POST and PUT methods)')

    args = parser.parse_args()


    # Replace these with your actual credentials
    # Generate a random username
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6)) + "test"

    # Generate a random password
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

    # Generate a random fullname (assuming you want a random string)
    fullname = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=6)) + "test"

    # Generate a random email (assuming you want a random string)
    email = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6)) + "@test.com"

    cookie = get_cookie()

    if args.method.upper() == 'POST' or args.method.upper() == 'PUT':
        if not args.data:
            print('Error: --data is required for POST and PUT requests.')
            return

        try:
            data = json.loads(args.data)

        except json.JSONDecodeError as e:
            print(f'Error decoding JSON data: {e}')
            return

    else:
        data = None


    # Signup the user
    jwt_token = signup_user(username, password, fullname, email, cookie=cookie)
    
    if not jwt_token:
        print("Failed to register user. JWT token not found.")
        return

    # Make sure we have a JWT token
    if jwt_token:
        print("Connected to API")
        # Make the API call
        response = make_api_call(args.endpoint, method=args.method, data=data, jwt_token=jwt_token, cookies=cookie, username=username)
        # If the API call succeeded, output all data including the JWT token etc
    if response:
        # Print the response data in a clean format
        print(f"Response Status: {response.status_code}")
        print("Response Data:")
        print(json.dumps(response.json(), indent=2))
        
        # Print the status and status code
        return
    else:
        print(f"Response Status: {response.status_code}")
        return 

if __name__ == '__main__':
    main()