from discord.ext import commands
import datetime
from utils.dataIO import fileIO, dataIO
import discord
import asyncio
import os
from utils import checks
from random import choice, randint

inv_settings = {"embed": False, "Channel": None, "toggleedit": False, "toggledelete": False, "toggleuser": False, "toggleroles": False,
                "togglevoice": False,
                "toggleban": False, "togglejoin": False, "toggleleave": False, "togglechannel": False, "toggleserver": False}
timef = datetime.datetime.now().strftime("%A, %B %-d %Y at %-I:%M%p").replace("PM", "pm").replace("AM", "am")
css = "```css\n{}```"

class ModLog:
    def __init__(self, bot):
        self.bot = bot
        self.direct = "data/modlogset/settings.json"
        self.ignore_list = dataIO.load_json("data/modlogset/ignorelist.json")

    @checks.botcom()
    @commands.group(name='modlogtoggle', pass_context=True, no_pm=True)
    async def modlogtoggles(self, ctx):
        """toggle which server activity to log"""
        if ctx.invoked_subcommand is None:
            db = fileIO(self.direct, "load")
            server = ctx.message.server
            e = discord.Embed(description="""b!modlogtoggle

toggle which server activity to log

Commands:
  leave   toggles notofications when a member leaves the server.
  join    toggles notofications when a member joins the server.
  roles   toggle notifications when roles change
  voice   toggle notifications when voice status change
  delete  toggle notifications when a member delete theyre message
  server  toggles notofications when the server updates.
  ban     toggle notifications when a user is banned
  edit    toggle notifications when a member edits theyre message
  channel toggles channel update logging for the server.
  user    toggle notifications when a user changes his profile

Type b!help command for more info on a command.
You can also type b!help category for more info on a category.""")
            e.set_author(name="Help for {}'s command group {}.".format(self.bot.user.name, ctx.command), icon_url=ctx.message.server.me.avatar_url)
            e.set_thumbnail(url=ctx.message.server.me.avatar_url)
            await self.bot.say(embed=e)

    @checks.botcom()
    @commands.group(pass_context=True, no_pm=True)
    async def modlogset(self, ctx):
        """Change modlog settings"""
        if ctx.invoked_subcommand is None:
            e = discord.Embed(description="""b!modlogset

Change modlog settings

Commands:
  status   Shows modlog settings for the server.
  disable  disables the modlog
  ignore   Sets a channel for modlog to ignore.
  embed    Enables or disables embed modlog.
  unignore Removes channel from ignore list
  channel  Set the channel to send notifications too

Type b!help command for more info on a command.
You can also type b!help category for more info on a category.""")
            e.set_author(name="Help for {}'s command group {}.".format(self.bot.user.name, ctx.command), icon_url=ctx.message.server.me.avatar_url)
            e.set_thumbnail(url=ctx.message.server.me.avatar_url)
            await self.bot.say(embed=e)
            
    @modlogset.command(pass_context=True)
    async def status(self, ctx):
        """Shows modlog settings for the server."""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        try:
            e = discord.Embed(title="Setting for {}".format(server.name), colour=discord.Colour.blue())
            e.add_field(name="Delete", value=str(db[ctx.message.server.id]['toggledelete']))
            e.add_field(name="Edit", value=str(db[ctx.message.server.id]['toggleedit']))
            e.add_field(name="Roles", value=str(db[ctx.message.server.id]['toggleroles']))
            e.add_field(name="User", value=str(db[ctx.message.server.id]['toggleuser']))
            e.add_field(name="Voice", value=str(db[ctx.message.server.id]['togglevoice']))
            e.add_field(name="Ban", value=str(db[ctx.message.server.id]['toggleban']))
            e.add_field(name="Join", value=str(db[ctx.message.server.id]['togglejoin']))
            e.add_field(name="Leave", value=str(db[ctx.message.server.id]['toggleleave']))
            e.add_field(name="Channel", value=str(db[ctx.message.server.id]['togglechannel']))
            e.add_field(name="Server", value=str(db[ctx.message.server.id]['toggleserver']))
            e.set_thumbnail(url=server.icon_url)
            await self.bot.say(embed=e)
        except KeyError:
            await self.bot.say("No settings for this server.")
            
    @modlogset.command(pass_context=True, name="ignore", no_pm=True)
    async def _ignore(self, ctx, channel: discord.Channel=None):
        """Sets a channel for modlog to ignore.
        
        Defaults to current channel."""
        current_ch = ctx.message.channel
        if not channel:
            if current_ch.id not in self.ignore_list["CHANNELS"]:
                self.ignore_list["CHANNELS"].append(current_ch.id)
                dataIO.save_json("data/modlogset/ignorelist.json", self.ignore_list)
                await self.bot.say("Channel added to ignore list.")
            else:
                await self.bot.say("Channel already in ignore list.")
        else:
            if channel.id not in self.ignore_list["CHANNELS"]:
                self.ignore_list["CHANNELS"].append(channel.id)
                dataIO.save_json("data/modlogset/ignorelist.json", self.ignore_list)
                await self.bot.say("Channel added to ignore list.")
            else:
                await self.bot.say("Channel already in ignore list.")

    @modlogset.command(pass_context=True, name="unignore", no_pm=True)
    async def _unignore(self, ctx, channel: discord.Channel=None):
        """Removes channel from ignore list
        Defaults to current one"""
        current_ch = ctx.message.channel
        if not channel:
            if current_ch.id in self.ignore_list["CHANNELS"]:
                self.ignore_list["CHANNELS"].remove(current_ch.id)
                dataIO.save_json("data/modlogset/ignorelist.json", self.ignore_list)
                await self.bot.say("This channel has been removed from the ignore list.")
            else:
                await self.bot.say("This channel is not in the ignore list.")
        else:
            if channel.id in self.ignore_list["CHANNELS"]:
                self.ignore_list["CHANNELS"].remove(channel.id)
                dataIO.save_json("data/modlogset/ignorelist.json", self.ignore_list)
                await self.bot.say("Channel removed from ignore list.")
            else:
                await self.bot.say("That channel is not in the ignore list.")

    @modlogset.command(name='channel', pass_context=True, no_pm=True)
    async def _channel(self, ctx):
        """Set the channel to send notifications too"""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if ctx.message.server.me.permissions_in(ctx.message.channel).send_messages:
            if server.id in db:
                db[server.id]['Channel'] = ctx.message.channel.id
                fileIO(self.direct, "save", db)
                await self.bot.say("Channel changed.")
                return
            if not server.id in db:
                db[server.id] = inv_settings
                db[server.id]["Channel"] = ctx.message.channel.id
                fileIO(self.direct, "save", db)
                await self.bot.say("I will now send toggled modlog notifications here")
        else:
            return
            
    @modlogset.command(pass_context=True, no_pm=True)
    async def embed(self, ctx):
        """Enables or disables embed modlog."""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if db[server.id]["embed"] == False:
            db[server.id]["embed"] = True
            fileIO(self.direct, "save", db)
            await self.bot.say("Enabled embed modlog.")
        elif db[server.id]["embed"] == True:
            db[server.id]["embed"] = False
            fileIO(self.direct, "save", db)
            await self.bot.say("Disabled embed modlog.")

    @modlogset.command(pass_context=True, no_pm=True)
    async def disable(self, ctx):
        """disables the modlog"""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if not server.id in db:
            await self.bot.say("Server not found, use modlogset to set a channnel")
            return
        del db[server.id]
        fileIO(self.direct, "save", db)
        await self.bot.say("I will no longer send modlog notifications here")

    @modlogtoggles.command(pass_context=True, no_pm=True)
    async def edit(self, ctx):
        """toggle notifications when a member edits theyre message"""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if db[server.id]["toggleedit"] == False:
            db[server.id]["toggleedit"] = True
            fileIO(self.direct, "save", db)
            await self.bot.say("Edit messages enabled")
        elif db[server.id]["toggleedit"] == True:
            db[server.id]["toggleedit"] = False
            fileIO(self.direct, "save", db)
            await self.bot.say("Edit messages disabled")
            
    @modlogtoggles.command(pass_context=True, no_pm=True)
    async def join(self, ctx):
        """toggles notofications when a member joins the server."""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if db[server.id]["togglejoin"] == False:
            db[server.id]["togglejoin"] = True
            fileIO(self.direct, "save", db)
            await self.bot.say("Enabled join logs.")
        elif db[server.id]['togglejoin'] == True:
            db[server.id]['togglejoin'] = False
            fileIO(self.direct, 'save', db)
            await self.bot.say("Disabled join logs.")

    @modlogtoggles.command(pass_context=True, no_pm=True)
    async def server(self, ctx):
        """toggles notofications when the server updates."""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if db[server.id]["toggleserver"] == False:
            db[server.id]["toggleserver"] = True
            fileIO(self.direct, "save", db)
            await self.bot.say("Enabled server logs.")
        elif db[server.id]['toggleserver'] == True:
            db[server.id]['toggleserver'] = False
            fileIO(self.direct, 'save', db)
            await self.bot.say("Disabled server logs.")

    @modlogtoggles.command(pass_context=True, no_pm=True)
    async def channel(self, ctx):
        """toggles channel update logging for the server."""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if db[server.id]["togglechannel"] == False:
            db[server.id]["togglechannel"] = True
            fileIO(self.direct, "save", db)
            await self.bot.say("Enabled channel logs.")
        elif db[server.id]['togglechannel'] == True:
            db[server.id]['togglechannel'] = False
            fileIO(self.direct, 'save', db)
            await self.bot.say("Disabled channel logs.")
            
    @modlogtoggles.command(pass_context=True, no_pm=True)
    async def leave(self, ctx):
        """toggles notofications when a member leaves the server."""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if db[server.id]["toggleleave"] == False:
            db[server.id]["toggleleave"] = True
            fileIO(self.direct, "save", db)
            await self.bot.say("Enabled leave logs.")
        elif db[server.id]['toggleleave'] == True:
            db[server.id]['toggleleave'] = False
            fileIO(self.direct, 'save', db)
            await self.bot.say("Disabled leave logs.")

    @modlogtoggles.command(pass_context=True, no_pm=True)
    async def delete(self, ctx):
        """toggle notifications when a member delete theyre message"""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if db[server.id]["toggledelete"] == False:
            db[server.id]["toggledelete"] = True
            fileIO(self.direct, "save", db)
            await self.bot.say("Delete messages enabled")
        elif db[server.id]["toggledelete"] == True:
            db[server.id]["toggledelete"] = False
            fileIO(self.direct, "save", db)
            await self.bot.say("Delete messages disabled")

    @modlogtoggles.command(pass_context=True, no_pm=True)
    async def user(self, ctx):
        """toggle notifications when a user changes his profile"""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if db[server.id]["toggleuser"] == False:
            db[server.id]["toggleuser"] = True
            fileIO(self.direct, "save", db)
            await self.bot.say("User messages enabled")
        elif db[server.id]["toggleuser"] == True:
            db[server.id]["toggleuser"] = False
            fileIO(self.direct, "save", db)
            await self.bot.say("User messages disabled")

    @modlogtoggles.command(pass_context=True, no_pm=True)
    async def roles(self, ctx):
        """toggle notifications when roles change"""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if db[server.id]["toggleroles"] == False:
            db[server.id]["toggleroles"] = True
            fileIO(self.direct, "save", db)
            await self.bot.say("Role messages enabled")
        elif db[server.id]["toggleroles"] == True:
            db[server.id]["toggleroles"] = False
            fileIO(self.direct, "save", db)
            await self.bot.say("Role messages disabled")

    @modlogtoggles.command(pass_context=True, no_pm=True)
    async def voice(self, ctx):
        """toggle notifications when voice status change"""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if db[server.id]["togglevoice"] == False:
            db[server.id]["togglevoice"] = True
            fileIO(self.direct, "save", db)
            await self.bot.say("Voice messages enabled")
        elif db[server.id]["togglevoice"] == True:
            db[server.id]["togglevoice"] = False
            fileIO(self.direct, "save", db)
            await self.bot.say("Voice messages disabled")

    @modlogtoggles.command(pass_context=True, no_pm=True)
    async def ban(self, ctx):
        """toggle notifications when a user is banned"""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if db[server.id]["toggleban"] == False:
            db[server.id]["toggleban"] = True
            fileIO(self.direct, "save", db)
            await self.bot.say("Ban messages enabled")
        elif db[server.id]["toggleban"] == True:
            db[server.id]["toggleban"] = False
            fileIO(self.direct, "save", db)
            await self.bot.say("Ban messages disabled")

    async def on_message_delete(self, message):
        server = message.server
        db = fileIO(self.direct, "load")
        if not server.id in db:
            return
        if db[server.id]['toggledelete'] == False:
            return
        if message.author.bot == True:
            return
        if message.channel.id in self.ignore_list["CHANNELS"]:
            return
        channel = db[server.id]["Channel"]
        time = datetime.datetime.now()
        fmt = '%H:%M:%S'
        msg = discord.Embed(title="{0.name} message has been delete in {1.name}!".format(message.author, message.channel), colour=discord.Colour.blue())
        msg.add_field(name="Content:", value="```css\n{}```".format(message.content), inline=False)
        msg.set_thumbnail(url=message.author.avatar_url)
        msg.set_footer(text=datetime.datetime.now().strftime("%A, %B %-d %Y at %-I:%M%p").replace("PM", "pm").replace("AM", "am"))
        await self.bot.send_message(server.get_channel(channel), embed=msg)
        
    async def on_member_join(self, member):
        server = member.server
        db = fileIO(self.direct, 'load')
        if not server.id in db:
            return
        if db[server.id]['togglejoin'] == False:
            return
        channel = db[server.id]["Channel"]
        time = datetime.datetime.now()
        fmt = '%H:%M:%S'
        users = len([e.name for e in server.members])
        msg = discord.Embed(description="Welcome {} to the server!\nThere is now {} users!".format(member.name, users), colour=discord.Colour.green())
        msg.set_author(name=member.name, icon_url=member.avatar_url)
        msg.set_footer(text=datetime.datetime.now().strftime("%A, %B %-d %Y at %-I:%M%p").replace("PM", "pm").replace("AM", "am"))
        await self.bot.send_message(server.get_channel(channel), embed=msg)
        
    async def on_member_remove(self, member):
        server = member.server
        db = fileIO(self.direct, 'load')
        if not server.id in db:
            return
        if db[server.id]['toggleleave'] == False:
            return
        channel = db[server.id]["Channel"]
        time = datetime.datetime.now()
        fmt = "%H:%M:%S"
        users = len([e.name for e in server.members])
        msg = discord.Embed(description="Fairwell! {} left the server!\nThere is now {} users!".format(member.name, users), colour=discord.Colour.green())
        msg.set_author(name=member.name, icon_url=member.avatar_url)
        msg.set_footer(text=datetime.datetime.now().strftime("%A, %B %-d %Y at %-I:%M%p").replace("PM", "pm").replace("AM", "am"))
        await self.bot.send_message(server.get_channel(channel), embed=msg)

    async def on_channel_update(self, before, after):
        server = before.server
        db = fileIO(self.direct, 'load')
        if not server.id in db:
            return
        if db[server.id]['togglechannel'] == False:
            return
        if before.channel.id in self.ignore_list["CHANNELS"]:
            return
        channel = db[server.id]["Channel"]
        time = datetime.datetime.now()
        fmt = "%H:%M:%S"
        msg = ""
        if before.name != after.name:
            if before.type == discord.ChannelType.voice:
                msg = discord.Embed(colour=discord.Color.blue())
                msg.title = "Voice channel name update!"
                msg.add_field(name="Before:", value="```css\n{}```".format(before.name), inline=False)
                msg.add_field(name="After:", value="```css\n{}```".format(after.name), inline=False)
                msg.set_footer(text=timef)
                msg.set_thumbnail(url="http://www.hey.fr/fun/emoji/twitter/en/icon/twitter/565-emoji_twitter_speaker_with_three_sound_waves.png")
                await self.bot.send_message(server.get_channel(channel), embed=msg)
            if before.type == discord.ChannelType.text:
                msg = discord.Embed(colour=discord.Color.blue())
                msg.title = "Text channel name update!"
                msg.add_field(name="Before:", value=css.format(before.name), inline=False)
                msg.add_field(name="After:", value=css.format(after.name), inline=False)
                msg.set_thumbnail(url="https://s-media-cache-ak0.pinimg.com/originals/27/18/77/27187782801d15f756a27156105d1233.png")
                msg.set_footer(text=timef)
                await self.bot.send_message(server.get_channel(channel), embed=msg)
        if before.topic != after.topic:
            msg = discord.Embed(colour=discord.Colour.blue())
            msg.title = "Channel topic has been updated! Channel {}".format(before.name)
            msg.add_field(name="Before:", value=css.format(before.topic), inline=False)
            msg.add_field(name="After:", value=css.format(after.topic), inline=False)
            msg.set_thumbnail(url="https://s-media-cache-ak0.pinimg.com/originals/27/18/77/27187782801d15f756a27156105d1233.png")
            msg.set_footer(text=timef)
            await self.bot.send_message(server.get_channel(channel), embed=msg)
        if before.position != after.position:
            if before.type == discord.ChannelType.voice:
                msg = discord.Embed(colour=discord.Colour.blue())
                msg.set_thumbnail(url="http://www.hey.fr/fun/emoji/twitter/en/icon/twitter/565-emoji_twitter_speaker_with_three_sound_waves.png")
                msg.title = "Voice channel position update! Channel {}".format(before.name)
                msg.add_field(name="Before:", value=css.format(before.position))
                msg.add_field(name="After:", value=css.format(after.position))
                msg.set_footer(text=timef)
                await self.bot.send_message(server.get_channel(channel), embed=msg)
            if before.type == discord.ChannelType.text:
                msg = discord.Embed(colour=discord.Colour.blue())
                msg.set_thumbnail(url="https://s-media-cache-ak0.pinimg.com/originals/27/18/77/27187782801d15f756a27156105d1233.png")
                msg.title = "Text channel position update! Channel {}".format(before.name)
                msg.add_field(name="Before:", value=css.format(before.position))
                msg.add_field(name="After:", value=css.format(after.position))
                msg.set_footer(text=timef)
                await self.bot.send_message(server.get_channel(channel), embed=msg)
        if before.bitrate != after.bitrate:
            msg = discord.Embed(colour=discord.Colour.blue())
            msg.set_thumbnail(url="http://www.hey.fr/fun/emoji/twitter/en/icon/twitter/565-emoji_twitter_speaker_with_three_sound_waves.png")
            msg.title = "Voice Channel bitrate update! Channel {}".format(before.name)
            msg.add_field(name="Before:", value=css.format(before.bitrate))
            msg.add_field(name="After:", value=css.format(after.bitrate))
            await sef.bot.send_message(server.get_channel(channel), embed=msg)

    async def on_message_edit(self, before, after):
        server = before.server
        db = fileIO(self.direct, "load")
        if not server.id in db:
            return
        if db[server.id]['toggleedit'] == False:
            return
        if before.content == after.content:
            return
        if before.author.bot == True:
            return
        if before.channel.id in self.ignore_list["CHANNELS"]:
            return
        channel = db[server.id]["Channel"]
        msg = discord.Embed(colour=discord.Color.blue())
        msg.title = "{} has edited a message in {}".format(before.author.display_name, before.channel)
        msg.add_field(name="Before Message:", value=css.format(before.content), inline=False)
        msg.add_field(name="After Message:", value=css.format(after.content), inline=False)
        msg.set_footer(text=timef)
        msg.set_thumbnail(url=before.author.avatar_url)
        await self.bot.send_message(server.get_channel(channel), embed=msg)
        
    async def on_channel_delete(self, channel):
        server = channel.server
        db = fileIO(self.direct, "load")
        if not server.id in db:
            return
        if db[server.id]['togglechannel'] == False:
            return
        channel = db[server.id]["Channel"]
        msg = discord.Embed(colour=discord.Colour.blue())
        msg.title = "A channel was deleted!"
        msg.add_field(name="Name:", value=css.format(channel.name))
        msg.set_footer(text=timef)
        await self.bot.send_message(server.get_channel(channel), embed=msg)

    async def on_channel_create(self, channel):
        server = channel.server
        db = fileIO(self.direct, "load")
        if not server.id in db:
            return
        if db[server.id]['togglechannel'] == False:
            return
        channel = db[server.id]["Channel"]
        msg = discord.Embed(colour=discord.Colour.blue())
        msg.title = "A channel was created!"
        msg.add_field(name="Name:", value=css.format(channel.name))
        msg.set_footer(text=timef)
        await self.bot.send_message(server.get_channel(channel), embed=msg)

    async def on_server_update(self, before, after):
        server = before
        db = fileIO(self.direct, "load")
        if not server.id in db:
            return
        if db[server.id]['toggleserver'] == False:
            return
        channel = db[server.id]["Channel"]
        time = datetime.datetime.now()
        fmt = '%H:%M:%S'
        if before.name != after.name:
            msg = discord.Embed(colour=discord.Colour.blue())
            msg.title = "Server name update!"
            msg.add_field(name="Before:", value=css.format(before.name), inline=False)
            msg.add_field(name="After:", value=css.format(after.name), inline=False)
            msg.set_thumbnail(url="http://www.emoji.co.uk/files/twitter-emojis/symbols-twitter/11164-globe-with-meridians.png")
            msg.set_footer(text=timef)
            await self.bot.send_message(server.get_channel(channel), embed=msg)
        if before.region != after.region:
            msg = discord.Embed(colour=discord.Colour.blue())
            msg.title = "Server region update!"
            msg.add_field(name="Before:", value=css.format(before.region), inline=False)
            msg.add_field(name="After:", value=css.format(after.region), inline=False)
            msg.set_thumbnail(url="http://www.emoji.co.uk/files/twitter-emojis/symbols-twitter/11164-globe-with-meridians.png")
            msg.set_footer(text=timef)
            await self.bot.send_message(server.get_channel(channel), embed=msg)

    async def on_voice_state_update(self, before, after):
        server = before.server
        db = fileIO(self.direct, "load")
        if not server.id in db:
            return
        if db[server.id]['togglevoice'] == False:
            return
        if before.bot == True:
            return
        channel = db[server.id]["Channel"]
        msg = "Action taken:\n"
        if before.voice_channel != after.voice_channel:
            msg += "User: {0} <{0.id}>\n".format(before)
            if not before.voice_channel:
                msg += "Voice Channel Join: {0.name} <{0.id}>\n".format(after.voice_channel)
            elif before.voice_channel and after.voice_channel:
                msg += "Voice Channel Before: {0.name} <{0.id}>\n".format(before.voice_channel)
                msg += "Voice Channel After: {0.name} <{0.id}\n>".format(after.voice_channel)
            elif before.voice_channel and not after.voice_channel:
                msg += "Voice Channel Leave: {0.name} <{0.id}>\n".format(before.voice_channel)
        if before.mute != after.mute:
            if not before.mute:
                msg += "Server Muted: {0} <{0.id}>\n".format(after)
            else:
                msg += "Server Un-Muted: {0} <{0.id}>\n".format(after)
        if before.deaf != after.deaf:
            if after.deaf:
                msg += "Server Deafened: {0} <{0.id}>\n".format(after)
            else:
                msg += "Server Un-Deafened: {0} <{0.id}>\n".format(after)
        if before.self_mute != after.self_mute:
            if not before.self_mute:
                msg += "Muted: {0} <{0.id}>\n".format(after)
            else:
                msg += "Un-Muted: {0} <{0.id}>\n".format(after)
        if before.self_deaf != after.self_deaf:
            if after.self_deaf:
                msg += "Deafened: {0} <{0.id}>\n".format(after)
            else:
                msg += "Un-Deafened: {0} <{0.id}>\n".format(after)
        if msg:
            e = discord.Embed(description=msg, colour=discord.Colour.blue())
            e.set_thumbnail(url=before.avatar_url)
            e.set_footer(text=timef)
            e.set_author(name="{}'s voice status has updated!".format(before))
            await self.bot.send_message(server.get_channel(channel), embed=e)

    async def on_member_update(self, before, after):
        server = before.server
        db = fileIO(self.direct, "load")
        if not server.id in db:
            return
        if db[server.id]['toggleuser'] == False:
            return
        if before.author.bot == True:
            return
        channel = db[server.id]["Channel"]
        if before.nick != after.nick:
            msg = discord.Embed(colour=discord.Color.blue())
            msg.title = "{}'s nickname has changed".format(before.name)
            msg.add_field(name="Before:", value=css.format(before.nick))
            msg.add_field(name="After:", value=css.format(after.nick))
            msg.set_footer(text=timef)
            msg.set_thumbnail(url=after.avatar_url)
            await self.bot.send_message(server.get_channel(channel), embed=msg)

    async def on_member_update(self, before, after):
        server = before.server
        db = fileIO(self.direct, "load")
        if not server.id in db:
            return
        if db[server.id]['toggleuser'] and db[server.id]['toggleroles'] == False:
            return
        channel = db[server.id]["Channel"]
        time = datetime.datetime.now()
        fmt = '%H:%M:%S'
        if before.roles != after.roles:
            msg = discord.Embed(colour=discord.Color.blue())
            msg.title = "{}'s roles have changed!".format(before.name)
            msg.add_field(name="Before:", value=css.format(", ".join([r.name for r in before.roles])), inline=False)
            msg.add_field(name="After:", value=css.format(", ".join([r.name for r in after.roles])), inline=False)
            msg.set_footer(text=timef)
            msg.set_thumbnail(url=after.avatar_url)
            await self.bot.send_message(server.get_channel(channel), embed=msg)
            
    async def on_server_role_create(self, role):
        server = role.server
        db = fileIO(self.direct, "load")
        if not server.id in db:
            return
        if db[server.id]["toggleserver"] == False:
            return
        channel = db[server.id]["Channel"]
        msg = discord.Embed(description="A role was created and the roles name is {}".format(role.name), colour=discord.Colour.green())
        msg.set_author(name="A role was created!")
        msg.set_footer(text=timef)
        await self.bot.send_message(server.get_channel(channel), embed=msg)
        
    async def on_server_role_delete(self, role):
        server = role.server
        db = fileIO(self.direct, "load")
        if not server.id in db:
            return
        if db[server.id]["toggleserver"] == False:
            return
        channel = db[server.id]["Channel"]
        msg = discord.Embed(description="A role was deleted and the roles name was {}".format(role.name), colour=discord.Colour.red())
        msg.set_author(name="A role was deleted!")
        msg.set_footer(text=timef)
        await self.bot.send_message(server.get_channel(channel), embed=msg)
        
                                    
    async def on_member_ban(self, member):
        server = member.server
        db = fileIO(self.direct, "load")
        if not server.id in db:
            return
        if db[server.id]["toggleban"] == False:
            return
        channel = db[server.id]["Channel"]
        msg = discord.Embed(description="{1.name}#{1.discriminator} has been banned!".format(member), colour=discord.Colour.red())
        msg.set_thumbnail(url=member.avatar_url)
        msg.set_footer(text=timef)
        await self.bot.send_message(server.get_channel(channel), embed=msg)

def check_folder():
    if not os.path.exists('data/modlogset'):
        print('Creating data/modlogset folder...')
        os.makedirs('data/modlogset')


def check_file():
    f = 'data/modlogset/settings.json'
    if not fileIO(f, 'check'):
        print('Creating default settings.json...')
        fileIO(f, 'save', {})
        
def check_file():
    f = 'data/modlogset/ignorelist.json'
    if not fileIO(f, 'check'):
        print('Creating default settings.json...')
        fileIO(f, 'save', {})

def setup(bot):
    check_folder()
    check_file()
    bot.add_cog(ModLog(bot))
