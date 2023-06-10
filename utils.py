from datetime import datetime, timezone
from tweety.bot import Twitter
from io import BytesIO
from PIL import Image
import pytesseract
import pyperclip
import pyautogui
import requests
import logging
import time
import sys
import re

logging.basicConfig(
    level=logging.INFO,
    format="\x1b[32m%(asctime)s\x1b[0m | \x1b[37m%(levelname)s\x1b[0m | \x1b[36m%(module)s:%(funcName)s:%(lineno)d\x1b[0m - %(message)s",
)

logging.getLogger("httpx").setLevel(logging.WARNING)


def print_green(str):
    GREEN = "\033[32m"
    RESET = "\033[0m"
    logging.info(GREEN + str + RESET)


def get_time(tweet):
    tweet_time = tweet.date
    tweet_time = tweet_time.strftime("%m/%d/%Y %H:%M")
    current_time = datetime.now(timezone.utc).strftime("%m/%d/%Y %H:%M")
    return tweet_time, current_time


def handle_img():
    app = Twitter()
    tweets = app.get_tweets("blahburner123")

    try:
        tweet = tweets[0]
        if len(tweet.media) > 0:
            img_url = tweet.media[0].media_url_https
            response = requests.get(img_url)
            image = Image.open(BytesIO(response.content))
            print_green("\nImage reads:\n")
            return pytesseract.image_to_string(image).replace("\n", " ")
        else:
            logging.info("Tweet has no media")
    except Exception as e:
        logging.error(f"Error getting tweet media: {e}")

    return ""


def check_tweets(tweets):
    if len(tweets) < 1:
        logging.info("No tweets found")
        time.sleep(2)
        return False
    return True


def paste_code(str, paste, coords):
    pyperclip.copy(str)
    if not paste:
        X, Y = coords
        pyautogui.moveTo(X, Y)
        pyautogui.click()
        pyautogui.click()
        pyautogui.keyDown("command")
        pyautogui.press("v")
        pyautogui.keyUp("command")
        pyautogui.press("enter")


def find_code(str):
    pattern = "[\d\w&%$@!#]+ to 888222"  # find pattern 'blahblahblah to 888222'
    matches = re.findall(pattern, str)
    if len(matches) == 0:
        return ("", "")

    code = matches[0].split()[0]

    second = ""
    if len(code.split("FREETHREES")) > 1:
        second = code.split("FREETHREES")[1]

    return code, second
