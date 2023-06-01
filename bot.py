from setup import setup, login
from pynput import mouse
from twscrape import AccountsPool, API, gather
from twscrape.logger import set_log_level
from dotenv import dotenv_values
from datetime import datetime, timezone
import sys
import subprocess
import pick
import pyautogui
import pyperclip
import json
import asyncio
import os
import time
import re


acc_path = "./.env"
config_path = "./config.json"
codes_path = "./codes.txt"

paste = True
if len(sys.argv) > 1:
    if sys.argv[1] == 'false':
        paste = False

#USER_ID = 141341662  # chipotletweets account id
USER_ID = 1663919694011670530

if not os.path.exists(codes_path):
    with open(codes_path, "w") as f:
        f.write("")

codes = set(line.strip() for line in open("codes.txt"))

def find_code(str):
    pattern = "[\d\w]+ to 888222"  # find pattern 'blahblahblah to 888222'
    matches = re.findall(pattern, str)
    if len(matches) == 0:
        return ""

    code = matches[0].split()[0]
    return code


def paste_code(str):
    pyperclip.copy(str)
    if paste:
        X, Y = load_config()
        pyautogui.moveTo(X, Y)
        pyautogui.click()
        pyautogui.click()
        pyautogui.keyDown("command")
        pyautogui.press("v")
        pyautogui.keyUp("command")
        pyautogui.press("enter")


def check_tweets(tweets):
    if len(tweets) < 2:
        print("no tweets found")
        time.sleep(2)
        return False
    return True


def handle_code(code):
    if code in codes:
        print(f"Code already used: {code}")
        return

    paste_code(code)

    print("###########################################")
    for _ in range(8):
        print(f"CODE FOUND!!!!: {code}")
    print("###########################################")
    codes.add(code)

    with open("codes.txt", "a") as f:
        f.write(code + "\n")


def load_config():
    with open(config_path) as file:
        data = json.load(file)

    X = data["position"][0]
    Y = data["position"][1]

    return X, Y


def load_acc():
    env_vars = dotenv_values()
    USERNAME = env_vars["USERNAME"]
    EMAIL = env_vars["EMAIL"]
    PASSWORD = env_vars["PASSWORD"]

    return USERNAME, EMAIL, PASSWORD


async def main():
    print()
    print("Bot starting...")
    print()

    if not os.path.exists(acc_path):
        print("Account not yet signed in")
        login()

    if not os.path.exists(config_path) and paste:
        print("Config not yet generated")
        setup()

    if os.path.exists("./accounts.db"):
        os.remove("./accounts.db")

    pool = AccountsPool()
    USERNAME, EMAIL, PASSWORD = load_acc()

    await pool.add_account(USERNAME, PASSWORD, EMAIL, PASSWORD)
    await pool.login_all()

    api = API(pool)

    while True:
        tweets = await gather(api.user_tweets(USER_ID, limit=1))

        if check_tweets(tweets) == False:
            continue

        tweet_content = tweets[0].rawContent
        tweet_time = tweets[0].date
        tweet_time = tweet_time.strftime("%d/%m/%Y %H:%M")
        current_time = datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M')
        code = find_code(tweet_content)

        if code != "":
            handle_code(code)
        else:
            print(tweet_content)
            print(f'Posted at: {tweet_time}. Current time: {current_time}')

        print()
        time.sleep(2)


def choose_option():
    options = [
        "1) Run bot",
        "2) Reconfigure cursor",
        "3) Sign in / Change account info",
        "4) Exit"
    ]
    option, index = pick.pick(options, "Chipotle Bot / " + ("Pasting enabled" if paste else 'Pasting disabled'), indicator="=>", default_index=0)

    if index == 1:
        setup()
        choose_option()
    elif index == 2:
        login()
        choose_option()
    elif index==3:
        sys.exit(0)


if __name__ == "__main__":
    choose_option()
    asyncio.run(main())
