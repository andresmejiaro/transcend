import curses
import json
import sys

class View:
    def __init__(self, api_client, websocket_manager, lobby_websocket):
        self.api_client = api_client
        self.websocket_manager = websocket_manager
        self.lobby_websocket = lobby_websocket
        self.online_friends = {}

# Views
    def home_page(self, online_users):
        stdscr = curses.initscr()
        stdscr.clear()
        curses.cbreak()
        stdscr.keypad(True)

        try:
            # Set up colors
            curses.start_color()
            curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)

            user_info_response = self.api_client.get_client_info()
            user_friend_list = self.api_client.get_list_friends()

            user_info = user_info_response.get("user", {})
            friends = user_friend_list.get("data", {})

            # Filter online friends
            self.online_friends = [friend for friend in friends if friend.get("username") in online_users.values()]

            username = user_info.get("username")

            self.print_debug(f"Username: {username}")
            self.print_debug(f"Online friends: {self.online_friends}")
            self.print_debug(f"All friends: {friends}")

            # Calculate centered position for the title
            title_width = len(f" Welcome to the Home Page, {username}! ")
            title_position = (stdscr.getmaxyx()[1] - title_width) // 2

            # Draw title in cyan
            stdscr.addstr(0, title_position, f" Welcome to the Home Page, {username}! ", curses.color_pair(1) | curses.A_BOLD)

            # Draw online friends box and get its height
            online_friends_content = [f"{i + 1}. {friend['username']}" for i, friend in enumerate(self.online_friends)]
            online_friends_height = self.draw_box(stdscr, "Online Friends", online_friends_content, 2, 0, 80, curses.color_pair(2))

            # Draw all friends box below the online friends box
            all_friends_content = [f"{i + 1}. {friend['username']}" for i, friend in enumerate(friends)]
            all_friends_height = self.draw_box(stdscr, "All Friends", all_friends_content, 2 + online_friends_height, 0, 80, curses.color_pair(2))

            # Draw user options box below the all friends box
            options = [
                "1. Invite Friend",
                "2. Remove Friend",
                "3. Play Pong with Friend",
                "4. Play Pong Against AI",
                "5. Random Matchmaking",
                "6. See My Stats",
            ]
            self.draw_box(stdscr, "User Options", options, 2 + online_friends_height + all_friends_height, 0, 80, curses.color_pair(2))

            stdscr.addstr(12 + len(self.online_friends) + len(friends) + len(options) + 4, 0, "Select an option: ", curses.color_pair(2))
            stdscr.refresh()

            # Get user input
            user_input = stdscr.getch()

            if user_input == ord('1'):
                # self.add_friend(online_users)
                pass
            elif user_input == ord('2'):
                # Implement the logic for removing a friend
                pass
            elif user_input == ord('3'):
                # Implement the logic for playing Pong with a friend
                pass
            elif user_input == ord('4'):
                # Implement the logic for playing Pong against AI
                pass
            elif user_input == ord('5'):
                self.play_pong_against_random(online_users)
                pass
            elif user_input == ord('6'):
                self.see_my_stats(online_users)

        finally:
            # Cleanup after displaying any view
            curses.endwin()

    def see_my_stats(self, online_users):
        stdscr = curses.initscr()
        stdscr.clear()
        curses.cbreak()
        stdscr.keypad(True)

        try:
            # Set up colors
            curses.start_color()
            curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)

            user_info = self.api_client.get_user_stats()

            # Extract user information
            user_data = user_info.get("data", {})
            username = user_data.get("username", "N/A")
            elo = user_data.get("ELO", "N/A")
            match_wins = user_data.get("total_match_wins", 0)
            tournament_wins = user_data.get("total_tournament_wins", 0)

            self.print_debug(f"Incoming user info: {user_info}")

            # Calculate centered position for the title
            title_width = len(f" Welcome to the Home Page, {username}! ")
            title_position = (stdscr.getmaxyx()[1] - title_width) // 2

            # Draw title in cyan
            stdscr.addstr(0, title_position, f" Welcome to the Home Page, {username}! ", curses.color_pair(1) | curses.A_BOLD)

            # Draw user info box and get its height
            user_info_content = [
                f"User ID: {user_data.get('id', 'N/A')}",
                f"Username: {username}",
                f"ELO: {elo}",
                f"Match Wins: {match_wins}",
                f"Tournament Wins: {tournament_wins}",
            ]
            user_info_height = self.draw_box(stdscr, "User Info", user_info_content, 2, 0, 80, curses.color_pair(2))

            # Draw the message right below the user info box
            message = "Press any key to go back to the Home Page."
            message_start_row = 2 + user_info_height
            stdscr.addstr(message_start_row, 0, message, curses.color_pair(2))
            stdscr.refresh()

            # Get user input
            stdscr.getch()
            # Return to home_page after getting user input
            self.home_page(online_users)

        finally:
            pass

    def play_pong_against_random(self, online_users):
        pass
# ----------------------------------------------------------

# Helper methods
    def draw_box(self, stdscr, title, content, start_row, start_col, width, color_pair):
        # Calculate box height
        box_height = len(content) + 4  # 2 lines for title, 1 line for top border, 1 line for bottom border

        # Draw box title
        stdscr.addstr(start_row, start_col, f"+ {'-' * (width - 4)} +", color_pair)
        stdscr.addstr(start_row + 1, start_col, f"| {title.center(width - 4)} |", color_pair)
        stdscr.addstr(start_row + 2, start_col, f"+{'-' * (width - 2)}+", color_pair)

        # Draw box content
        for i, line in enumerate(content, 1):
            stdscr.addstr(start_row + 2 + i, start_col, f"| {line.ljust(width - 4)} |", color_pair)

        # Draw box bottom
        stdscr.addstr(start_row + 2 + len(content) + 1, start_col, f"+{'-' * (width - 2)}+", color_pair)

        # Return the calculated height
        return box_height

    def get_user_input(self, stdscr, prompt, friends, options):
        curses.echo()
        stdscr.addstr(15 + len(self.online_friends) + len(friends) + len(options) + 8, 0, prompt, curses.color_pair(2))
        stdscr.refresh()
        user_input = stdscr.getstr(16 + len(self.online_friends) + len(friends) + len(options) + 9, 0, 60).decode('utf-8')
        curses.noecho()
        return user_input

    def print_debug(self, message):
        with open("debug_output.txt", "a") as debug_file:
            debug_file.write(f"{message}\n")
# ----------------------------------------------------------