# SPDX-FileCopyrightText: 2022 Joe Freeman joe@freemansoft.com
#
# SPDX-License-Identifier: MIT
#
# TODO: Why is this file in this project?
from aiy.board import Board, Led
import time
import sys

# Google AIY Voice Hat flash - Raspberry pi

# configure python
# sudo apt-get update
# sudo apt-get install python3-dev python3-venv
# python3 -m venv env
# env/bin/python -m pip install --upgrade pip setuptools wheel
# source env/bin/activate

# This can be dropped
# pip install --upgrade google-assistant-sdk
# python -m pip install --upgrade google-assistant-library==1.0.1

# The simplest way to get all the bits installed including c files to talk pio
# cd ~
# git clone https://github.com/google/aiyprojects-raspbian.git
# cd aiyprojects-raspbian
# sudo python3 ./setup.py install_lib


button_pressed = False


def exit_now():
    global button_pressed
    print("button pressed status {} prior to button press ".format(button_pressed))
    button_pressed = True
    print("button pressed status {}  after button press".format(button_pressed))


def button_flash():
    global button_pressed
    print("LED flashes until button is pressed.")
    with Board() as board:
        board.button.when_pressed = exit_now
        board.led.state = Led.DECAY
        while not (button_pressed):
            print("button pressed status {}".format(button_pressed))
            #            board.led.state = Led.DECAY
            time.sleep(2)


def button_ack():
    print("LED is ON while button is pressed (Ctrl-C for exit).")
    with Board() as board:
        while True:
            board.button.wait_for_press()
            print("ON")
            board.led.state = Led.ON
            board.button.wait_for_release()
            print("OFF")
            board.led.state = Led.OFF


if __name__ == "__main__":
    button_flash()
