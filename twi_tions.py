"""Needed twitter api functions for telegram bot."""
from tweepy import *
import config

auth = OAuth1UserHandler( 
    config.consumer_key,
    config.consumer_secret,
    config.access_token,
    config.access_token_secret
    )

api = API(auth)

def send_tweet(this) -> int:
    """Sends tweets to twitter account."""
    tweet = api.update_status(status = this)
    print(f'Tweeted\n{tweet.id}\nto your account.')
    
    return tweet.id


def retweet(tweet_id) -> int:
    """Retweet a tweet."""
    api.retweet(tweet_id)

    return 1


def like(tweet_id) -> int:
    """Likes a tweet"""
    api.create_favorite(tweet_id)

    return 1
