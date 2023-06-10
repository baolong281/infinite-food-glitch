from setup import setup, login
from twscrape import AccountsPool, API, gather
from dotenv import dotenv_values
from utils import find_code, paste_code, check_tweets, get_time, print_green, handle_img
import argparse
import logging
import sys
import signal
import pick
import json
import asyncio
import os
import time

logging.basicConfig(
    level=logging.INFO,
    format="\x1b[32m%(asctime)s\x1b[0m | \x1b[37m%(levelname)s\x1b[0m | \x1b[36m%(module)s:%(funcName)s:%(lineno)d\x1b[0m - %(message)s",
)


# ------------ handling exit ------------
def handle_exit(sig, frame):
    logging.info("Exiting.....")
    sys.exit(0)


signal.signal(signal.SIGINT, handle_exit)
# ----------------------------------------

parser = argparse.ArgumentParser()
parser.add_argument("--nopaste", type=bool, help="Paste code into messages")
parser.add_argument("--image", type=bool, help="Scans for images or not")
args = parser.parse_args()

paste = args.nopaste
scan_image = args.image

USER_ID = 141341662  # chipotletweets account id

acc_path = "./.env"
config_path = "./config.json"
codes_path = "./codes.txt"


if not os.path.exists(codes_path):
    with open(codes_path, "w") as f:
        f.write("")

codes = set(line.strip() for line in open("codes.txt"))


def handle_code(code, second, paste):
    if code in codes:
        logging.info(f"Code already used: {code}")
        return

    paste_code(code, paste, load_config())

    logging.info("###########################################")
    for _ in range(8):
        logging.info(f"CODE FOUND: {code}  or  {second}")
    logging.info("###########################################")
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
    print_green("Bot starting...")

    if not os.path.exists(acc_path):
        logging.warning("Account not yet signed in")
        login()

    if not os.path.exists(config_path) and paste:
        logging.warning("Config not yet generated")
        setup()

    if os.path.exists("./accounts.db"):
        os.remove("./accounts.db")

    if not scan_image:
        pool = AccountsPool()
        USERNAME, EMAIL, PASSWORD = load_acc()

        await pool.add_account(USERNAME, PASSWORD, EMAIL, PASSWORD)
        await pool.login_all()

        api = API(pool)

    while True:
        if not scan_image:
            tweets = await gather(api.user_tweets(USER_ID, limit=1))

            if check_tweets(tweets) is False:
                continue

            tweet = tweets[0]
            tweet_content = tweet.rawContent
        else:
            tweet_content = handle_img()
            logging.info(tweet_content)

        code, second = find_code(tweet_content)
        if code != "":
            handle_code(code, second, paste)
        elif not scan_image:
            tweet_time, current_time = get_time(tweet)
            print_green(f"Posted at: {tweet_time}. Current time: {current_time}")

        time.sleep(
            1.85
        )  # twitter allows 500ish requests every 15 minuts ~= 1 request every 1.8 seconds


if __name__ == "__main__":
    choose_option()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Exiting.....")
        sys.exit(0)
