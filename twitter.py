import logging
import time
from django.utils import simplejson as json

import oauth2 as oauth

import httplib2

import twitter_settings

def get_mentions(since=-1):
    client = oauth.Client(twitter_settings.consumer, twitter_settings.token)

    if since > -1:
        resp, content = client.request("http://api.twitter.com/1/statuses/mentions.json?count=20&since_id=" + str(since), "GET")
    else:
        resp, content = client.request("http://api.twitter.com/1/statuses/mentions.json?count=200", "GET")

    return json.loads(content)

def get_tweets(screen_name):
    h = httplib2.Http(timeout=30)
    resp, content = h.request('http://api.twitter.com/1/statuses/user_timeline.json?screen_name=' + screen_name + '&count=200&trim_user=true', "GET")

    return json.loads(content)

def get_timeline_tweets(count):
    client = oauth.Client(twitter_settings.consumer, twitter_settings.token)

    resp, content = client.request('http://api.twitter.com/1/statuses/friends_timeline.json?count=' + str(count), "GET")

    return json.loads(content)

def get_timeline_tweets_since(since_id=-1):
    client = oauth.Client(twitter_settings.consumer, twitter_settings.token)
    tweets = []

    if since_id < 0:
        resp, content = client.request('http://api.twitter.com/1/statuses/friends_timeline.json', "GET")
        tweets.extend(json.loads(content))
    else:
        # TODO 1 or 0?
        current_page = 0
        while len(tweets) == 0 or not since_id >= max(map(lambda t:int(t['id']), tweets)):
            resp, content = client.request('http://api.twitter.com/1/statuses/friends_timeline.json?count=2&page=' + str(current_page), "GET")
            new_tweets = json.loads(content)
            if len(new_tweets) == 0:
                break
            tweets.extend(new_tweets)
            current_page += 1
            
    return tweets 

def post_tweet(text):
    client = oauth.Client(twitter_settings.consumer, twitter_settings.token)
    resp, content = client.request("http://api.twitter.com/1/statuses/update.json", "POST", "status=" + text)

    return content

def follow_user(screen_name):
    client = oauth.Client(twitter_settings.consumer, twitter_settings.token)
    resp, content = client.request("http://api.twitter.com/1/friendships/create.json", "POST", "screen_name=" + screen_name)

    return content
