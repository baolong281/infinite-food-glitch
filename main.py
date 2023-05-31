import pyautogui
import pyperclip
import json
import asyncio
from twscrape import AccountsPool, API, gather
from twscrape.logger import set_log_level
from dotenv import dotenv_values
import time
import re

env_vars = dotenv_values()

with open("./config.json") as file:
    data = json.load(file)

# USER_ID = 141341662 #chipotletweets account id
USER_ID = 1663919694011670530  # blahburner123
USERNAME = env_vars["USERNAME"]
EMAIL = env_vars["EMAIL"]
PASSWORD = env_vars["PASSWORD"]

X = data["position"][0]
Y = data["position"][1]

codes = set(line.strip() for line in open("codes.txt"))


def find_code(str):
    pattern = "[\d\w]+ to 888222"  # find pattern 'blahblahblah to 888222'
    matches = re.findall(pattern, str)
    if len(matches) == 0:
        return ""

    code = matches[0].split()[0]
    return code


def paste_code(str):
    pyautogui.moveTo(X, Y)
    pyautogui.click()
    pyperclip.copy(str)
    pyautogui.keyDown("command")
    pyautogui.press("v")
    pyautogui.keyUp('command')
    pyautogui.press('enter')



def check_tweets(tweets):
    if len(tweets) < 2:
        print("no tweets found")
        time.sleep(2)
        return False
    return True


def handle_code(code):
    if code in codes:
        print(f'Code already used: {code}')
        return

    paste_code(code)
    print("###########################################")
    for _ in range(3):
        print(f"CODE FOUND!!!!: {code}")
    print("###########################################")
    codes.add(code)

    with open('codes.txt', 'a') as f:
        f.write(code+'\n')


async def main():
    pool = AccountsPool()
    await pool.add_account(USERNAME, PASSWORD, EMAIL, PASSWORD)
    await pool.login_all()
    api = API(pool)

    count = 0
    while True:
        tweets = await gather(api.user_tweets(USER_ID, limit=1))

        if check_tweets(tweets) == False:
            continue

        tweet_content = tweets[1].rawContent
        code = find_code(tweet_content)

        if code != "":
            handle_code(code)
        else:
            print(count, tweet_content)

        print()
        count += 1
        time.sleep(2)


if __name__ == "__main__":
    asyncio.run(main())
