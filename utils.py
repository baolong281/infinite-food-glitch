from datetime import datetime, timezone
import re
import logging
import time
import webbrowser
import pyautogui

logging.basicConfig(
    level=logging.INFO,
    format="\x1b[32m%(asctime)s\x1b[0m | \x1b[37m%(levelname)s\x1b[0m | \x1b[36m%(module)s:%(funcName)s:%(lineno)d\x1b[0m - %(message)s",
)

logging.getLogger("httpx").setLevel(logging.WARNING)


def turn_green(str):
    GREEN = "\033[32m"
    RESET = "\033[0m"
    return GREEN + str + RESET


def get_time(tweet):
    tweet_time = tweet.date
    tweet_time = tweet_time.strftime("%m/%d/%Y %H:%M")
    current_time = datetime.now(timezone.utc).strftime("%m/%d/%Y %H:%M")
    return tweet_time, current_time


def check_tweets(tweets):
    if len(tweets) < 1:
        logging.info("No tweets found")
        time.sleep(.10)
        return False
    return True


def paste_code(str):
    webbrowser.open(f"sms:+888222&body={str}")
    time.sleep(1)
    pyautogui.press('enter')

def find_code(str, pattern):

    # default pattern
    if pattern == "":
        pattern = "[\d\w&%$@!#]+ to 888222"

    matches = re.findall(pattern, str)
    if len(matches) == 0:
        return ("", "")

    code = matches[0].split()[0]

    second = ""
    if len(code.split("FREETHREES")) > 1:
        second = code.split("FREETHREES")[1]

    return code, second
