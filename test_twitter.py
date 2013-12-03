import twitter

print twitter.get_rate_limit_status()

mentions = twitter.get_mentions()
assert len(mentions) > 1

tweets = twitter.get_tweets('markovator_dev')
assert len(tweets) > 1

print("Tests passed")
