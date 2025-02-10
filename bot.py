from setup import login
from tweety import TwitterAsync
import argparse
import logging
import sys
import signal
import pick
import asyncio
import os
import time
from datetime import datetime, timezone
import re
import webbrowser
import pyautogui
import tempfile
from PIL import Image, ImageFilter
import requests
import io
import pytesseract

logging.basicConfig(
    level=logging.INFO,
    format="\x1b[32m%(asctime)s\x1b[0m | \x1b[37m%(levelname)s\x1b[0m | \x1b[36m%(module)s:%(funcName)s:%(lineno)d\x1b[0m - %(message)s",
)

def handle_exit(sig, frame):
    logging.info("Exiting.....")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)

parser = argparse.ArgumentParser()
parser.add_argument(
    "--nopaste", action="store_true", help="Disable pasting code into messages"
)
parser.add_argument("--image", action="store_true", help="Enable image scanning")
args = parser.parse_args()

paste = args.nopaste
scan_image = args.image

if scan_image:
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
    except ImportError:
        logging.error("Please install Pillow and pytesseract to use image scanning.")
        sys.exit(1)
    except pytesseract.TesseractNotFoundError:
        logging.error("Tesseract OCR is not installed. Please install it.")
        sys.exit(1)

codes_path = "./codes.txt"
session_path = "./session.tw_session"

REGEX_PATTERN = "[\d\w&%$@!#]+ to 888222"

def download_image(url):
    """Download image using Pillow and requests"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        image = Image.open(io.BytesIO(response.content))
        gray = image.convert('L')
    
        # Apply threshold to create binary image
        # This will help separate the white outline text from background
        binary = gray.point(lambda x: 0 if x < 200 else 255, '1')
        
        # Optional: Apply morphological operations to clean up the text
        binary = binary.filter(ImageFilter.MinFilter(3))
        binary = binary.filter(ImageFilter.MaxFilter(3))
        
        # Optional: Increase image size
        width, height = binary.size
        new_size = (width * 2, height * 2)
        binary = binary.resize(new_size, Image.Resampling.LANCZOS)
        return binary
    except Exception as e:
        logging.error(f"Error downloading image: {e}")
        return None


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
    webbrowser.open(f"sms:888222&body={str}")
    time.sleep(1.5)
    pyautogui.press('enter')

def find_code(str, pattern):
    if pattern == "":
        pattern = "[\d\w&%$@!#]+ to 888222"
    matches = re.findall(pattern, str)
    if len(matches) == 0:
        return ""
    code = matches[0].split()[0]
    return code

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
        "2) Change Regex",
        "3) Exit",
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

    app = TwitterAsync("session")
    await app.connect()
    chipotle = await app.get_user_info("chipotletweets")
    last_tweet_id = None

    while True:
        tweets = await app.get_tweets(chipotle, wait_time=30)
        if not check_tweets(tweets):
            continue

        tweet = tweets[1]

        try:
            tweet_content = tweet.text
        except AttributeError:
            logging.error("Error getting tweet content")
            logging.error(tweet)
            tweet = tweet.tweets[0]
            tweet_content = tweet.text

        if last_tweet_id is not None and last_tweet_id == tweet.id:
            time.sleep(30)
            continue

        last_tweet_id = tweet.id
        logging.info(tweet_content)
        code = find_code(tweet_content, REGEX_PATTERN)

        if code:
            handle_code(code)
        else:
            tweet_time, current_time = get_time(tweet)
            logging.info(turn_green(f"Posted at: {tweet_time}. Current time: {current_time}"))

        if scan_image and tweet.media:
            logging.info("Scanning images in the tweet...")
            for media in tweet.media:
                if media.type == 'photo':
                    try:
                        image = download_image(media.media_url_https)
                        image.show()
                        if image:
                            # Configure Tesseract for better results
                            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                            text = pytesseract.image_to_string(image, config=custom_config)
                            logging.info(f"Image text: {text}")
                            img_code = find_code(text, REGEX_PATTERN)
                            if img_code:
                                handle_code(img_code)
                    except Exception as e:
                        logging.error(f"Error processing image: {e}")

        time.sleep(30)

if __name__ == "__main__":
    choose_option()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Exiting.....")
        sys.exit(0)
