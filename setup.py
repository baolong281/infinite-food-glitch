from pynput import mouse
import pyautogui
import json
import time
from tweety import Twitter


async def login():
    print()
    print("Twitter sign in")
    print("#########################")
    print()

    app = Twitter("session")
    await app.start()

    print()
    print("Account info successfully updated")
    print()
    time.sleep(1.5)


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
