import click
import requests
import re

headers = {
    "Content-Type": "application/json",
    # Add other headers as needed
}


def loginAuth(username, password):
    try:
        endpoint = 'http://localhost:8000/api/user/login/'
        payload = {
            "username": username,
            "password": password
        }

        response = requests.post(endpoint, json=payload, headers=headers)
        
        response.raise_for_status()

        csrf_token = response.headers.get('Set-Cookie').split('=')[1].split(';')[0]
        jwt_token = response.json().get('token')
        print(f"CSRF Token: {csrf_token}")
        print(f"JWT Token: {jwt_token}")
        

        click.echo(f"Logged in as {username}.")
        return True

    except requests.exceptions.RequestException as e:
        print(f"Error Logging In status: {e}")
        return False

def checkSignupArgs(username, fullname, email, password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email):
        return False, "Invalid email format"

    return True, ""


def signupAuth(username, fullname, email, password):

    is_valid, message = checkSignupArgs(username, fullname, email, password)
    if is_valid:
        print("Signup arguments are valid")
    else:
        print(f"Invalid signup arguments: {message}")
        return False

    try:
        endpoint = 'http://localhost:8000/api/user/signup/'
        payload = {
            "username": username,
            "fullname": fullname,
            "email": email,
            "password": password
        }

        response = requests.post(endpoint, json=payload, headers=headers)

        response.raise_for_status()

        csrf_token = response.headers.get('Set-Cookie').split('=')[1].split(';')[0]
        jwt_token = response.json().get('token')
        print(f"CSRF Token: {csrf_token}")
        print(f"JWT Token: {jwt_token}")
        

        click.echo(f"Signed In as {username}.")
        return True

    except requests.exceptions.RequestException as e:
        print(f"Error Sign In status: {e}")
        return False

    click.echo(f"Account created for {username}.")

def startAuth():
    username = ""

    while True:
        login_signup_choice = click.prompt("Choose an option: 1 (Login) or 2 (Signup)", type=click.IntRange(1, 2))
        
        if login_signup_choice == 1:
            username = click.prompt("Enter your username")
            password = click.prompt("Enter your password", hide_input=True)
            if loginAuth(username, password):
                break

        elif login_signup_choice == 2:
            username = click.prompt("Choose a username")
            fullname = click.prompt("Choose a fullname")
            email = click.prompt("Choose a email")
            password = click.prompt("Choose a password", hide_input=True)
            if signupAuth(username, fullname, email, password):
                break

    return username

def startPlay():
    # Ask for play options
    play_options_choice = click.prompt("Choose an option: 1 (Play Now) or 2 (Play Tournament) or 3 (Play Against IA)", type=click.IntRange(1, 3))
    if play_options_choice == 1:
        click.echo("Let's start playing now!")
    elif play_options_choice == 2:
        click.echo("Get ready for the tournament!")
    elif play_options_choice == 3:
        click.echo("Get ready for the IA!")


