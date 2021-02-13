import os
import sys
import constants
import custom_discord
import custom_twitter
import threading
import asyncio

def get_env(title: str, default: str = None) -> str:
	if not title in os.environ.keys():
		if default == None:
			print("Missing env variablle: " + title, file = sys.stderr)
			sys.exit(1)
		else:
			return default
	return os.environ[title]

twitter_wait_event = threading.Event()

_discord = None
_twitter = None

tw_api_key = get_env(constants.TWITTER_API_KEY_ENV)
tw_api_secret = get_env(constants.TWITTER_API_SECRET_ENV)

tw_access_key = get_env(constants.TWITTER_ACCESS_KEY_ENV)
tw_access_secret = get_env(constants.TWITTER_ACCESS_SECRET_ENV)
tw_update_timer = int(get_env(constants.TWITTER_UPDATE_TIMER_ENV, 60))

tw_handle = get_env(constants.TWITTER_TARGET_USER_ENV, '_jstefanelli')

ds_token = get_env(constants.DISCORD_BOT_TOKEN_ENV)

def run_twitter():
	def echo_tweet(message: str, link: str):
		_discord.loop.create_task(_discord.post_tweet(message, link))

	if(tw_update_timer < constants.TWITTER_RECONNECT_CUTOFF):
		_twitter.connect(tw_api_key, tw_api_secret, tw_access_key, tw_access_secret)

	while not twitter_wait_event.is_set():
		if(tw_update_timer >= constants.TWITTER_RECONNECT_CUTOFF):
			_twitter.connect(tw_api_key, tw_api_secret, tw_access_key, tw_access_secret)

		_twitter.update(echo_tweet)

		if(tw_update_timer >= constants.TWITTER_RECONNECT_CUTOFF):
			_twitter.disconnect()
		twitter_wait_event.wait(tw_update_timer)
	twitter_wait_event.clear()
		
twitter_thread = threading.Thread(None, run_twitter, 'twitter_thread')

def on_discord_ready():
	twitter_thread.start()

_twitter = custom_twitter.TweetFollower(tw_handle)
_discord = custom_discord.EchoClient(ds_token, on_discord_ready)

try:
	sys.stdout.flush()
	_discord.run()
finally:
	print("[MAIN] Closing...", file = sys.stderr)
	twitter_wait_event.set()
	twitter_thread.join()

