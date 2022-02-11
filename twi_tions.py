"""Needed twitter api functions for telegram bot."""
from twitter import *
import config

t = Twitter(auth = OAuth(
    config.access_key,
    config.access_secret, 
    config.customer_key,
    config.costomer_secret
    ))

def send_tweet(this) -> None:
    """Sends tweets to twitter account."""
    tweet = t.statuses.update(status = this)
    print(f'Tweeted\n{tweet}\nto your account.')

