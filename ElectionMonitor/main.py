import os
import time
import dotenv
import tweepy as tp

from apscheduler.schedulers.background import BackgroundScheduler

dotenv.load_dotenv()


class ElectionMonitor:
    def __init__(self):
        print('initiating')
        # Authenticate API credentials
        self.client = tp.Client(os.getenv('APP_ACCESS_TOKEN'))
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
            tweets = self.client.search_recent_tweets(query=keyword, max_results=100)
            print('tweet generated')
            for tweet in tweets.data:
                print(tweet)
                print(tweet.author_id)
                # print(tweet.author)
                if 'RT @' not in tweet.text and tweet.id not in self.retweeted_tweets:
                    self.client.retweet(tweet.id, user_auth=False)
                    self.retweeted_tweets.add(tweet.id)
                    print('Retweeted:', tweet.id)
                    time.sleep(10)

            # Save the updated list of retweeted ids
            with open('retweeted_tweets.txt', 'w') as f:
                f.write('\n'.join(str(tweet_id) for tweet_id in self.retweeted_tweets))


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    election_monitor = ElectionMonitor()
    scheduler.add_job(election_monitor.monitor(), 'interval', minutes=30)
    scheduler.start()

    try:
        while True:
            time.sleep(1700)
    except KeyboardInterrupt:
        scheduler.shutdown()
