import os
import sys
import constants
import custom_discord
import custom_twitter
import custom_http
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
_httpserver = None

tw_api_key = get_env(constants.TWITTER_API_KEY_ENV)
tw_api_secret = get_env(constants.TWITTER_API_SECRET_ENV)

tw_access_key = get_env(constants.TWITTER_ACCESS_KEY_ENV)
tw_access_secret = get_env(constants.TWITTER_ACCESS_SECRET_ENV)

ds_token = get_env(constants.DISCORD_BOT_TOKEN_ENV)

http_port = int(get_env(constants.HTTP_PORT_ENV, '80'))
http_redirect_target = get_env(constants.HTTP_REDIRECT_TARGET_ENV)

def run_twitter():
	def echo_tweet(message: str, link: str):
		asyncio.run(_discord.post_tweet(message, link))

	_twitter.connect(tw_api_key, tw_api_secret, tw_access_key, tw_access_secret)

	while not twitter_wait_event.is_set():
		_twitter.update(echo_tweet)
		twitter_wait_event.wait(10)
	twitter_wait_event.clear()

def run_http():
	print("[MAIN] Serving HTTP requests on port: ", http_port)
	_httpserver.start()
		
twitter_thread = threading.Thread(None, run_twitter, 'twitter_thread')
http_thread = threading.Thread(None, run_http, 'http_thread')

def on_discord_ready():
	twitter_thread.start()
	http_thread.start()

def on_code(code: str) -> bool:
	return True

_twitter = custom_twitter.TweetFollower("_jstefanelli")
_discord = custom_discord.EchoClient(ds_token, on_discord_ready)
_httpserver = custom_http.CustomHTTPServer(http_port, on_code, http_redirect_target)

try:
	sys.stdout.flush()
	_discord.run()
finally:
	print("[MAIN] Closing...", file = sys.stderr)
	twitter_wait_event.set()
	_httpserver.stop()
	twitter_thread.join()

