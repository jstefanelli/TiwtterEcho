from typing import Callable
import twitter
import time
import os
import json

class TweetFollower:
	def __init__(self, api_key: str, api_secret: str, access_key: str, access_secret: str, config_file_path: str = 'twitterCfg.json'):
		self.api = twitter.Api(consumer_key = api_key,
					consumer_secret = api_secret,
					access_token_key = access_key,
					access_token_secret = access_secret,
					tweet_mode='extended')
		self.last_tweet_id = None
		self.config_path = config_file_path
		self.target_user = '_jstefanelli'

		self.load()

	def update(self, on_new_tweet: Callable[[str, str], None]):
		timeline = self.api.GetUserTimeline(screen_name="_jstefanelli", count=2, since_id = self.last_tweet_id, trim_user=True, exclude_replies=True, include_rts=True)

		for tweet in timeline:
				on_new_tweet(tweet.full_text, str(tweet.url))

		if len(timeline) > 0:
			self.last_tweet_id = timeline[0].id
			self.save()

	def load(self):
		if not os.path.exists(self.config_path):
			return

		fs = open(self.config_path, 'r')
		data = json.load(fs)
		fs.close()

		self.last_tweet_id = data.last_tweet
		self.target_user = data.target_user

	def save(self):
		fs = open(self.config_path, 'w')
		json.dump({ 'last_tweet': self.last_tweet_id, 'target_user': self.target_user }, fs)
		fs.close()



		