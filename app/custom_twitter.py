from typing import Callable
import twitter
import sys
import os
import json

class TweetFollower:
	def __init__(self, target_user = None, config_file_path: str = 'twitterCfg.json'):
		self.last_tweet_id = None
		self.config_path = config_file_path
		self.load()
		if target_user != None:
			self.target_user = target_user

		if self.target_user == None:
			raise Exception("No user defined")

	def connect(self, api_key: str, api_secret: str, access_key: str, access_secret: str):
		self.api = twitter.Api(consumer_key = api_key,
					consumer_secret = api_secret,
					access_token_key = access_key,
					access_token_secret = access_secret,
					tweet_mode='extended')

	def disconnect(self):
		self.api = None

	def gen_tweet_url(tweet: twitter.Status):
		return "https://twitter.com/" + str(tweet.user.screen_name) + "/status/" + str(tweet.id)

	def update(self, on_new_tweet: Callable[[str, str], None]):
		timeline = self.api.GetUserTimeline(screen_name=self.target_user, count=10, since_id = self.last_tweet_id, trim_user=False, exclude_replies=False, include_rts=True)

		if len(timeline) > 0:
			print("[TWITTER] Received", len(timeline), "tweets", file = sys.stderr)
			print("[TWITTER] Last tweet id:", self.last_tweet_id, file = sys.stderr)
			timeline.reverse()
			for tweet in timeline:
				on_new_tweet(tweet.full_text, TweetFollower.gen_tweet_url(tweet))
				self.last_tweet_id = tweet.id

		if len(timeline) > 0:
			self.save()

	def load(self):
		if not os.path.exists(self.config_path):
			return

		fs = open(self.config_path, 'r')
		data = json.load(fs)
		fs.close()

		self.last_tweet_id = data['last_tweet']

	def save(self):
		fs = open(self.config_path, 'w')
		json.dump({ 'last_tweet': self.last_tweet_id }, fs)
		fs.close()



		