import os
import sys
import constants
import custom_discord
import custom_twitter
import threading
import time
import asyncio

def get_env(title: str) -> str:
	if not title in os.environ.keys():
		print("Missing env variablle: " + title, file = sys.stderr)
		sys.exit(1)
	return os.environ[title]

twitter_wait_event = threading.Event()

_discord = None
_twitter = None

tw_api_key = get_env(constants.TWITTER_API_KEY_ENV)
tw_api_secret = get_env(constants.TWITTER_API_SECRET_ENV)

tw_access_key = get_env(constants.TWITTER_ACCESS_KEY_ENV)
tw_access_secret = get_env(constants.TWITTER_ACCESS_SECRET_ENV)

ds_token = get_env(constants.DISCORD_BOT_TOKEN_ENV)

def run_twitter():
	def echo_tweet(message: str, link: str):
		asyncio.run(_discord.post_tweet(message, link))

	_twitter.connect(tw_api_key, tw_api_secret, tw_access_key, tw_access_secret)

	while not twitter_wait_event.is_set():
		_twitter.update(echo_tweet)
		twitter_wait_event.wait(10)
	twitter_wait_event.clear()
		
twitter_thread = threading.Thread(None, run_twitter, 'twitter_thread')

_twitter = custom_twitter.TweetFollower("_jstefanelli")
_discord = custom_discord.EchoClient(ds_token, lambda : twitter_thread.start())

try:
	_discord.run()
finally:
	print("[MAIN] Closing...", file = sys.stderr)
	twitter_wait_event.set()
	twitter_thread.join()

