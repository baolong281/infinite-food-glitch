import pyautogui
import pyperclip
import json
import asyncio
from twscrape import AccountsPool, API, gather
from twscrape.logger import set_log_level
from dotenv import dotenv_values
import re

env_vars = dotenv_values()

with open('./config.json') as file:
    data = json.load(file)

USER_ID = 141341662 #chipotletweets account id
USERNAME = env_vars['USERNAME']
EMAIL = env_vars['EMAIL']
PASSWORD = env_vars['PASSWORD']

X = data['position'][0]
Y = data['position'][1]

def find_code(str):
    pattern = "[\d\w]+ to 888222" #find pattern 'blahblahblah to 888222'
    matches = re.findall(pattern, str)

    if len(matches) == 0:
        return ''

    return matches[0].split()[0]

def paste_code(str):
    pyautogui.moveTo(X, Y)
    pyautogui.click()
    pyperclip.copy(str)
    pyautogui.keyDown('command')
    pyautogui.press('v')
    
async def main():
    pool = AccountsPool()  
    await pool.add_account(USERNAME, PASSWORD, EMAIL, PASSWORD)
    await pool.login_all()
    api = API(pool)
    
    tweets = await gather(api.user_tweets(USER_ID, limit=1))
    tweet_content = tweets[1].rawContent
    print(tweet_content)


if __name__ == "__main__":
    #asyncio.run(main())
    print(find_code('fortnite to 888222'))
    print(find_code('Agaheuoghaeogh48294t to 888222'))
    print(find_code('DESTROY!!!!!!!!!'))

