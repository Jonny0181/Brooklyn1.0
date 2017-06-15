import asyncio
import traceback
import aiohttp
import youtube_dl
import os
import subprocess
import shutil
import discord
from discord.ext import commands
from discord.ext import commands
from discord.opus import OpusNotLoaded

py = "```py\n{}\n```"
ytdl_format_options = {"format": "bestaudio/best", "extractaudio": True, "audioformat": "mp3", "noplaylist": True, "nocheckcertificate": True, "ignoreerrors": False, "logtostderr": False, "quiet": True, "no_warnings": True, "default_search": "auto", "source_address": "0.0.0.0", "preferredcodec": "libmp3lame"}

def get_ytdl(id):
    format = ytdl_format_options
    format["outtmpl"] = "data/music/{}/%(id)s.mp3".format(id)
    return youtube_dl.YoutubeDL(format)

def clear_data(id=None):
    if id is None:
        shutil.rmtree("data/music")
    else:
        shutil.rmtree("data/music/{}".format(id))

class VoiceEntry:
    def __init__(self, message, player, data, file_url):
        self.requester = message.author
        self.channel = message.channel
        self.player = player
        self.data = data
        self.file_url = file_url

    def __str__(self):
        string = "**{}** requested by `{}`".format(self.data["title"], self.requester.display_name)
        duration = self.data["duration"]
        if duration:
            m, s = divmod(duration, 60)
            h, m = divmod(m, 60)
            length = "%02d:%02d:%02d" % (h, m, s)
            string = "{} [`{}`]".format(string, length)
        return string

class VoiceState:
    def __init__(self, bot):
        self.current = None
        self.voice = None
        self.bot = bot
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.queue = []
        # Set to 0.5 by default to prevent jumpscares
        self.volume = 0.5
        self.skip_votes = set()
        self.audio_player = self.bot.loop.create_task(self.audio_change_task())

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False
        return not self.current.player.is_done()

    @property
    def player(self):
        return self.current.player

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_change_task(self):
        while True:
            if self.current is not None:
                try:
                    os.remove(self.current.file_url)
                except:
                    log.warning("Failed to remove {}".format(self.current.file_url))
            self.play_next_song.clear()
            self.current = await self.songs.get()
            self.queue.remove(self.current)
            await self.bot.send_message(self.current.channel, "Now playing {}".format(self.current))
            self.current.player.volume = self.volume
            self.current.player.start()
            await self.play_next_song.wait()


class Music:
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}
        self.players = {}
        self.default_vol = 100

    def get_voice_state(self, server:discord.Server):
        voice_state = self.voice_states.get(server.id)
        if voice_state is None:
            voice_state = VoiceState(self.bot)
            self.voice_states[server.id] = voice_state
        return voice_state

    async def disconnect_all_voice_clients(self):
        for id in self.voice_states:
            state = self.voice_states[id]
            state.audio_player.cancel()
            await state.voice.disconnect()

    def clear_cache(self):
        # This is here because I can't call clear_data() from the main class for obvious reasons
        clear_data()

    async def _api_request(self, payload):
        url = 'https://api.spotify.com/v1/search'
        headers = {'user-agent': 'Red-cog/1.0'}
        conn = aiohttp.TCPConnector()
        session = aiohttp.ClientSession(connector=conn)
        async with session.get(url, params=payload, headers=headers) as r:
            data = await r.json()
        session.close()
        return data

    @commands.command(pass_context=True, name='spotify')
    async def _spotify(self, context, *, query: str):
        """Search for a song on Spotify
        """
        payload = {}
        payload['q'] = ''.join(query)
        payload['type'] = 'track'
        payload['limit'] = '1'
        r = await self._api_request(payload)
        if r['tracks']['total'] > 0:
            items = r['tracks']['items']
            item = items[0]
            track = item['name']
            artist = item['artists'][0]['name']
            url = item['external_urls']['spotify']
            image = item['album']['images'][0]['url']
            em = discord.Embed(title='{} - {}'.format(artist, track), url=url)
            em.set_image(url=image)
            await self.bot.say(embed=em)
        else:
            await self.bot.say('**I\'m sorry, but I couldn\'t find anything for {}.**'.format(''.join(query)))

    @commands.group(pass_context=True)
    async def samurai(self, ctx):
        """A set of commands to play music from a stream."""
        # If a subcommand isn't called
        if not ctx.invoked_subcommand:
            e = discord.Embed(description="""b!lm

A set of commands to play music from a stream.

Commands:
  disconnect Leaves the voice channel and stops the stream
  pause      Pauses the music
  volume     Allows the user to change the volume of the bot
  check_vol  Checks the volume for the servers voice channel that it's in
  resume     Unpauses the music
  playin     Has the bot join a voice channel and also starts the stream from...

Type b!help command for more info on a command.
You can also type b!help category for more info on a category.""")
            e.set_author(name="Help for {}'s command group {}.".format(self.bot.user.name, ctx.command), icon_url=ctx.message.server.me.avatar_url)
            e.set_thumbnail(url=ctx.message.server.me.avatar_url)
            self.bot.say(embed=e)

    @samurai.command(name="start", pass_context=True)
    async def join_vc_and_play_stream(self, ctx, *, channel: discord.Channel = None):
        """Has the bot join a voice channel and also starts the stream from listen.moe"""
        try:
            # Because the bot needs a channel to join, if it's None we'll just return the function assuming they're not in a voice channel
            if channel is None:
                # Set it to the voice channel for the member who triggers the command
                channel = ctx.message.author.voice.voice_channel
            # Get the VoiceClient object
            voice_client = await self.bot.join_voice_channel(channel)
            # Set it to stereo and set sample rate to 48000
            voice_client.encoder_options(sample_rate=48000, channels=2)
            # Set the user agent and create the player
            player = voice_client.create_ffmpeg_player("https://www.youtube.com/watch?v=ZJE8dbW10h4", headers={"User-Agent": "Pixie (https://github.com/GetRektByMe/Pixie)"})
            # Set default player volume
            player.volume = self.default_vol / 100
            # Start the player
            player.start()
            # Be a tsun while telling the user that you joined the channel
            await self.bot.say("```xl\nI-I didn't join {0.channel} because you told me to...```".format(voice_client))
            # Add to the dict of server ids linked to objects
            self.players.update({ctx.message.server.id: player})
        # Here we account for our bot not having enough perms or for the bot region being a bit dodgy
        except asyncio.TimeoutError:
            await self.bot.say("```xl\nSorry, I timed out trying to join!```")
        # This here pms the owner of the bot by the owner id in the setup file telling them if Opus isn't loaded
        except OpusNotLoaded:
            # Get the member object (here we assume the owner is in a server that the bot can see)
            member = discord.utils.get(self.bot.get_all_members(), id="146040787891781632")
            # Send a message to tell the owner that the Opus isn't loaded
            await self.bot.send_message(member, "```xl\nOpus library not loaded.```")
        # Account for if the bot is in a channel on the server already
        except discord.ClientException:
            await self.bot.say("```xl\nSorry, I'm already in a voice channel on this server!```")

    @samurai.command(name="pause", pass_context=True)
    async def pause_audio_stream(self, ctx):
        """Pauses the music"""
        # Get the player object from the dict using the server id as a key
        player = self.players[ctx.message.server.id]
        # Pause the bot's stream
        player.pause()
        # Tell the user who executed the command that the bot's stream is paused
        await self.bot.say("```xl\nStream has been paused```")

    @samurai.command(name="resume", pass_context=True)
    async def resume_audio_stream(self, ctx):
        """Unpauses the music"""
        # Get the player object from the dict using the server id as a key
        player = self.players[ctx.message.server.id]
        # Resume the bots stream
        player.resume()
        # Tell the user who executed the command that the stream is resumed
        await self.bot.say("```xl\nStream has been resumed```")

    @samurai.command(name="volume", pass_context=True)
    async def change_volume(self, ctx, volume: int = 100):
        """Allows the user to change the volume of the bot"""
        # Get the player object from the dict using the server id as a key
        player = self.players[ctx.message.server.id]
        # We divide volume by 100 because for some reason discord works on 1.0 as 100%
        player.volume = volume / 100
        # Check if the player volume is above 200
        if (player.volume * 100) > 200:
            # Tell the user their input isn't allowed
            await self.bot.say("```xl\nSorry, the max input is 200```")
            # Return the function as we don't want to set the volume
            return
        # Tell the user what the current volume now is
        await self.bot.say("```py\nVolume has been changed to: {}```".format(str(volume)))

    @samurai.command(name="check_vol", pass_context=True)
    async def check_volume(self, ctx):
        """Checks the volume for the servers voice channel that it's in"""
        # Get the player object from the dict using the server id as a key
        player = self.players[ctx.message.server.id]
        # Have the bot say the volume
        await self.bot.say("```xl\nThe current volume is: {}```".format(player.volume * 100))

    @samurai.command(name="disconnect", pass_context=True)
    async def leave_vc(self, ctx):
        """Leaves the voice channel and stops the stream"""
        # Get the voice and player objects using the server id as a key
        voice = self.bot.voice_client_in(ctx.message.server)
        # Account for voice being None due to voice_client_in returning None if the bot isn't in a voice channel
        if voice is None:
            await self.bot.say("```xl\nSorry it doesn't seem like I'm in a voice channel in this server!```")
            return
        # Disconnect everything from the voice client object that the server is accessing
        await voice.disconnect()
        # Remove from the dictionaries since we no longer need to access this
        self.players.pop(ctx.message.server.id)

    @commands.command(pass_context=True)
    async def summon(self, ctx):
        """Summons the bot to your current voice channel"""
        if ctx.message.author.voice_channel is None:
            await self.bot.say("You are not in a voice channel")
            return
        state = self.get_voice_state(ctx.message.server)
        if state.voice is None:
            try:
                state.voice = await self.bot.join_voice_channel(ctx.message.author.voice_channel)
                await self.bot.server_voice_state(ctx.message.server.me, deafen=True)
            except:
                await self.bot.say(":x: An error occured! Please give me the correct permissions to server deafen myself.".format(self.bot.command_prefix))
        else:
            await state.voice.move_to(ctx.message.author.voice_channel)
        return True
    
    @commands.command(pass_context=True)
    async def play(self, ctx, *, song:str):
        """Plays a song, searches youtube or gets video from youtube url"""
        await self.bot.send_typing(ctx.message.channel)
        song = song.strip("<>")
        try:
            state = self.get_voice_state(ctx.message.server)
            if state.voice is None:
                success = await ctx.invoke(self.summon)
                if not success:
                    return
            ytdl = get_ytdl(ctx.message.server.id)
            try:
                song_info = ytdl.extract_info(song, download=False, process=False)
                if "url" in song_info:
                    if song_info["url"].startswith("ytsearch"):
                        song_info = ytdl.extract_info(song_info["url"], download=False, process=False)
                    if "entries" in song_info:
                        url = song_info["entries"][0]["url"]
                    else:
                        url = song_info["url"]
                    url = "https://youtube.com/watch?v={}".format(url)
                else:
                    url = song
                song_info = ytdl.extract_info(url, download=True)
                id = song_info["id"]
                title = song_info["title"]
                file_url = "data/music/{}/{}.mp3".format(ctx.message.server.id, id)
                await asyncio.sleep(5)
                player = state.voice.create_ffmpeg_player(file_url, stderr=subprocess.PIPE, after=state.toggle_next)
            except Exception as e:
                await self.bot.say("An error occurred while processing this request: {}".format(py.format("{}: {}\n{}".format(type(e).__name__, e, traceback.format_exc()))))
                return
            player.volume = state.volume
            entry = VoiceEntry(ctx.message, player, song_info, file_url)
            await self.bot.say("Enqueued {}".format(entry))
            await state.songs.put(entry)
            state.queue.append(entry)
        except Exception as e:
            await self.bot.say(traceback.format_exc())

    @commands.command(pass_context=True, no_pm=True)
    async def volume(self, ctx, amount:int):
        """Sets the volume"""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.volume = amount / 100
            state.volume = amount / 100
            await self.bot.say("Set the volume to `{:.0%}`".format(player.volume))
        else:
            await self.bot.say("Nothing is playing!")

    @commands.command(pass_context=True)
    async def disconnect(self, ctx):
        """Disconnects the bot from the voice channel"""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.stop()
        try:
            state.audio_player.cancel()
            del self.voice_states[ctx.message.server.id]
            await state.voice.disconnect()
        except:
            if ctx.message.server.me.voice_channel:
                try:
                    await ctx.message.server.voice_client.disconnect()
                except:
                    log.error("Bot failed to force the disconnection from a voice channel!\n{}".format(traceback.format_exc()))
                    pass
        await self.bot.say("Disconnected from the voice channel")

    @commands.command(pass_context=True)
    async def skip(self, ctx):
        """Vote to skip a song. Server mods, the server owner, bot developers, and the song requester can skip the song"""
        state = self.get_voice_state(ctx.message.server)
        if not state.is_playing():
            await self.bot.say("Nothing is playing!")
            return
        voter = ctx.message.author
        if voter == state.current.requester:
            await self.bot.say("Requester requested to skip the song, skipping song...")
            state.skip()
        elif voter == ctx.message.server.owner:
            await self.bot.say("Server owner requested to skip the song, skipping song...")
            state.skip()
        elif voter.id not in state.skip_votes:
            votes_needed = 3
            members = []
            for member in state.voice.channel.voice_members:
                if not member.bot:
                    members.append(member)
            if len(members) < 3:
                votes_needed = len(members)
            state.skip_votes.add(voter.id)
            total_votes = len(state.skip_votes)
            if total_votes >= votes_needed:
                await self.bot.say("Skip vote passed, skipping song...")
                state.skip()
            else:
                await self.bot.say("Skip vote added, currently at `{}/{}`".format(total_votes, votes_needed))
        else:
            await self.bot.say("You have already voted to skip this song.")

    @commands.command(pass_context=True)
    async def pause(self, ctx):
        """Pauses the player"""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.pause()
            await self.bot.say("Song paused")
        else:
            await self.bot.say("Nothing is playing!")

    @commands.command(pass_context=True)
    async def resume(self, ctx):
        """Resumes the player"""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.resume()
            await self.bot.say("Song resumed")
        else:
            await self.bot.say("Nothing is playing!")

    @commands.command(pass_context=True)
    async def queue(self, ctx):
        """Displays the song queue"""
        state = self.get_voice_state(ctx.message.server)
        songs = state.queue
        if len(songs) == 0 and not state.current:
            await self.bot.say("Nothing is in the queue!")
        else:
            current_song = "Now playing: {}".format(state.current)
            if len(songs) != 0:
                songs = "{}\n\n{}".format(current_song, "\n".join([str(song) for song in songs]))
            else:
                songs = "{}".format(current_song)
            await self.bot.say(songs)

def setup(bot):
    bot.add_cog(Music(bot))
