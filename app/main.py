import os
import sys
import constants
import custom_discord
import custom_twitter

def get_env(title: str) -> str:
	if not title in os.environ.keys():
		print("Missing env variablle: " + title, file = sys.stderr)
		sys.exit(1)
	return os.environ[title]


tw_api_key = get_env(constants.TWITTER_API_KEY_ENV)
tw_api_secret = get_env(constants.TWITTER_API_SECRET_ENV)

tw_access_key = get_env(constants.TWITTER_ACCESS_KEY_ENV)
tw_access_secret = get_env(constants.TWITTER_ACCESS_SECRET_ENV)

ds_token = get_env(constants.DISCORD_BOT_TOKEN_ENV)

