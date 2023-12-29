# views/init_views.py

from app.home.friends import Friends
from app.home.home import Home
from app.home.login import Login
from app.home.profile import Profile
from app.home.register import Register
from app.home.registration import Registration
from app.home.splash_screen import SplashScreen
from app.game.game import Game

def initialize_views(stdscr, http, ws):
    friends_view = Friends(stdscr, http, ws)
    home_view = Home(stdscr, http, ws)
    login_view = Login(stdscr, http, ws)
    profile_view = Profile(stdscr, http, ws)
    register_view = Register(stdscr, http, ws)
    registration_view = Registration(stdscr, http, ws)
    splash_screen = SplashScreen(stdscr, http, ws)
    game_view = Game(stdscr, http, ws)

    # You can add more views as needed
    return [
            {"name": "Home", "view": Home(stdscr, http, ws)},
            {"name": "Friends", "view": Friends(stdscr, http, ws)},
            {"name": "Login", "view": Login(stdscr, http, ws)},
            {"name": "Profile", "view": Profile(stdscr, http, ws)},
            {"name": "Register", "view": Register(stdscr, http, ws)},
            {"name": "Registration", "view": Registration(stdscr, http, ws)},
            {"name": "SplashScreen", "view": SplashScreen(stdscr, http, ws)},
            {"name": "Game", "view": Game(stdscr, http, ws)},
    ]
