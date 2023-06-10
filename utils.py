from datetime import datetime, timezone
import re
import time
import pyperclip
import pyautogui
from tweety.bot import Twitter


def print_green(str):
    GREEN = "\033[32m"
    RESET = "\033[0m"
    print(GREEN + str + RESET)


def get_time(tweet):
    tweet_time = tweet.date
    tweet_time = tweet_time.strftime("%m/%d/%Y %H:%M")
    current_time = datetime.now(timezone.utc).strftime("%m/%d/%Y %H:%M")
    return tweet_time, current_time


def contains_img():
    app = Twitter()
    tweets = app.get_tweets("chipotletweets")

    try:
        tweet = tweets[0]
        return len(tweets.media > 0)
    except:
        return False



def check_tweets(tweets):
    if len(tweets) < 1:
        print("No tweets found")
        time.sleep(2)
        return False
    return True


def paste_code(str, paste, coords):
    pyperclip.copy(str)
    if paste:
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
        return ('', '')

    code = matches[0].split()[0]

    second = ''
    if len(code.split('FREETHREES')) > 1:
        second = code.split('FREETHREES')[1]

    return code, second
