import discord
import sys
import os
import json
from typing import Callable

class EchoClient(discord.Client):
	def __init__(self, token: str, start: Callable[[], None], config_file_path: str = 'discordCfg.json'):
		discord.Client.__init__(self)
		self.start_cb = start
		self.token = token
		self.target_channels = []
		self.config_file_path = config_file_path
		self.loaded = False

	async def on_ready(self):
		print('[DISCORD] Ready...', file = sys.stdout)
		try:
			cached_user = self.user
			if cached_user is not None:
				self.cached_user = cached_user
			
			if not self.loaded:
				await self.load()
				if self.start_cb != None:
					self.start_cb()
				self.loaded = True
		except Exception as ex:
			print('[DISCORD] Exception "on_ready"', str(ex), file = sys.stderr)

	async def load(self):
		print("[DISCORD] Loading...", file = sys.stdout)
		if os.path.exists(self.config_file_path):
			fs = open(self.config_file_path, 'r')

			data = json.load(fs)

			fs.close()

			if 'channels' in data and data['channels'] != None:
				for channelId in data['channels']:
					ch = self.get_channel(channelId)
					if ch != None:
						self.target_channels.append(ch)

	async def save(self):
		print("[DISCORD] Saving...", file = sys.stdout)
		cfg = { 'channels': [] }
		for channel in self.target_channels:
			cfg['channels'].append(channel.id)

		fs = open(self.config_file_path, "w")

		json.dump(cfg, fs, indent = "\t")

		fs.close()

	async def on_error(self, event: str, args, kwargs):
		print("[DISCORD] Error", event, file = sys.stderr)
		

	async def exec_start_message(self, message: discord.Message):
		if message.channel in self.target_channels:
			await message.reply("Already working")

		self.target_channels.append(message.channel)
		await self.save()
		await message.add_reaction('👍')

	async def exec_stop_message(self, message: discord.Message):
		if not message.channel in self.target_channels:
			await message.reply("Not monitoring")

		self.target_channels.remove(message.channel)
		await self.save()
		await message.add_reaction('👍')

	async def on_message(self, message: discord.Message):
		if len(message.mentions) >= 1 and message.mentions[0].id != self.cached_user.id:
			return

		if 'start' in message.content:
			await self.exec_start_message(message)

		if 'stop' in message.content:
			await self.exec_stop_message(message)

	async def post_tweet(self, tweet: str, url: str) -> bool:
		if tweet == None or len(tweet.strip()) == 0:
			return False
		
		tweet = tweet.strip()
		tmp_channels = self.target_channels.copy()

		for channel in tmp_channels:
			await channel.send(tweet)

		return True

	def run(self):
		discord.Client.run(self, self.token)
		