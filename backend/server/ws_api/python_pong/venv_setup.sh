#!/bin/bash


python3 -m venv venv

source venv/bin/activate

pip install --upgrade pip


pip install json
pip install click
pip install requests
pip install pynput
pip install curses
pip install time
pip install sys


pip freeze > requirements.txt

pip install --upgrade pip

pip install -r requirements.txt

