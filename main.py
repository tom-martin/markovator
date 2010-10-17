import logging
from django.utils import simplejson as json

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import twitter
import status
from markovate import Markovator
from status_endpoint import StatusHandler

import twitter_settings

def create_markovated_tweet(tweets, max_length):
    tweets_texts = map(lambda t: t['text'].strip(), tweets)
    markovator = Markovator()
    markovator.parse_sentences(tweets_texts)
    markovation = markovator.markovate()

    count = 0
    while len(markovation) > max_length or markovation in tweets_texts:
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


class RepliesProcessor(webapp.RequestHandler):
    def get(self):
        self.response.out.write('<html><body>')

        since_id = status.get_reply_since_id()

        if since_id:
            mentions = twitter.get_mentions(since_id)
        else:
            mentions = twitter.get_mentions()

        self.response.out.write("<pre>" + str(since_id) + ":" + str(mentions) + "</pre>")

        if not mentions:
            return

        for mention in reversed(mentions):
            self.response.out.write("<p>" + str(mention['id']) + " | " + mention['user']['screen_name'] + " protected("+ str(mention['user']['protected']) + "): " + mention['text'] +"</p>")

        self.reply_to_user(mentions[-1]['user'])

        twitter.follow_user(mentions[-1]['user']['screen_name'])
        status.set_reply_since_id(mentions[-1]['id'])

        self.response.out.write('</body></html>')

    def reply_to_user(self, user):
        if user['protected']:
            self.response.out.write("@" + user['screen_name'] + " sorry, I can't process protected users :(")
            return

        screen_name = user['screen_name']

        self.response.out.write("<h1>" + screen_name + "</h1>")

        tweets = filter_tweets(twitter.get_tweets(screen_name))

        if len(tweets) <= 1:
            self.response.out.write("<p>Not enough tweets</p>")
            twitter.post_tweet("@" + screen_name + " sorry, you need to tweet more :(")
            return

        tweet_prefix = '@' + screen_name + ' markovated: '
        ideal_tweet_length = 140 - len(tweet_prefix)
        
        best_tweet = create_markovated_tweet(tweets, ideal_tweet_length)
        
        if best_tweet != None:
            twitter.post_tweet(tweet_prefix + best_tweet)
            self.response.out.write('<p>' + tweet_prefix + best_tweet + '</p>' + '(' + str(len(tweet_prefix + best_tweet)) + ')')
        else:
            self.response.out.write('<p>Could not generate reply</p>')

class TweetsProcessor(webapp.RequestHandler):
    def get(self):

        # Just get the latest tweets
        tweets = twitter.get_timeline_tweets(800)
        tweets = filter_tweets(tweets)
        tweets = filter(lambda t:not t['user']['screen_name'] == twitter_settings.screen_name, tweets)

        if len(tweets) <= 1:
            self.response.out.write('<p>Could not generate tweet (not enough eligible tweets)</p>')
            return

        best_tweet = create_markovated_tweet(tweets, 140)

        if best_tweet != None:
            twitter.post_tweet(best_tweet)
            self.response.out.write('<p>' + best_tweet + '</p>' + '(' + str(len(best_tweet)) + ')')
        else:
            self.response.out.write('<p>Could not generate tweet</p>')

application = webapp.WSGIApplication([('/cron/processReplies/', RepliesProcessor),
                                      ('/status/', StatusHandler),
                                      ('/cron/processTweets/', TweetsProcessor)],
                                       debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

