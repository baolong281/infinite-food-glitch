import time
from tweety import Twitter


async def login():
    print()
    print("Twitter sign in")
    print("#########################")
    print()

    app = Twitter("session")
    await app.start()

    print()
    print("Account info successfully updated")
    print()
    time.sleep(1.5)

