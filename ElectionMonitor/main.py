import os
import time
import dotenv
import tweepy as tp

from apscheduler.schedulers.background import BackgroundScheduler

dotenv.load_dotenv()
dotenv_file = dotenv.find_dotenv()


class ElectionMonitor:
    def __init__(self):
        print('initiating')
        # Authenticate API credentials
        self.client_id = os.getenv('client_id')
        self.client = tp.Client(os.getenv('APP_ACCESS_TOKEN'))
        self.client_secret = os.getenv('client_secret')
        self.redirect_uri = os.getenv('redirect_uri')
        print('authentication done')

        self.keywords = ("Nigeria election 2023", "Nigerian politics", "INEC", "APC", "PDP",
                         'labour party', 'LP', "Nigerian Election", "Nigeria gubernatorial election",
                         'Lagos governorship election', '#NigeriaDecides', 'Sanwoolu', 'GRV', "nigerian elections",
                         'nigeria vote', 'nigeria ballot', 'nigeria electoral', 'nigeria campaign', 'labour party',
                         'pdp', 'apc', 'peter obi', 'gbadebo rhodes vivour', 'sanwoolu', 'tinubu')

        with open('retweeted_tweets.txt', 'r') as f:
            self.retweeted_tweets = set(f.read().splitlines())

    def monitor(self):
        for keyword in self.keywords:
            print('Generating tweets')
            query = f'{keyword} -is:reply -is:retweet -is:quote'
            tweets = self.client.search_recent_tweets(query=query, max_results=100)
            print('tweet generated')
            for tweet in tweets.data:
                if 'RT @' not in tweet.text and tweet.id not in self.retweeted_tweets:
                    self.client.retweet(tweet.id, user_auth=False)
                    self.retweeted_tweets.add(tweet.id)
                    print('Retweeted:', tweet.id)
                    time.sleep(10)

                    # Save the updated list of retweeted ids
                    with open('retweeted_tweets.txt', 'a') as f:
                        f.write('\n'.join(str(tweet.id)))

    def refresh_token(self):
        auth = tp.OAuth2UserHandler(client_id=self.client_id,
                                    client_secret=self.client_secret,
                                    redirect_uri=self.redirect_uri,
                                    scope=['tweet.read', 'tweet.write', 'tweet.moderate.write', 'users.read',
                                           'follows.write', 'offline.access', 'space.read', 'like.write',
                                           'bookmark.write'],
                                    )

        token_data = auth.refresh_token(
            'https://api.twitter.com/2/oauth2/token', os.environ["REFRESH_TOKEN"]
        )
        os.environ['APP_ACCESS_TOKEN'] = token_data['access_token']
        os.environ['REFRESH_TOKEN'] = token_data['refresh_token']
        dotenv.set_key(dotenv_file, "APP_ACCESS_TOKEN", os.environ["APP_ACCESS_TOKEN"])
        dotenv.set_key(dotenv_file, "REFRESH_TOKEN", os.environ["REFRESH_TOKEN"])


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    election_monitor = ElectionMonitor()
    scheduler.add_job(election_monitor.monitor, 'interval', minutes=30)
    scheduler.add_job(election_monitor.refresh_token, 'interval', hours=1, minutes=55)
    scheduler.start()

    try:
        while True:
            time.sleep(1700)
    except KeyboardInterrupt:
        scheduler.shutdown()
