from Game import Game
from Player import Player
import json
import click
from auth import startAuth, startPlay
import requests
from pynput import keyboard
import curses
import time
import sys

dictKeyboard = {}



def check_server_status():
    url = "http://localhost:8000/api/test/"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        return True  # Server is running and responded successfully
    except requests.exceptions.RequestException as e:
        print(f"Error checking server status: {e}")
        return False  # Server is not running or encountered an error


def update_key_status(key_status):
    def on_press(key):
        key_status[getattr(key, 'char', key)] = True

    def on_release(key):
        key_status[getattr(key, 'char', key)] = False

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

def scaler(prior, priorMax, posMax):
    return int(posMax * prior / priorMax)


def rectdrawer(dictCanvas: dict, obj:str, stdscr, 
               enclousure = {"xl" : 0,"xh": 858,"yl": 0,"yh": 525}):
    height,width = stdscr.getmaxyx()
    startY = scaler(dictCanvas[obj]["position"]["y"],enclousure["yh"],height)
    endY = scaler(dictCanvas[obj]["position"]["y"] + dictCanvas[obj]["size"]["y"],enclousure["yh"],height)
    startX = scaler(dictCanvas[obj]["position"]["x"],enclousure["xh"],width)
    endX = scaler(dictCanvas[obj]["position"]["x"] + dictCanvas[obj]["size"]["x"],enclousure["xh"],width)
    for i in range(round(startY), round(endY)):
        for j in range(round(startX), round(endX)):
            stdscr.addstr(i, j, "x")


def curses_main(stdscr, username):
    leftP = Player(username,binds={"up" : "w", "down":"s", "left":"xx","right":"xx"})
    rightP = Player("Javier",binds={"up" : "t", "down":"g", "left":"xx","right":"xx"})

    game1 = Game(dictKeyboard, leftP, rightP)

    listener = update_key_status(dictKeyboard)
    game1.start()

    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(True)  # Non-blocking input
    stdscr.clear()  # Clear the screen
    curses.noecho()
    report = {}
    while True:
        stdscr.clear()  # Clear the screen
        stdscr.getch()
        actualT = str(time.time())
        report[actualT] = {}
        report[actualT]["keyboard"] = dictKeyboard.copy()
        report[actualT]["canvas"] = game1.reportScreen()
        rectdrawer(report[actualT]["canvas"], "ball", stdscr)
        rectdrawer(report[actualT]["canvas"], "leftPaddle", stdscr)
        rectdrawer(report[actualT]["canvas"], "rightPaddle", stdscr)
        height, width = stdscr.getmaxyx()
        scoreb = ''
        report[actualT]["score"] = game1.reportScore()
        for key, value in report[actualT]["score"].items():
            scoreb += f"{key}: {value} "
        stdscr.addstr(2, int((width - len(scoreb)) / 2), scoreb)
        stdscr.refresh()  # Refresh the screen to show updates
        fps = 30
        time.sleep(1 / fps)  # Adjust for desired refresh rate
        if not game1.isAlive():
            curses.echo()
            with open(actualT + ".json", "w") as file:
                json.dump(report, file)
            break

@click.command()
def main():
    click.echo("Hello! Welcome to the Game CLI.")

    if not check_server_status():
        print("Server is not running or encountered an error. Exiting.")
        sys.exit()

    username = startAuth()

    startPlay()
    time.sleep(0.5)
    curses.wrapper(curses_main, username)


if __name__ == "__main__":
    main()
