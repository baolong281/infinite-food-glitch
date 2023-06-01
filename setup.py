import pyautogui
import json
import time
from pynput import mouse
import os


def login():
    print()
    print("#########################")
    print("Twitter sign in")
    print("#########################")
    print()
    username = input("Twitter username: ")
    email = input("Twitter email: ")
    password = input("Twitter password: ")

    with open(".env", "w") as f:
        f.write(f"USERNAME={username}\nEMAIL={email}\nPASSWORD={password}\n")


def setup():
    print()
    print("#########################")
    print("Configuration")
    print("Click on where your iMessage box will be")
    print("#########################")
    print()

    def on_click(x, y, button, pressed):
        if pressed:
            return False

    listener = mouse.Listener(on_click=on_click)
    listener.start()
    listener.join()

    x, y = pyautogui.position()
    print(f"Mouse position: {x}, {y}")

    config = {"position": [x, y]}

    config_path = "./config.json"

    with open(config_path, "w") as f:
        json.dump(config, f)

    print("Config successfully updated!")
    print()
    time.sleep(1.5)
