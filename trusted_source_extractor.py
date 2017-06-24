from credentials import *
from datetime import datetime, timedelta
from tweepy import OAuthHandler, API, TweepError
import pandas as pd


class TwitterTrustedSourceExtractor(object):

    # https://en.wikipedia.org/wiki/News_agency
    SOURCES = [
        # News agencies
        'AFP',            # agency france presse
        'AP',             # assicoated press
        'business',       # bloomberg
        'dpa',            # deutsche presse agentur
        'dowjones',
        'epaphotos',      # european pressphoto agency
        'pa',             # press association
        'reuters',
        
        # News channels
        'DailyMailUK',   # daily mail UK
        'CNN',
        'MSNBC',
        'FoxNews',
        'HuffPost',
        'detikcom',

        # Breaking news
        'BreakingNews',
        'BBCBreaking',
        'cnnbrk',
        'WSJbreakingnews',
        'ReutersLive',
        'CBSTopNews',
        'SkyNewsBreak',
        'ABCNewsLive',
        'TWCBreaking',
        'CBSTopNews',
        'BuzzFeedNews',

        # Other
        'whitehouse',
        'wsj',   # wall street journal
        'wired',
        'techcrunch',
        'espn',
        'time',

        # CNN extensions
        # 'cnnbrk',
        # 'MSNBC',
        # 'CNNPolitics',
        # 'cnni',
        # 'CNNnewsroom',

        # Fox News extensions
        # 'FoxNews',
        # 'foxheadlines',
        # 'foxnewspolitics',
        # 'FOX4',
    ]

    N_TWEETS_PER_REQUEST = 100
    TWEET_STORAGE = []
    TWEET_DATAFRAME = None
    N_DAYS_HISTORY = 10

    def __init__(self):
        auth = OAuthHandler(TWITTER_CONS_KEY, TWITTER_CONS_SECRET)
        auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
        self.API = API(auth)
        self.from_time = datetime.today() - timedelta(days=self.N_DAYS_HISTORY)


    def get_filtered_tweet(self, tweet):
        filtered = {
            'id': tweet.id,
            'author': tweet.author.screen_name,
            'text': tweet.text.encode('utf-8'),
            'favorite_count': tweet.favorite_count,
            'retweet_count': tweet.retweet_count,
            'created_at': tweet.created_at
        }
        return filtered


    def extract_tweets_from_a_source(self, source):
        if '@' not in source:
            source = '@' + source

        extracted_tweets = []
        try:
            print "Extracting %s..." % source
            max_twitter_id = None
            while True:
                tw = self.API.user_timeline(screen_name=source, count=self.N_TWEETS_PER_REQUEST, max_id=max_twitter_id)
                if not len(tw):
                    break

                extracted_tweets += [self.get_filtered_tweet(t) for t in tw]
                earliest_tweet_date = extracted_tweets[-1]['created_at']
                if earliest_tweet_date < self.from_time:
                    break

                max_twitter_id = extracted_tweets[-1]['id'] - 1
        except TweepError:
            print "Error processing", source

        print "\textracted %d tweets for %s" % (len(extracted_tweets), source)
        self.TWEET_STORAGE += extracted_tweets
        return extracted_tweets


    def get_tweets_as_dataframe(self):
        self.TWEET_DATAFRAME = pd.DataFrame(self.TWEET_STORAGE)
        return self.TWEET_DATAFRAME


    def save_tweets_to_csv(self, filename):
        self.TWEET_DATAFRAME.to_csv(filename, index=False)


    def extract_tweets_from_all(self):
        for source in self.SOURCES:
            self.extract_tweets_from_a_source(source)
        return self.TWEET_STORAGE


if __name__ == '__main__':
    t = TwitterTrustedSourceExtractor()
    # t.extract_tweets_from_a_source('AJELive')
    t.extract_tweets_from_all()
    t.get_tweets_as_dataframe()
    t.save_tweets_to_csv('tweetz.csv')
