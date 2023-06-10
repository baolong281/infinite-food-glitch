from setup import setup, login
from twscrape import AccountsPool, API, gather
from dotenv import dotenv_values
from img import read_img
from utils import find_code, paste_code, check_tweets, contains_img, get_time, print_green
import sys
import pick
import json
import asyncio
import os
import time

acc_path = "./.env"
config_path = "./config.json"
codes_path = "./codes.txt"

paste = True
if len(sys.argv) > 1:
    if sys.argv[1] == "false":
        paste = False

USER_ID = 141341662  # chipotletweets account id

if not os.path.exists(codes_path):
    with open(codes_path, "w") as f:
        f.write("")

codes = set(line.strip() for line in open("codes.txt"))


def handle_code(code, second, paste):
    if code in codes:
        print(f"Code already used: {code}")
        return

    paste_code(code, paste, load_config())

    print("###########################################")
    for _ in range(8):
        print(f"CODE FOUND: {code}  or  {second}")
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


def choose_option():
    options = [
        "1) Run bot",
        "2) Reconfigure cursor",
        "3) Sign in / Change account info",
        "4) Exit",
    ]
    option, index = pick.pick(
        options,
        "Chipotle Bot / " + ("Pasting enabled" if paste else "Pasting disabled"),
        indicator="=>",
        default_index=0,
    )

    if index == 1:
        setup()
        choose_option()
    elif index == 2:
        login()
        choose_option()
    elif index == 3:
        sys.exit(0)



async def main():
    print()
    print_green("Bot starting...")
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

        if check_tweets(tweets) is False:
            continue

        tweet = tweets[0]
        tweet_content = tweet.rawContent
        tweet_time, current_time = get_time(tweet)

        if contains_img():
            print(tweet_content)
            tweet_content = read_img()

        code, second = find_code(tweet_content)

        if code != "":
            handle_code(code, second, paste)
        else:
            print(tweet_content)
            print_green(f"Posted at: {tweet_time}. Current time: {current_time}")

        time.sleep(2)


if __name__ == "__main__":
    choose_option()
    asyncio.run(main())
