import os
import time
import dotenv
import tweepy as tp
from apscheduler.schedulers.background import BackgroundScheduler

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv()

scheduler = BackgroundScheduler()

# refer to notebook to get refresh and access tokens
auth = tp.OAuth2UserHandler(client_id=os.getenv('client_id'),
                            client_secret=os.getenv('client_secret'),
                            redirect_uri=os.getenv('redirect_uri'),
                            scope=['tweet.read', 'tweet.write', 'tweet.moderate.write', 'users.read',
                                   'follows.write', 'offline.access', 'space.read', 'like.write',
                                   'bookmark.write'],
                            )


def refresh_token():
    token_data = auth.refresh_token(
        'https://api.twitter.com/2/oauth2/token', os.environ["REFRESH_TOKEN"]
    )
    os.environ['APP_ACCESS_TOKEN'] = token_data['access_token']
    os.environ['REFRESH_TOKEN'] = token_data['refresh_token']
    dotenv.set_key(dotenv_file, "APP_ACCESS_TOKEN", os.environ["APP_ACCESS_TOKEN"])
    dotenv.set_key(dotenv_file, "REFRESH_TOKEN", os.environ["REFRESH_TOKEN"])


if __name__ == '__main__':
    scheduler.add_job(refresh_token, 'interval', hours=1, minutes=55)
    scheduler.start()
    print(os.environ['APP_ACCESS_TOKEN'])
    print(os.getenv("REFRESH_TOKEN"))

    try:
        while True:
            time.sleep(5400)
    except KeyboardInterrupt:
        scheduler.shutdown()
