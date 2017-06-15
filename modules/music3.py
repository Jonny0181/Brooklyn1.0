import discord
from discord.ext import commands
from utils.dataIO import dataIO
from utils import checks
import subprocess
import threading
import asyncio
import random
import aiohttp
import copy
import json
import re
import os

try:
	from bs4 import BeautifulSoup
except:
	BeautifulSoup = None
try:
	import youtube_dl
except:
	youtube_dl = None
try:
	if not discord.opus.is_loaded():
		discord.opus.load_opus('libopus-0.dll')
except OSError:
	opus = False
except:
	opus = None
else:
	opus = True

ytdl_options = {
    'source_address': '0.0.0.0',
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': "mp3",
    'outtmpl': '%(id)s',
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'quiet': True,
    'no_warnings': True,
    'outtmpl': "data/audio/cache/%(id)s",
    'default_search': 'auto'
}

def format(length : int):
	return (str(int(length / 3600)) + ":" if int(length / 60) >= 60 else "")+ ("0" if int(length / 60) >= 60 and int(length / 60)%60 < 10 else "") + str(int(length / 60)%60) + ":" + ("0" if length%60 < 10 else "") + str(length%60)

class Music:
	"""Music streaming"""
	def __init__(self, bot, player):
		settings_file = "data/audio/settings.json"
		
		self.bot = bot
		self.settings = dataIO.load_json(settings_file)
		self.to_queue = {}
		self.queue = {}
		self.players = {}
		self.skip_votes = {}
		self.ytdl = youtube_dl.YoutubeDL(ytdl_options)
		self.time_alone = 0
		self.repeat = 0
		
		self.settings["avconv"] = player == "avconv"
		dataIO.save_json(settings_file, self.settings)
	
	async def queue_scheduler(self):
		while self == self.bot.get_cog("Music"):
			for server in self.bot.servers:
				id = server.id
				if self.bot.is_voice_connected(server) and sum(not m.bot for m in server.me.voice_channel.voice_members) == 0:
					if self.time_alone >= 10:
						await self._disconnect(server)
					else:
						self.time_alone += 1
				else:
					self.time_alone = 0
					if id in self.queue and len(self.queue[id]) > 0:
						if id not in self.players or self.players[id].is_done():
							channel = self.bot.get_channel(self.queue[id][0]["channel"])
							if channel != None:
								await self._join(channel)
								for i in range(min(len(self.queue[id]), 2)):
									if not os.path.isfile(os.path.join("data/audio/cache", self.queue[id][i]["id"])):
										self.ytdl.extract_info(self.queue[id][i]["url"])
								self.players[id] = self._play(server)
							else:
								self._next(server)
					
					elif self.bot.is_voice_connected(server):
						await self._disconnect(server)
			
			for id in self.players:
				if self.players[id].is_playing():
					self.players[id].time_played += 1
			
			await asyncio.sleep(1)
	
	async def queuer(self):
		while self == self.bot.get_cog("Music"):
			for id in self.to_queue:
				if len(self.to_queue[id]) > 0:
					song = self.to_queue[id][0]
					await self._queue(song["queuer"], song["link"], self.bot.get_channel(song["channel"]), song["playlist"])
					self.to_queue[id].pop(0)
			await asyncio.sleep(0.1)
	
	def _dequeue_first(self, server):
		if server.id in self.queue and len(self.queue[server.id]) > 0:
			self.queue[server.id].pop(0)
	
	def _dequeue_all(self, server):
		if server.id in self.queue:
			self.queue[server.id] = []
		
		if server.id in self.to_queue:
			self.to_queue[server.id] = []
	
	async def _queue_playlist(self, author, channel, playlist):
		id = channel.server.id
		
		if id not in self.to_queue:
			self.to_queue[id] = []
		
		for song in playlist:
			self.to_queue[id].append({
				"queuer": author,
				"link": song,
				"channel": channel.id,
				"playlist": True
			})
		
		await self.bot.say("Queued " + str(len(playlist)) + " songs")
	
	def _find_playlist(self, server, name):
		file = None
		file1 = os.path.join("data/audio/playlists", name + ".txt")
		file2 = os.path.join("data/audio/playlists", server.id, name + ".txt")
		if os.path.isfile(file1):
			file = file1
		elif os.path.isfile(file2):
			file = file2
		
		return file
	
	def _next(self, server):
		if self.repeat != 0:
			song = self.queue[server.id][0]
			self._dequeue_first(server)
			self.queue[server.id].insert(min(self.repeat - 1, len(self.queue[server.id])), song)
		else:
			self._dequeue_first(server)
	
	def _end(self, player):
		server = player.server
		id = server.id
		
		if id in self.skip_votes:
			self.skip_votes[id] = []
		
		self._next(server)
		os.remove(os.path.join("data/audio/cache", player.id))
		
		for key in self.players:
			if self.players[key] == player:
				del self.players[key]
	
	def _play(self, server):
		player = server.voice_client.create_ffmpeg_player(os.path.join("data/audio/cache", self.queue[server.id][0]["id"]), options="-b:a 64k -bufsize 64k", after=self._end)
		player.volume = self.settings["volume"] / 100
		player.id = self.queue[server.id][0]["id"]
		player.time_played = 0
		player.server = server
		player.start()
		return player
	
	def _print_queue(self, server):
		msg = "Nothing queued"
		if server.id in self.queue:
			queue = self.queue[server.id]
			if len(queue) != 0:
				total_length = 0
				for song in queue:
					total_length += song["length-seconds"]
				
				progress = None
				if server.id in self.players and self.players[server.id] != None:
					time = self.players[server.id].time_played
					total_length -= time
					time_string = format(time)
					progress = int(10 * time / queue[0]["length-seconds"])
				
				msg = "```Perl\n# Now playing #\n" + queue[0]["title"] + ("\n\n# Queue (" + str(min(len(queue) - 1, 9)) + "/" + str(len(queue) - 1) + ") #\n" + "\n".join(str(i) + ". (" + queue[i]["length"] + ") " + queue[i]["title"] for i in range(1, min(len(queue), 10))) if len(queue) > 1 else "") + ("\nTotal queue length: " + format(total_length)) + ("\n\nRepeating first " + (str(self.repeat) + " songs" if self.repeat > 1 else "song") if self.repeat > 0 else "") + "```"
		
		return msg
	
	async def _join(self, channel):
		server = channel.server
		
		if self.bot.is_voice_connected(server):
			if server.voice_client.channel == channel:
				return server.voice_client
			else:
				await server.voice_client.disconnect()
		else:
			self.repeat = 0
		try:
			await self.bot.join_voice_channel(channel)
		except:
			await server.voice_client.disconnect()
			await self.bot.say("An error has occured, oh well. Use the fucking report command you fuck.")
		return server.voice_client
	
	async def _disconnect(self, server):
		self._dequeue_all(server)
		if server.voice_client != None:
			await server.voice_client.disconnect()
	
	async def _parse_playlist(self, link):
		if re.match(r'https://www.youtube.com/playlist?', link):
			links = await self._parse_yt_playlist(link)
		elif re.match(r'https://soundcloud.com/.+?/sets/', link):
			links = await self._parse_sc_playlist(link)
		else:
			return None
		
		return links
	
	async def _parse_yt_playlist(self, url):
		async with aiohttp.get(url) as response:
			soup = BeautifulSoup(await response.text(), "html.parser")
		
		buttons = soup.find_all("button", "browse-items-load-more-button")
		if len(buttons) > 0:
			button = buttons[0]
			async with aiohttp.get("https://www.youtube.com" + button["data-uix-load-more-href"]) as response:
				extra_links = re.findall(r'href=\\"\\(/watch\?v=.*?)\\u0026', await response.text())
		else:
			extra_links = []
		
		link_elements = soup.find_all("a", "pl-video-title-link")
		links = []
		
		for i in range(len(link_elements)):
			links.append("https://www.youtube.com" + link_elements[i]["href"])
		
		for i in range(0, len(extra_links), 2):
			links.append("https://www.youtube.com" + extra_links[i])
		
		return links
	
	async def _parse_sc_playlist(self, url):
		links = []
		
		async with aiohttp.get("http://api.soundcloud.com/resolve?url=" + url + "&client_id=" + self.settings["sc_client_id"]) as response:
			playlist = json.loads(await response.text())
		
		for song in playlist["tracks"]:
			links.append(song["permalink_url"])
		
		return links
	
	async def _search(self, search):
		url = "https://www.youtube.com/results?search_query=" + re.sub(r'\s+', "+", search) + "&sp=EgIQAQ%253D%253D&hl=en"
				
		async with aiohttp.get(url) as response:
			soup = BeautifulSoup(await response.text(), "html.parser")
		
		videos = soup.find_all("a", "yt-uix-tile-link")
		video_lengths = soup.find_all("span", "video-time")
		links = []
		titles = []
		lengths = []
		for i in range(min(len(videos), 5)):
			links.append("https://www.youtube.com" + videos[i]["href"])
			titles.append(videos[i].string)
			lengths.append(video_lengths[i].string)
		
		return [ links, titles, lengths ]
	
	async def _selection_menu(self, user, titles, lengths):
		msg = await self.bot.say("```Perl\n# Song selection #\n" + "\n".join(str(i + 1) + ". (" + lengths[i] + ") " + titles[i] for i in range(len(titles))) + "```")
		
		for i in range(len(titles)):
			await self.bot.add_reaction(msg, str(i + 1) + u"\u20E3")
		await self.bot.add_reaction(msg, u"\U0001F1E8")
		
		def check(reaction, reactor):
			return user == reactor
		
		res = await self.bot.wait_for_reaction(message=msg, check=check, timeout=30)
		
		await self.bot.delete_message(msg)
		
		if res == None:
			return u"\U0001F1E8"
		return str(res.reaction.emoji)[0]
	
	async def _queue(self, author, link, channel, playlist=False):
		server = channel.server
		info = self.ytdl.extract_info(link, download=False)
		
		if info == None:
			if playlist == False:
				await self.bot.say("Couldn't get video info ¯\_(ツ)_/¯")
			return
		
		length = int(info["duration"])
		if length > self.settings["max_length"]:
			if playlist == False:
				await self.bot.say("That song is way too long")
			return
		
		if server.id not in self.queue:
			self.queue[server.id] = []
		
		position = len(self.queue[server.id])
		if playlist == False:
			for i in range(len(self.queue[server.id]) - 1, 0, -1):
				if self.queue[server.id][i]["playlist"]:
					position = i
		
		if not playlist:
			await self.bot.say("Queued " + info["title"])
		
		song = {
			"title": info["title"],
			"id": info["id"],
			"url": info["webpage_url"],
			"length": format(length),
			"length-seconds": length,
			"channel": channel.id,
			"playlist": playlist,
			"queuer": author
		}
		
		if "thumbnails" in info and len(info["thumbnails"]) > 0:
			song["thumbnail"] = info["thumbnails"][0]["url"]
		
		self.queue[server.id].insert(position, song)
		
	def _player_count(self):
		count = 0
		queue = copy.deepcopy(self.queue)
		for sid in queue:
			server = self.bot.get_server(sid)
			try:
				vc = self.voice_client(server)
				if vc.audio_player.is_playing():
					count += 1
			except:
				pass
		return count
		
	@commands.command(name="mstats")
	async def audiostat_servers(self):
		"""Number of servers currently playing."""
		count = self._player_count()
		await self.bot.say("Playing music in {} servers.".format(
            count))
	
	@commands.command(pass_context=True, aliases=["play","queue"])
	async def q(self, ctx, *, search=None):
		"""Queue a song or playlist, defaults to queue."""
		server = ctx.message.server
		author = ctx.message.author
		channel = ctx.message.channel
		voice_channel = author.voice_channel
		if search == None:
			if server.id in self.queue:
				queue = self.queue[server.id]
				if len(queue) != 0:
					total_length = 0
				for song in queue:
					total_length += song["length-seconds"]
				progress = None
				if server.id in self.players and self.players[server.id] != None:
					time = self.players[server.id].time_played
					total_length -= time
					time_string = format(time)
					progress = int(10 * time / queue[0]["length-seconds"])
					num = len(queue)
					msg = discord.Embed(colour=discord.Colour.blue())
					msg.add_field(name="Now Playing:", value="{}\n{}".format(queue[0]["title"], queue[0]["url"]))
					if num > 1:
						msg.add_field(name="Next Up:", value="\n".join(str(i) + ") " + queue[i]["title"] for i in range(1, min(len(queue), 10))) if len(queue) > 1 else "")
					if num > 10:
						msg.set_footer(text="Total length of queue {} with {} more songs.".format(format(total_length), (len(queue) - 9)))
					if num == 9:
						msg.set_footer(text="Total length of queue {}.".format(format(total_length)))
					if "thumbnail" in song:
						msg.set_thumbnail(url=queue[0]["thumbnail"])
					await self.bot.say(embed=msg)
		else:
			if voice_channel == None:
				if self.bot.is_voice_connected(server):
					voice_channel = server.voice_client.channel
				else:
					await self.bot.say("You must be in a voice channel to use that command")
					return
			
			if search == "gasolina":
				await self.bot.say("kys faggot")
			
			if server.id not in self.queue:
				self.queue[server.id] = []
			
			match = re.match(r'(https?://[^\s/$.?#].[^\s]*)', search)
			if match == None:
				results = await self._search(search)
				
				selection = await self._selection_menu(author, results[1], results[2])
				if selection != u"\U0001F1E8":
					link = results[0][int(selection) - 1]
				else:
					return
			else:
				link = match.group(1)
			
			links = await self._parse_playlist(link)
			if links != None:
				await self._queue_playlist(author.id, voice_channel, links)
			else:
				await self._queue(author.id, link, voice_channel)
	
	@commands.command(pass_context=True)
	async def np(self, ctx):
		"""Shows info about the song currently playing"""
		server = ctx.message.server
		author = ctx.message.author
		
		if server.id in self.queue:
			queue = self.queue[server.id]
			if len(queue) != 0:
				song = queue[0]
				progress = None
				if server.id in self.players and self.players[server.id] != None:
					time = self.players[server.id].time_played
					time_string = format(time)
					progress = int(10 * time / song["length-seconds"])
				progress = "".join("▮" if i < progress else "▯" for i in range(20)) + " [ "+ time_string +" | " + queue[0]["length"] + " ]" if progress != None else ""
				data = discord.Embed(description="{}\n{}\n{}".format(song["title"], progress, song["url"]), color=author.color)
				if "thumbnail" in song:
					data.set_thumbnail(url=song["thumbnail"])
				data.set_author(name="Currently playing..")
				#data.set_footer(text=progress)
				await self.bot.say(embed=data)
		else:
			await self.bot.say("Nothing queued")
		
		
	
	@commands.command(pass_context=True)
	async def stop(self, ctx):
		"""Stops playing and deletes the queue"""
		server = ctx.message.server
		author = ctx.message.author
		voice_channel = author.voice_channel
		
		if voice_channel == None:
			await self.bot.say("You must be in a voice channel to use that command")
			return
		
		self._dequeue_all(server)
		if server.id in self.players:
			if self.players[server.id].is_playing():
				self.players[server.id].stop()
		else:
			await self.bot.say("Nothing to stop")
	
	@commands.command(pass_context=True)
	async def pause(self, ctx):
		"""Pauses whatever is playing"""
		server = ctx.message.server
		author = ctx.message.author
		voice_channel = author.voice_channel
		
		if voice_channel == None:
			await self.bot.say("You must be in a voice channel to use that command")
			return
		
		if server.id in self.players:
			if self.players[server.id].is_playing():
				self.players[server.id].pause()
			else:
				await self.bot.say("I'm not playing anything at the moment")
		else:
			await self.bot.say("Nothing to pause")
	
	@commands.command(pass_context=True)
	async def resume(self, ctx):
		"""Continues playing"""
		server = ctx.message.server
		author = ctx.message.author
		voice_channel = author.voice_channel
		
		if voice_channel == None:
			await self.bot.say("You must be in a voice channel to use that command")
			return
		
		if server.id in self.players:
			if not self.players[server.id].is_playing():
				self.players[server.id].resume()
			else:
				await self.bot.say("I'm playing music already")
		else:
			await self.bot.say("Nothing to resume")
	
	@commands.command(pass_context=True)
	async def skip(self, ctx):
		"""Skips a shitty song"""
		server = ctx.message.server
		user = ctx.message.author
		members = sum(not m.bot for m in server.me.voice_channel.voice_members)
		skips = len(self.skip_votes[server.id])
		votes = int(100 * skips / members)
		if votes >= 3:
			self.players[server.id].stop()
			await self.bot.say("Skipping")
		else:
			await self.bot.say(user.name + " voted to skip. " + len(skips) + " out of 3 needed")
	
	@commands.command(name="repeat")
	async def re(self, amount : int):
		"""Set amount of songs to repeat
			Set to 0 to disable repeat"""
		if amount < 0:
			self.bot.say("haha so funny, retard")
			return
		
		self.repeat = amount
		await self.bot.say("\n\nRepeating first " + (str(self.repeat) + " songs" if self.repeat > 1 else "song") if self.repeat > 0 else "Disabled repeat")
	
	@commands.command(pass_context=True)
	async def disconnect(self, ctx):
		"""Makes the bot disconnect from the voice channel"""
		server = ctx.message.server
		await self._disconnect(server)
	
	@commands.group(pass_context=True)
	async def audioset(self, ctx):
		"""Audio settings"""
		if ctx.invoked_subcommand == None:
			await send_cmd_help(ctx)
	
	@commands.command(pass_context=True, name="volume")
	async def audioset_volume(self, ctx, volume: int=None):
		"""Sets the volume (0 - 100)
		Note: volume may be set up to 200 but you may experience clipping."""
		server = ctx.message.server
		settings_file = "data/audio/settings.json"
		
		if volume is None:
			msg = "Volume is currently set to " + str(self.settings["volume"]) + "%"
		elif volume >= 0 and volume <= 200:
			self.settings["volume"] = volume
			msg = "Volume is now set to " + str(volume) + "%"
			
			if volume > 100:
				msg += "\nWarning: volume levels above 100 may result in clipping"
			
			for id in self.players:
				self.players[id].volume = volume / 100
			
			dataIO.save_json(settings_file, self.settings)
		else:
			msg = "Volume must be between 0 and 100"
		
		await self.bot.say(msg)
	
	@commands.group(pass_context=True)
	async def playlist(self, ctx):
		"""Playlist management/control"""
		if ctx.invoked_subcommand == None:
			await send_cmd_help(ctx)
	
	@playlist.command(pass_context=True, name="add")
	async def pl_add(self, ctx, name, link):
		"""Create a playlist from a playlist"""
		server = ctx.message.server
		author = ctx.message.author
		voice_channel = author.voice_channel
		
		if re.match(r'(https?://[^\s/$.?#].[^\s]*)', link) == None:
			await self.bot.say("That's not a valid link")
			return
		
		if re.match(r'(https?://[^\s/$.?#].[^\s]*)', name):
			await send_cmd_help(ctx)
			return
		
		path = os.path.join("data/audio/playlists", server.id)
		file = self._find_playlist(server, name)
		if file != None:
			await self.bot.say("That playlist already exists")
			return
		
		list = await self._parse_playlist(link)
		if list == None:
			await self.bot.say("Invalid playlist")
			return
		
		playlist = { "author": author.id, "playlist": list }
		
		if not os.path.exists(path):
			os.makedirs(path)
		dataIO.save_json(os.path.join(path, name + ".txt"), playlist)
		
		await self.bot.say("Created playlist")
	
	@playlist.command(pass_context=True, name="create")
	async def pl_create(self, ctx, name, *, links):
		"""Create a playlist from a list of links"""
		server = ctx.message.server
		author = ctx.message.author
		voice_channel = author.voice_channel
		
		if re.match(r'(https?://[^\s/$.?#].[^\s]*)', name):
			await send_cmd_help(ctx)
			return
		
		path = os.path.join("data/audio/playlists", server.id)
		file = self._find_playlist(server, name)
		if file != None:
			await self.bot.say("That playlist already exists")
			return
		
		links = links.split()
		playlist = []
		invalid_links = 0
		for link in links:
			if re.match(r'(https?://[^\s/$.?#].[^\s]*)', link) != None:
				playlist.append(link)
			else:
				invalid_links += 1
		
		if invalid_links > 0:
			await self.bot.say(str(invalid_links) + " invalid links")
		
		playlist = { "author": author.id, "playlist": links }
		
		if not os.path.exists(path):
			os.makedirs(path)
		dataIO.save_json(os.path.join(path, name + ".txt"), playlist)
		
		await self.bot.say("Created playlist")
	
	@playlist.command(pass_context=True, name="append")
	async def pl_append(self, ctx, name, *, links):
		"""Appends a list of links to a playlist"""
		server = ctx.message.server
		author = ctx.message.author
		voice_channel = author.voice_channel
		
		if re.match(r'(https?://[^\s/$.?#].[^\s]*)', name):
			await send_cmd_help(ctx)
		
		file = self._find_playlist(server, name)
		if file == None:
			await self.bot.say("That playlist doesn't exist")
			return
		
		playlist = dataIO.load_json(file)
		
		if author.id != playlist["author"]:
			await self.bot.say("You are not the author of this playlist")
			return
		
		links = links.split()
		invalid_links = 0
		for link in links:
			if re.match(r'(https?://[^\s/$.?#].[^\s]*)', link) != None:
				playlist["playlist"].append(link)
			else:
				invalid_links += 1
		
		if invalid_links > 0:
			await self.bot.say(str(invalid_links) + " invalid links")
		
		dataIO.save_json(file, playlist)
		
		await self.bot.say("Added " + str(len(links) - invalid_links) + " links to " + name)
	
	@playlist.command(pass_context=True, name="remove")
	async def pl_remove(self, ctx, name):
		"""Removes a playlist"""
		server = ctx.message.server
		author = ctx.message.author
		voice_channel = author.voice_channel
		
		file = self._find_playlist(server, name)
		if file == None:
			await self.bot.say("That playlist doesn't exist")
			return
		
		playlist = dataIO.load_json(file)
		
		if author.id != playlist["author"]:
			await self.bot.say("You are not the author of this playlist")
			return
		
		await self.bot.say("Deleted " + name)
		os.remove(file)
	
	@playlist.command(pass_context=True, name="queue")
	async def pl_queue(self, ctx, name):
		"""Queues a playlist"""
		server = ctx.message.server
		author = ctx.message.author
		voice_channel = ctx.message.author.voice_channel
		
		if voice_channel == None:
			await self.bot.say("You must be in a voice channel to use that command")
			return
		
		file = self._find_playlist(server, name)
		if file == None:
			await self.bot.say("That playlist doesn't exist")
			return
		
		playlist = dataIO.load_json(file)
		await self._queue_playlist(author.id, voice_channel, playlist["playlist"])
	
	@playlist.command(pass_context=True, name="mix")
	async def pl_mix(self, ctx, name):
		"""Queues a playlist in random order"""
		server = ctx.message.server
		author = ctx.message.author
		voice_channel = ctx.message.author.voice_channel
		
		if voice_channel == None:
			await self.bot.say("You must be in a voice channel to use that command")
			return
		
		file = self._find_playlist(server, name)
		if file == None:
			await self.bot.say("That playlist doesn't exist")
			return
		
		playlist = dataIO.load_json(file)
		random.shuffle(playlist["playlist"])
		await self._queue_playlist(author.id, voice_channel, playlist["playlist"])
	
	@playlist.command(pass_context=True, name="list")
	async def pl_list(self, ctx):
		"""Lists all available playlists"""
		server = ctx.message.server
		
		playlists_path = "data/audio/playlists"
		custom_playlists_path = os.path.join(playlists_path, server.id)
		
		msg = "```Perl\n"
		
		files = [ f for f in os.listdir(playlists_path) if os.path.isfile(os.path.join(playlists_path, f)) ]
		if len(files) > 0:
			msg += "# Default playlists #\n"
			for filename in files:
				msg += filename[:-4] + ", "
			msg = msg[:-2]
		
		if os.path.exists(custom_playlists_path):
			files = [ f for f in os.listdir(custom_playlists_path) if os.path.isfile(os.path.join(custom_playlists_path, f)) ]
			if len(files) > 0:
				msg += "\n\n# Custom playlists #\n"
				for filename in files:
					msg += filename[:-4] + ", "
				msg = msg[:-2]
		msg += "```"
		
		await self.bot.say(msg)

def check_folders():
	folders = ("data/audio", "data/audio/cache", "data/audio/playlists")
	for folder in folders:
		if not os.path.exists(folder):
			print("Creating " + folder + " folder")
			os.makedirs(folder)

def check_files():
	default = {
		"volume": 50,
		"max_length": 4500,
		"vote_enabled": True,
		"vote_threshold": 50,
		"title_status": True,
		"anvconv": False,
		"servers": {},
		"sc_client_id": "hdTx9VMgRKaZjGttAZ0GheOtJobG9eYm"
	}
	
	settings_path = "data/audio/settings.json"
	if not os.path.isfile(settings_path):
		print("Creating default audio settings.json")
		dataIO.save_json(settings_path, default)
	
	settings = dataIO.load_json(settings_path)
	for key in default:
		if key not in settings:
			settings[key] = default[key]
	dataIO.save_json(settings_path, settings)

def verify_ffmpeg_avconv():
	try:
		subprocess.call(["ffmpeg", "-version"], stdout=subprocess.DEVNULL)
	except FileNotFoundError:
		pass
	else:
		return "ffmpeg"

	try:
		subprocess.call(["avconv", "-version"], stdout=subprocess.DEVNULL)
	except FileNotFoundError:
		return False
	else:
		return "avconv"

def setup(bot):
	check_folders()
	check_files()
	
	if BeautifulSoup is None:
		raise RuntimeError("You need to run `pip3 install beautifulsoup4`")
	if youtube_dl is None:
		raise RuntimeError("You need to run `pip3 install youtube_dl`")
	if opus is False:
		raise RuntimeError("Your opus library's bitness must match your python installation's bitness. They both must be either 32bit or 64bit.")
	elif opus is None:
		raise RuntimeError("You need to install ffmpeg and opus. See \"https://github.com/Twentysix26/Red-DiscordBot/wiki/Requirements\"")
	
	player = verify_ffmpeg_avconv()
	
	if not player:
		if os.name == "nt":
			msg = "ffmpeg isn't installed"
		else:
			msg = "Neither ffmpeg nor avconv are installed"
		raise RuntimeError(msg + "\nConsult the guide for your operating system and do ALL the steps in order.\nhttps://twentysix26.github.io/Red-Docs/\n")
	
	n = Music(bot, player)
	bot.add_cog(n)
	bot.loop.create_task(n.queue_scheduler())
	bot.loop.create_task(n.queuer())
