from setup import login
from tweety import TwitterAsync
from utils import find_code, paste_code, check_tweets, get_time, turn_green
import argparse
import logging
import sys
import signal
import pick
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
parser.add_argument(
    "--nopaste", action="store_true", help="Disable pasting code into messages"
)
parser.add_argument("--image", action="store_true", help="Enable image scanning")
args = parser.parse_args()

paste = args.nopaste
scan_image = args.image

codes_path = "./codes.txt"
session_path = "./session.tw_session"

REGEX_PATTERN = "[\d\w&%$@!#]+ to 888222"


if not os.path.exists(codes_path):
    with open(codes_path, "w") as f:
        f.write("")

codes = set(line.strip() for line in open("codes.txt"))

def handle_code(code):
    if code in codes:
        logging.info(f"Code already used: {code}")
        return

    paste_code(code)

    logging.info("###########################################")
    for _ in range(8):
        logging.info(f"CODE FOUND: {code}")
    logging.info("###########################################")
    codes.add(code)

    with open("codes.txt", "a") as f:
        f.write(code + "\n")


def choose_option():
    options = [
        "1) Run bot",
        "1) Change Regex",
        "2) Exit",
    ]
    option, index = pick.pick(
        options,
        "Chipotle Bot\n",
        indicator="=>",
        default_index=0,
    )

    if index == 1:
        logging.info("Changing regex...")
        global REGEX_PATTERN
        pattern = input("Enter new regex pattern: ")
        REGEX_PATTERN = pattern
        choose_option()
    elif index == 2:
        sys.exit(0)


async def main():
    logging.info(turn_green("Bot starting..."))

    if not os.path.exists(session_path):
        logging.warning("Account not yet signed in")
        await login()

    # if not scan_image:
    app = TwitterAsync("session")
    await app.connect()
    chipotle = await app.get_user_info("chipotletweets")

    last_tweet_id = None

    while True:
        tweets = await app.get_tweets(chipotle, wait_time=5)

        if check_tweets(tweets) is False:
            continue


        tweet = tweets[0]

        if last_tweet_id is not None and last_tweet_id == tweet.id:
            time.sleep(
                10,
            )  # twitter allows 500ish requests every 15 minuts ~= 1 request every 1.8 seconds
            continue


        try:
            tweet_content = tweet.text
        except Exception as err:
            logging.error(f"Error: {err}")
            logging.error(f"Tweet: {tweet}")
            time.sleep(
                10,
            )  # twitter allows 500ish requests every 15 minuts ~= 1 request every 1.8 seconds
            continue


        last_tweet_id = tweet.id
        logging.info(tweet_content)
        code = find_code(tweet_content, REGEX_PATTERN)

        if code != "":
            handle_code(code)
        elif not scan_image:
            tweet_time, current_time = get_time(tweet)
            logging.info(
                turn_green(f"Posted at: {tweet_time}. Current time: {current_time}")
            )

        time.sleep(
            10,
        )  # twitter allows 500ish requests every 15 minuts ~= 1 request every 1.8 seconds


if __name__ == "__main__":
    choose_option()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Exiting.....")
        sys.exit(0)
