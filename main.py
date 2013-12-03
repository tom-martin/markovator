import json

import twitter
import file_system_status as status
from markovate import Markovator

import twitter_settings
import sys
import random

def create_markovated_tweet(tweets, max_length, unwanted_markovations=[]):
    tweets_texts = map(lambda t: t['text'].strip(), tweets)
    markovator = Markovator()
    markovator.parse_sentences(tweets_texts)
    markovation = markovator.markovate()

    unwanted_markovations.extend(tweets_texts)

    count = 0
    while len(markovation) > max_length or markovation in unwanted_markovations:
        markovation = markovator.markovate()
        count += 1
        if count > 20:
            return None

    return markovation

def filter_tweets(tweets):
    return filter_out_mentions(filter_out_links(filter_out_bad_words(tweets)))

def filter_out_mentions(tweets):
    # TODO This is to be polite, we could keep tweets that mention people that follow us
    return filter(lambda t:not '@' in t['text'], tweets)

def filter_out_links(tweets):
    # Links are almost guaranteed to ruin the context of the markovation
    return filter(lambda t:not 'http://' in t['text'].lower(), tweets)

def filter_out_bad_words(tweets):
    # Might be offensive/inappropriate for humour
    return filter(lambda t:not ('cancer' in t['text'].lower() or
                                'r.i.p' in t['text'].lower() or
                                'RIP' in t['text']), tweets)

def reply_to_user(user, app_status):
    if user['protected']:
        print("@" + user['screen_name'] + " sorry, I can't process protected users :(")
        return

    screen_name = user['screen_name']

    print(screen_name)

    tweets = filter_tweets(twitter.get_tweets(screen_name, True))

    if len(tweets) <= 1:
        print("Not enough tweets")
        fail_reply = "@" + screen_name + " sorry, you need to tweet more (or tweet less @ mentions and links) :("
        twitter.post_tweet(fail_reply)
        app_status['latest_reply'] = fail_reply
        return

    tweet_prefix = '@' + screen_name + ' markovated: '
    ideal_tweet_length = 140 - len(tweet_prefix)
    
    best_tweet = create_markovated_tweet(tweets, ideal_tweet_length)
    
    if best_tweet != None:
        tweet = tweet_prefix + best_tweet
        twitter.post_tweet(tweet)
        encoded = unicode(tweet).encode('utf-8')
        print(encoded + '(' + str(len(encoded)) + ')')
        app_status['latest_reply'] = encoded
    else:
        print('<p>Could not generate reply</p>')
        app_status['latest_reply'] = 'Could not generate'

def process_replies():
    app_status = status.load()
    since_id = app_status.get('reply_since_id', -1)

    if since_id:
        mentions = twitter.get_mentions(since_id)
    else:
        mentions = twitter.get_mentions()

    print(str(len(mentions))+" mentions since "+str(since_id))

    mentions.reverse()
    for mention in mentions:
        twitter.follow_user(mentions[-1]['user']['screen_name'])
        reply_to_user(mention['user'], app_status)

        app_status['reply_since_id'] = mention['id']
        app_status['latest_user_replied_to'] = mention['user']['screen_name']

        # Save after each one so if we crash we don't resend replies
        status.save(app_status)

def produce_next_tweet(app_status):
    app_status = status.load()
    # Just get the latest tweets
    tweets = twitter.get_timeline_tweets(800)
    tweets = filter_tweets(tweets)
    tweets = filter(lambda t:not t['user']['screen_name'] == twitter_settings.screen_name, tweets)

    if len(tweets) <= 1:
        print('Could not generate tweet (not enough eligible tweets)')
        app_status['latest_tweet'] = 'Could not generate tweet (not enough eligible tweets)'
        return

    recent_tweets = twitter.get_tweets(twitter_settings.screen_name, True)

    best_tweet = create_markovated_tweet(tweets, 140, map(lambda t: t['text'].strip(), recent_tweets))

    if best_tweet != None:
        twitter.post_tweet(best_tweet)
        encoded = unicode(best_tweet).encode('utf-8')
        print(encoded + '(' + str(len(encoded)) + ')')
        app_status['latest_tweet'] =  encoded;
    else:
        print('Could not generate tweet')
        app_status['latest_tweet'] = 'Could not generate tweet'

    status.save(app_status)

print("Started")
process_replies()
if random.randrange(240) == 0:
    produce_next_tweet(status)
print("Finished")

