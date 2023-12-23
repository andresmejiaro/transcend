import os

class View:
    def __init__(self, api_client, websocket_manager):
        self.api_client = api_client
        self.websocket_manager = websocket_manager

    def home_page(self):
        user_info_response = self.api_client.get_client_info()
        user_friend_list = self.api_client.get_list_friends()

        os.system("clear")

        user_info = user_info_response.get("user", {})
        friends = user_friend_list.get("data", {})

        username = user_info.get("username")
        email = user_info.get("email")

        # Calculate dynamic content width based on the maximum length
        max_username_length = max(len(username), max(len(friend.get('username')) for friend in friends))
        max_option_length = max(len(option) for option in ["Invite Friend", "Play Pong with Friend", "Play Pong Against AI", "See My Stats"])

        content_width = max(max_username_length, max_option_length) + 5

        # Display the main content
        print("+" + "-" * content_width + "+")
        print(f"| Welcome to the Home Page{' ' * (content_width - 25)}|")
        print("+" + "-" * content_width + "+")

        # Check if username and email are not None
        username_display = f" Username: {username}" if username else " Username: N/A"

        print(f"|{username_display.ljust(content_width)}|")
        print("+" + "-" * content_width + "+")

        print("| Friends:                 |")

        # Counter variable for friend numbers
        friend_number = 1

        for friend in friends:
            print(f"| {str(friend_number) + '. ' + friend.get('username').ljust(content_width - 5)} |")
            friend_number += 1

        print("+" + "-" * content_width + "+")

        # User Options section
        print("| User Options:            |")
        options = [
            "Fiend Invite",
            "Play Pong with Friend",
            "Play Pong Against AI",
            "See My Stats",
        ]

        for i, option in enumerate(options, 1):
            print(f"| {i}. {option.ljust(content_width - 5)} |")

        print("+" + "-" * content_width + "+")


    def friend_invite(self):
        pass

    def play_pong_with_friend(self):
        pass

    def play_pong_against_ai(self):
        pass

    def see_my_stats(self):
        pass


    def pong_game(self, match_id, player1, player2, websocket):
        pass