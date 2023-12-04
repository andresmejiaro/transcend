from Game import Game
from Player import Player
import json

dictKeyboard = {}
leftP = Player("Andres",binds={"up" : "w", "down":"s", "left":"xx","right":"xx"})
rightP = Player("Javier",binds={"up" : "t", "down":"g", "left":"xx","right":"xx"})

game1 = Game(dictKeyboard, leftP, rightP)

from pynput import keyboard

def update_key_status(key_status):
    def on_press(key):
        key_status[getattr(key, 'char', key)] = True

    def on_release(key):
        key_status[getattr(key, 'char', key)] = False

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

listener = update_key_status(dictKeyboard)


game1.start()




import curses
import time

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




def main(stdscr):
    # Initialize curses
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
        rectdrawer(report[actualT]["canvas"],"ball",stdscr)
        rectdrawer(report[actualT]["canvas"],"leftPaddle",stdscr)
        rectdrawer(report[actualT]["canvas"],"rightPaddle",stdscr)
        height,width = stdscr.getmaxyx()
        scoreb = ''
        report[actualT]["score"] = game1.reportScore()
        for key, value in report[actualT]["score"].items():
            scoreb += f"{key}: {value} "
        stdscr.addstr(2,int((width - len(scoreb))/2), scoreb)
        stdscr.refresh()  # Refresh the screen to show updates
        fps = 30
        time.sleep(1/fps)  # Adjust for desired refresh rate
        if not game1.isAlive():
            curses.echo()
            with open(actualT + ".json","w") as file:
                json.dump(report, file)
            break
        

    stdscr.clear()

# Run the program
curses.wrapper(main)