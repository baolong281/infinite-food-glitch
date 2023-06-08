import pytesseract
import requests
from utils import print_green
from PIL import Image
from io import BytesIO
from tweety.bot import Twitter


def read_img():
    app = Twitter()
    tweets = app.get_tweets("chipotletweets")

    try:
        tweet = tweets[0]
        img_url = tweet.media[0].media_url_https
        response = requests.get(img_url)
        image = Image.open(BytesIO(response.content))
    except:
        return "err"

    print_green("\nImage reads:\n")
    return pytesseract.image_to_string(image)
