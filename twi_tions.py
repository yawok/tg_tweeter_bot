"""Needed twitter api functions for telegram bot."""
from dotenv import load_dotenv
import os
from tweepy import *
import config

load_dotenv()

auth = OAuth1UserHandler(
        os.getenv("consumer_key"),
        os.getenv("consumer_secret"),
        os.getenv("access_token"),
        os.getenv("access_token_secret")
    )

api = API(auth)

def send_tweet(this, reply_id, imgs=[]) -> int:
    """Sends tweets and images."""
    media_ids = []
    if imgs:
        for img in imgs:
            res = api.media_upload(img)
            media_ids.append(res.media_id)

    tweet = api.update_status(status=this, media_ids=media_ids, in_reply_to_status_id=reply_id, auto_populate_reply_metadata=True)

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


def get_tweet_txt(tweet_id) -> str:
    """Return the text of a tweet."""
    text = api.get_status(tweet_id).text

    return text
