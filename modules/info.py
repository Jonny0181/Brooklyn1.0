import discord
import random
import os
import asyncio
import psutil
import ast
import aiohttp
import logging
import datetime
import urllib.request
from datetime import datetime
import time
import copy
from utils.dataIO import dataIO, fileIO
from discord.ext import commands
from random import choice, randint
from utils.chat_formatting import pagify, box

starttime = time.time()
DB_VERSION = 2
wrap = "```py\n{}```"
user_id = "3691279"
patreon_link = "_brooklyn"

class Info:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def channels(self, ctx):
        """Lists all servers channels."""

        list = "\n".join([c.name for c in ctx.message.server.channels])
        for page in pagify(list, ["\n"], shorten_by=7, page_length=2000):
            await self.bot.say(box(page))

    @commands.command(pass_context=True)
    async def textchannels(self, ctx):
        """Lists only servers text channels."""

        list = "\n".join(
            [c.name for c in ctx.message.server.channels if c.type == discord.ChannelType.text])
        for page in pagify(list, ["\n"], shorten_by=7, page_length=2000):
            await self.bot.say(box(page))

    @commands.command(pass_context=True)
    async def rolecount(self, ctx):
        """Shows server role count."""

        list = len([x.name for x in ctx.message.server.role_hierarchy if x.name != "@everyone"])
        await self.bot.say(box(list, "Prolog"))

    @commands.command(pass_context=True)
    async def roles(self, ctx):
        """Lists all servers roles."""

        list = "\n".join([x.name for x in ctx.message.server.role_hierarchy if x.name != "@everyone"])
        for page in pagify(list, ["\n"], shorten_by=7, page_length=2000):
            await self.bot.say(box(page))

    @commands.command(pass_context=True)
    async def botlist(self, ctx):
        """Lists all bots in the server."""

        list = "\n".join([m.name for m in ctx.message.server.members if m.bot])
        for page in pagify(list, ["\n"], shorten_by=7, page_length=2000):
            await self.bot.say(box(page))

    @commands.command(pass_context=True)
    async def usercount(self, ctx):
        """Shows server member count."""

        list = len([m.name for m in ctx.message.server.members if not m.bot])
        await self.bot.say(box(list, "Prolog"))

    @commands.command(pass_context=True)
    async def voicechannels(self, ctx):
        """Lists only servers voice channels."""

        list = "\n".join(
            [c.name for c in ctx.message.server.channels if c.type == discord.ChannelType.voice])
        for page in pagify(list, ["\n"], shorten_by=7, page_length=2000):
            await self.bot.say(box(page))

    @commands.command()
    async def patreon(self):
        """Shows Patreon stats."""
        with aiohttp.ClientSession() as session:
            async with session.get('http://api.patreon.com/user/{}'.format(user_id)) as resp:
                data = await resp.json()
                if len(data["linked"]) > 0:
                    patrons = str(data["linked"][0]["patron_count"])
                    pledge = str(data["linked"][0]["pledge_sum"])[:-2]
                else:
                    patrons = "N/A"
                    pledge = "N/A"
        await self.bot.say("{0} patrons, ${1} per month. Become a patron: <https://www.patreon.com/{2}>".format(
            patrons, pledge, patreon_link))

    @commands.command(pass_context=True)
    async def ghstatus(self, ctx): # !!ghstatus
        await self.bot.send_typing(ctx.message.channel)
        st = urllib.request.urlopen('https://status.github.com/api/last-message.json')
        st = str(st.read())
        st = st[2:]
        st = st[:len(st) - 1]
        st = ast.literal_eval(st)
        status = st['status']
        desc = st['body']
        timestamp = st['created_on']
        color = discord.Color.default()
        if status == "good":
            color = discord.Color.green()
            status = "Good :white_check_mark:"
        elif status == "minor":
            status = "Minor :hourglass:"
            color = discord.Color.gold()
        elif status == "major":
            color = discord.Color.red()
            status = "Major :x:"
        embed = discord.Embed(color=color)
        embed.title="GitHub Status"
        embed.set_footer(text="Last updated " + timestamp)
        embed.add_field(name="Status", value=status)
        embed.add_field(name="Description", value=desc)
        embed.set_thumbnail(url="https://maxcdn.icons8.com/iOS7/PNG/75/Logos/github_copyrighted_filled-75.png")
        await self.bot.say(embed=embed)

    @commands.command()
    async def shard(self):
        """Shows shard number."""
        await self.bot.say("Shard {} out of {} shards.".format(str(self.bot.shard_id + 1), self.bot.shard_count))

    @commands.command(pass_context=True)
    async def inrole(self, ctx, *, rolename):
        """Check members in the role specified."""
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        server = ctx.message.server
        message = ctx.message
        channel = ctx.message.channel
        await self.bot.send_typing(ctx.message.channel)
        therole = discord.utils.find(lambda r: r.name.lower() == rolename.lower(), ctx.message.server.roles)
        if therole is not None and len([m for m in server.members if therole in m.roles]) < 50:
            await asyncio.sleep(1) #taking time to retrieve the names
            server = ctx.message.server
            member = discord.Embed(description="**{1} users found in the {0} role.**\n".format(rolename, len([m for m in server.members if therole in m.roles])), colour=discord.Colour(value=colour))
            member.add_field(name="Users", value="\n".join(m.display_name for m in server.members if therole in m.roles))
            await self.bot.say(embed=member)
        elif len([m for m in server.members if therole in m.roles]) > 50:
            awaiter = await self.bot.say("Getting Member Names")
            await asyncio.sleep(1)
            await self.bot.edit_message(awaiter, " :raised_hand: Woah way too many people in **{0}** Role, **{1}** Members found\n".format(rolename,  len([m.mention for m in server.members if therole in m.roles])))
        else:
            embed=discord.Embed(description="**Role was not found**", colour=discord.Colour(value=colour))
            await self.bot.say(embed=embed)

    @commands.command(pass_context=True, no_pm=True)
    async def avatar(self, ctx, *, user: discord.Member=None):
        """Retrieves a users avatar."""
        author = ctx.message.author
        if not user:
            user = author
        data = discord.Embed(colour=user.colour)
        data.set_image(url=user.avatar_url)
        data.set_author(name="Avatar for {}!".format(user.name), icon_url=user.avatar_url)
        data.set_footer(text=datetime.datetime.now().strftime("%A, %B %-d %Y at %-I:%M%p").replace("PM", "pm").replace("AM", "am"))
        await self.bot.say(embed=data)

    @commands.command(pass_context=True, aliases=["ri"])
    async def roleinfo(self, ctx, rolename):
        """Get your role info !!!
        If dis dun work first trry use "" quotes on te role"""
        channel = ctx.message.channel
        server = ctx.message.server
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        await self.bot.send_typing(ctx.message.channel)
        therole = discord.utils.find(lambda r: r.name.lower() == rolename.lower(), ctx.message.server.roles)
        since_created = (ctx.message.timestamp - therole.created_at).days
        created_on = "{} days ago".format(since_created)
        if therole is None:
            await bot.say(':no_good: That role cannot be found. :no_good:')
            return
        if therole is not None:
            perms = iter(therole.permissions)
            perms_we_have = ""
            perms_we_dont = ""
            for x in perms:
                if "True" in str(x):
                    perms_we_have += "<:vpGreenTick:257437292820561920> {0}\n".format(str(x).split('\'')[1])
                else:
                    perms_we_dont += ("<:vpRedTick:257437215615877129> {0}\n".format(str(x).split('\'')[1]))
            msg = discord.Embed(description=":raised_hand:***`Collecting Role Stats`*** :raised_hand:",
            colour=therole.color)
            if therole.color is None:
                therole.color = discord.Colour(value=colour)
            lolol = await self.bot.say(embed=msg)
            em = discord.Embed(colour=therole.colour)
            em.add_field(name="Role Name", value=therole.name)
            em.add_field(name="Created", value=created_on)
            em.add_field(name="UsersinRole", value=len([m for m in server.members if therole in m.roles]))
            em.add_field(name="Id", value=therole.id)
            em.add_field(name="Color", value=therole.color)
            em.add_field(name="Position", value=therole.position)
            em.add_field(name="Valid Perms", value="{}".format(perms_we_have))
            em.add_field(name="Invalid Perms", value="{}".format(perms_we_dont))
            em.set_thumbnail(url=server.icon_url)
        try:
            await self.bot.edit_message(lolol, embed=em)
        except discord.HTTPException:
            permss = "```diff\n"
            therole = discord.utils.find(lambda r: r.name.lower() == rolename.lower(), ctx.message.server.roles)
            if therole is None:
                await bot.say(':no_good: That role cannot be found. :no_good:')
                return
            if therole is not None:
                perms = iter(therole.permissions)
                perms_we_have2 = ""
                perms_we_dont2 = ""
                for x in perms:
                    if "True" in str(x):
                        perms_we_have2 += "+{0}\n".format(str(x).split('\'')[1])
                    else:
                        perms_we_dont2 += ("-{0}\n".format(str(x).split('\'')[1]))
            await self.bot.say("{}Name: {}\nCreated: {}\nUsersinRole : {}\nId : {}\nColor : {}\nPosition : {}\nValid Perms : \n{}\nInvalid Perms : \n{}```".format(permss, therole.name, created_on, len([m for m in server.members if therole in m.roles]), therole.id, therole.color, therole.position, perms_we_have2, perms_we_dont2))
            await self.bot.delete_message(lolol)

    @commands.command(pass_context=True)
    async def discr(self, ctx, discrim: int):
        """gives you farmed discrms"""
        try:
            dis = []
            for server in self.bot.servers:
                for member in server.members:
                    if int(member.discriminator) == discrim:
                        if not member.name in dis:
                            dis.append(member.name)
            em = discord.Embed(title="Scraped Discriminators\n", description="\n".join(dis),color=0xff5555, inline=True)
            await self.bot.say(embed=em)
        except Exception as e:
            await self.bot.say(wrap.format(type(e).__name__ + ': ' + str(e)))

    @commands.command(pass_context=True)
    async def sleaderboard(self, ctx):
        author = ctx.message.author
        server = ctx.message.server
        e = discord.Embed(colour=author.colour)
        e.set_thumbnail(url=server.me.avatar_url)
        e.title = "Currently on shard {} with {} servers and {} users!".format(str(self.bot.shard_id + 1), len(self.bot.servers), len([e.name for e in self.bot.get_all_members()]))
        e.description = "".join(["**Name:** {0.name} | **Members:** {0.member_count} Members\n\n".format(e) for e in sorted(self.bot.servers, key =lambda e : e.member_count, reverse=True)][:10])
        await self.bot.say(embed=e)

    @commands.command(pass_context=True)
    async def info(self, ctx):
        """Shows info on Brooklyn."""
        server = ctx.message.server
        shard_count = self.bot.shard_count
        musage = psutil.Process().memory_full_info().uss / 1024**2
        members1 = str(sum(len(s.members) for s in self.bot.servers))
        members2 = str(int(str(members1)) * int(shard_count))
        cpu_p = psutil.cpu_percent(interval=None, percpu=True)
        cpu_usage = sum(cpu_p)/len(cpu_p)
        if server.me.colour:
            colour = server.me.colour
        else:
            colour = discord.Colour.blue()
        e = discord.Embed(description="Showing Information for Brooklyn.", colour=colour)
        e.set_thumbnail(url=self.bot.user.avatar_url)
        e.add_field(name="Developer:", value="<@146040787891781632>")
        e.add_field(name="Support:", value="<@217179156008534016>, <@125367412370440192>")
        e.add_field(name="Bot Version:", value="v4")
        e.add_field(name="Discord Version:", value=discord.__version__)
        e.add_field(name="Build Date:", value="September 16, 2016 00:09")
        e.add_field(name="Voice Connections:", value=len(self.bot.voice_clients))
        e.add_field(name="Servers:", value=str(int(len(self.bot.servers)) * int(shard_count)))
        e.add_field(name="Members:", value=members2)
        e.add_field(name="Shard Number:", value="Shard {} out of {}.".format(str(self.bot.shard_id + 1), str(self.bot.shard_count)))
        e.add_field(name="Shard Stats:", value="{} channels.\n{} members.\n{} servers.".format(len([e.name for e in self.bot.get_all_channels()]), members1, len(self.bot.servers)))
        e.add_field(name="Memory Usage:", value="{:.2f} MiB".format(musage))
        e.add_field(name='CPU usage:', value='{0:.1f}%'.format(cpu_usage))
        e.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await self.bot.say(embed=e)

    @commands.command(aliases=["guinfo"], pass_context=True)
    async def globaluserinfo(self, ctx, id: str):
        """Gives you the info of ANY user."""

        if not self.bot.user.bot:
            await self.bot.say("``This is not a bot account\n"
                               "It only works with bot accounts")
            return

        if not id.isdigit():
            await self.bot.say("You can only use IDs from a user\nExample: `146040787891781632` (ID of Young)")
            return

        try:
            user = await self.bot.get_user_info(id)
        except discord.errors.NotFound:
            await self.bot.say("No user with the id `{}` found.".format(id))
            return
        except:
            await self.bot.say("An error has occured.")
            return

        colour = ''.join([choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)

        randnum = randint(1, 10)
        empty = u"\u2063"
        emptyrand = empty * randnum

        user_created = user.created_at.strftime("%d %b %Y %H:%M")
        since_created = (ctx.message.timestamp - user.created_at).days

        created_on = "{}\n({} days ago)".format(user_created, since_created)

        if user .avatar_url.find("gif") != -1:
            nitro = True
        else:
            nitro = False

        if user.bot == False:
            data = discord.Embed(description="User ID : " +
                                 user.id, colour=colour)
        else:
            data = discord.Embed(
                description="**Bot** | User ID : " + user.id, colour=colour)

        data.add_field(name="Joined Discord on", value=created_on)
        data.add_field(name="Nitro", value=nitro)

        if user.avatar_url:
            data.set_author(name="{} {}".format(
                user.name, user.discriminator), url=user.avatar_url)
            data.set_thumbnail(url=user.avatar_url)
        else:
            data.set_author(name="{} {}".format(
                user.name, user.discriminator), url=user.default_avatar_url)
            data.set_thumbnail(url=user.default_avatar_url)

        try:
            await self.bot.say(embed=data)
        except:
            await self.bot.say("I need the `Embed links` permission "
                               "to send this")

    @commands.command(pass_context=True)
    async def invite(self, ctx):
        if not ctx.message.channel.is_private:
            await self.bot.reply("I have sent you my invite link in dm's! :mailbox_with_mail:")
        await self.bot.whisper("""**Hello there I see you have requested my invite link!**

**Here is my invite link:**
<https://discordapp.com/oauth2/authorize?client_id=226132382846156800&scope=bot&permissions=401697975>

**If you would like to help contribute to Brooklyn you may here:**
<https://www.patreon.com/_brooklyn>

**If you come across any problems or would like to receive updates on Brooklyn you may join this server!**
https://discord.gg/fmuvSX9""")

    @commands.command(pass_context=True, no_pm=True)
    async def channelinfo(self, ctx, *, channel: discord.Channel=None):
        """Shows channel informations"""
        author = ctx.message.channel
        server = ctx.message.server

        if not channel:
            channel = author

        userlist = [r.display_name for r in channel.voice_members]
        if not userlist:
            userlist = None
        else:
            userlist = "\n".join(userlist)

        passed = (ctx.message.timestamp - channel.created_at).days
        created_at = ("Created on {} ({} days ago!)"
                      "".format(channel.created_at.strftime("%d %b %Y %H:%M"),
                                passed))

        randnum = randint(1, 10)
        empty = u"\u2063"
        emptyrand = empty * randnum

        colour = ''.join([choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)

        data = discord.Embed(description="Channel ID: " +
                             channel.id, colour=discord.Colour(value=colour))
        if "{}".format(channel.is_default) == "True":
            data.add_field(name="Default Channel", value="Yes")
        else:
            data.add_field(name="Default Channel", value="No")
        data.add_field(name="Type", value=channel.type)
        data.add_field(name="Position", value=channel.position)
        if "{}".format(channel.type) == "voice":
            if channel.user_limit != 0:
                data.add_field(
                    name="User Number", value="{}/{}".format(len(channel.voice_members), channel.user_limit))
            else:
                data.add_field(name="User Number", value="{}".format(
                    len(channel.voice_members)))
            data.add_field(name="Users", value=userlist)
            data.add_field(name="Bitrate", value=channel.bitrate)
        elif "{}".format(channel.type) == "text":
            if channel.topic != "":
                data.add_field(name="Topic", value=channel.topic, inline=False)

        data.set_footer(text=created_at)
        data.set_author(name=channel.name)

        try:
            await self.bot.say(emptyrand, embed=data)
        except:
            await self.bot.say("I need the `Embed links` permission "
                               "to send this")

    @commands.command(pass_context=True)
    async def ping(self, ctx):
        """Pong."""
        msg = await self.bot.say("Pinging to server...")
        time = (msg.timestamp - ctx.message.timestamp).total_seconds() * 1000
        await self.bot.edit_message(msg, 'Pong: {}ms :ping_pong:'.format(round(time)))
        
    @commands.command(pass_context=True)
    async def stats(self, ctx):
        """Shows stats."""
        text_channels = 0
        voice_channels = 0
        list2 = []
        list = []
        for i in self.bot.servers:
            if i.me.voice_channel is not None:
                list.append(i.me.voice_channel)
        for c in list:
            list2.extend(c.voice_members)
        mem_v = psutil.virtual_memory()
        cpu_p = psutil.cpu_percent(interval=None, percpu=True)
        cpu_usage = sum(cpu_p)/len(cpu_p)
        online = len([e.name for e in self.bot.get_all_members() if not e.bot and e.status == discord.Status.online])
        idle = len([e.name for e in self.bot.get_all_members() if not e.bot and e.status == discord.Status.idle])
        dnd = len([e.name for e in self.bot.get_all_members() if not e.bot and e.status == discord.Status.dnd])
        offline = len([e.name for e in self.bot.get_all_members() if not e.bot and e.status == discord.Status.offline])
        seconds = time.time() - starttime
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        w, d = divmod(d, 7)
        t1 = time.perf_counter()
        await self.bot.type()
        t2 = time.perf_counter()
        data = discord.Embed(description="Showing stats for {}.".format(self.bot.user.name), colour=discord.Colour.red())
        data.add_field(name="Owner", value="<@146040787891781632>")
        data.add_field(name="Ping", value="{}ms".format(round((t2-t1)*1000)))
        data.add_field(name="Shard ID", value=str(self.bot.shard_id + 1))
        data.add_field(name="Shard Count", value=self.bot.shard_count)
        data.add_field(name="Servers", value=len(self.bot.servers))
        data.add_field(name="Api version", value=discord.__version__)
        data.add_field(name="Users", value="{} Online\n{} Idle\n{} Dnd\n{} Offline\n\n**Total:** {}".format(online, idle, dnd, offline, len([e.name for e in self.bot.get_all_members()])))
        data.add_field(name="Channels", value="{} Voice Channels\n{} Text Channels\n\n**Total:** {}".format(len([e.name for e in self.bot.get_all_channels() if e.type == discord.ChannelType.voice]), len([e.name for e in self.bot.get_all_channels() if e.type == discord.ChannelType.text]), len([e.name for e in self.bot.get_all_channels()])))
        data.add_field(name='CPU usage', value='{0:.1f}%'.format(cpu_usage))
        data.add_field(name='Memory usage', value='{0:.1f}%'.format(mem_v.percent))
        data.add_field(name="Commands", value="{0} active modules, with {1} commands...".format(len(self.bot.cogs), len(self.bot.commands)))
        data.add_field(name='Uptime', value="%d Weeks," % (w) + " %d Days," % (d) + " %d Hours,"
                                   % (
                h) + " %d Minutes," % (m) + " and %d Seconds!" % (s))
        data.add_field(name="Voice Stats:", value="Connected to {} voice channels, with a total of {} users.".format(len(list), len(list2)), inline=False)
        data.set_author(name=ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url)
        data.set_thumbnail(url=ctx.message.author.avatar_url)
        await self.bot.say(embed=data)

    @commands.command(pass_context=True)
    async def mods(self, ctx):
        """Shows mods in the server."""
        colour = "".join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        server = ctx.message.server
        one = [e.display_name for e in server.members if e.permissions_in(ctx.message.channel).manage_messages and not e.bot and e.status == discord.Status.online]
        two = [e.display_name for e in server.members if e.permissions_in(ctx.message.channel).manage_messages and not e.bot and e.status == discord.Status.idle]
        three = [e.display_name for e in server.members if e.permissions_in(ctx.message.channel).manage_messages and not e.bot and e.status == discord.Status.dnd]
        four = [e.display_name for e in server.members if e.permissions_in(ctx.message.channel).manage_messages and not e.bot and e.status == discord.Status.offline]
        embed = discord.Embed(description="Listing mods for this server.", colour=discord.Colour(value=colour))
        if one:
            embed.add_field(name="Online", value="{0}".format(("\n".join(one)).replace("`", "")), inline=False)
        else:
            embed.remove_field(0)
        if two:
            embed.add_field(name="Idle", value="{0}".format(("\n".join(two)).replace("`", "")), inline=False)
        else:
            embed.remove_field(1)
        if three:
            embed.add_field(name="Dnd", value="{0}".format(("\n".join(three)).replace("`", "")), inline=False)
        else:
            embed.remove_field(2)
        if four:
            embed.add_field(name="Offline", value="{0}".format(("\n".join(four)).replace("`", "")), inline=False)
        else:
            embed.remove_field(3)
        if server.icon_url:
            embed.set_author(name=server.name, url=server.icon_url)
            embed.set_thumbnail(url=server.icon_url)
        else:
            embed.set_author(name=server.name)
        await self.bot.say(embed=embed)
        
    @commands.command(pass_context=True)
    async def admins(self, ctx):
        """Shows mods in the server."""
        colour = "".join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        server = ctx.message.server
        one = [e.display_name for e in server.members if e.permissions_in(ctx.message.channel).administrator and not e.bot and e.status == discord.Status.online]
        two = [e.display_name for e in server.members if e.permissions_in(ctx.message.channel).administrator and not e.bot and e.status == discord.Status.idle]
        three = [e.display_name for e in server.members if e.permissions_in(ctx.message.channel).administrator and not e.bot and e.status == discord.Status.dnd]
        four = [e.display_name for e in server.members if e.permissions_in(ctx.message.channel).administrator and not e.bot and e.status == discord.Status.offline]
        embed = discord.Embed(description="Listing admins for this server.", colour=discord.Colour(value=colour))
        if one:
            embed.add_field(name="Online", value="{0}".format(("\n".join(one)).replace("`", "")), inline=False)
        else:
            embed.remove_field(0)
        if two:
            embed.add_field(name="Idle", value="{0}".format(("\n".join(two)).replace("`", "")), inline=False)
        else:
            embed.remove_field(1)
        if three:
            embed.add_field(name="Dnd", value="{0}".format(("\n".join(three)).replace("`", "")), inline=False)
        else:
            embed.remove_field(2)
        if four:
            embed.add_field(name="Offline", value="{0}".format(("\n".join(four)).replace("`", "")), inline=False)
        else:
            embed.remove_field(3)
        if server.icon_url:
            embed.set_author(name=server.name, url=server.icon_url)
            embed.set_thumbnail(url=server.icon_url)
        else:
            embed.set_author(name=server.name)
        await self.bot.say(embed=embed)
        
    @commands.command(pass_context=True)
    async def banlist(self, ctx):
        """Displays the server's banlist"""
        try:
            banlist = await self.bot.get_bans(ctx.message.server)
        except discord.errors.Forbidden:
            await self.bot.say("I do not have the `Ban Members` permission")
            return
        bancount = len(banlist)
        if bancount == 0:
            banlist = "No users are banned from this server"
        else:
            banlist = "\n".join(map(str, banlist))
        await self.bot.say("Total bans: `{}`\n```{}```".format(bancount, banlist))
        
    @commands.command(pass_context=True)
    async def serverinfo(self, ctx):
        "Show server , owner and channel info"
        server = ctx.message.server
        channel = ctx.message.channel
        members = set(server.members)

        owner = server.owner

        offline = filter(lambda m: m.status is discord.Status.offline, members)
        offline = set(offline)

        bots = filter(lambda m: m.bot, members)
        bots = set(bots)

        users = members - bots

        msg = '\n'.join((
            'Server Name     : ' + server.name,
            'Server ID       : ' + str(server.id),
            'Server Created  : ' + str(server.created_at),
            'Server Region   : ' + str(server.region),
            'Verification    : ' + str(server.verification_level),
            # minus one for @​everyone
            'Server # Roles  : %i' % (len(server.roles) - 1),
            '',
            'Server Owner    : ' + (
                ('{0.nick} ({0})'.format(owner)) if owner.nick
                else str(owner)),
            'Owner ID        : ' + str(owner.id),
            'Owner Status    : ' + str(owner.status),
            '',
            'Total Bots      : %i' % len(bots),
            'Bots Online     : %i' % len(bots - offline),
            'Bots Offline    : %i' % len(bots & offline),
            '',
            'Total Users     : %i' % len(users),
            'Users Online    : %i' % len(users - offline),
            'Users Offline   : %i' % len(users & offline),
            '',
            'Current Channel : #' + channel.name,
            'Channel ID      : ' + str(channel.id),
            'Channel Created : ' + str(channel.created_at)
        ))
        embed=discord.Embed(description=msg, colour=discord.Colour.blue())
        embed.set_thumbnail(url=ctx.message.server.icon_url)
        await self.bot.say(embed=embed)
        
    def fetch_joined_at(self, user, server):
        return user.joined_at
        
    @commands.command(pass_context=True)
    async def userinfo(self, ctx, *, user: discord.Member=None):
        """Shows userss informations"""
        author = ctx.message.author
        server = ctx.message.server
        if not user:
            user = author
        roles = [x.name for x in user.roles if x.name != "@everyone"]
        joined_at = self.fetch_joined_at(user, server)
        since_created = (ctx.message.timestamp - user.created_at).days
        since_joined = (ctx.message.timestamp - joined_at).days
        user_joined = joined_at.strftime("%d %b %Y %H:%M")
        user_created = user.created_at.strftime("%d %b %Y %H:%M")
        member_number = sorted(server.members, key=lambda m: m.joined_at).index(user) + 1
        shared = sum(1 for m in self.bot.get_all_members() if m.id == user.id)
        created_on = "{}\n({} days ago)".format(user_created, since_created)
        joined_on = "{}\n({} days ago)".format(user_joined, since_joined)
        game = "Chilling in {} status".format(user.status)
        if user.game is None:
            pass
        elif user.game.url is None:
            game = "**Playing:** {}".format(user.game)
        else:
            game = "**Streaming:** [{}]({})".format(user.game, user.game.url)
        if roles:
            roles = sorted(roles, key=[x.name for x in server.role_hierarchy if x.name != "@everyone"].index)
            roles = ", ".join(roles)
        else:
            roles = "None"
        data = discord.Embed(description=game, colour=user.colour)
        data.add_field(name="Name", value=user.name)
        data.add_field(name="ID", value=user.id)
        data.add_field(name="Member Number:", value=member_number)
        data.add_field(name="Shared Servers:", value="%s servers." % shared)
        data.add_field(name="Color", value=user.colour)
        data.add_field(name="Discriminator", value=user.discriminator)
        data.add_field(name="VoiceChannel", value=bool(user.voice_channel))
        data.add_field(name="Nickname", value=user.nick)
        data.add_field(name="Deafened", value="Local: {}\nServer: {}".format(user.self_deaf, user.deaf))
        data.add_field(name="Muted", value="Local: {}\nServer: {}".format(user.self_mute, user.mute))
        data.add_field(name="Status", value=user.status)
        data.add_field(name="Top Role", value=user.top_role)
        data.add_field(name="Joined Discord on", value=created_on)
        data.add_field(name="Joined this server on", value=joined_on)
        data.add_field(name="All Roles", value=roles, inline=False)
        if user.avatar_url:
            name = str(user)
            name = " ~ ".join((name, user.nick)) if user.nick else name
            data.set_author(name=name, url=user.avatar_url)
            data.set_thumbnail(url=user.avatar_url)
        else:
            data.set_author(name=user.name)
        try:
            await self.bot.say(embed=data)
        except discord.HTTPException:
            author = ctx.message.author
            server = ctx.message.server
            if not user:
                user = author
            roles = [x.name for x in user.roles if x.name != "@everyone"]
            if not roles: roles = ["None"]
            data = "```prolog\n"
            data += "Name: {}\n".format(str(user))
            data += "Nickname: {}\n".format(str(user.nick))
            data += "ID: {}\n".format(user.id)
            if user.game is None:
                pass
            elif user.game.url is None:
                data += "Playing: {}\n".format(str(user.game))
            else:
                data += "Streaming: {} ({})\n".format(str(user.game),(user.game.url))
            passed = (ctx.message.timestamp - user.created_at).days
            data += "Created: {} ({} days ago)\n".format(user.created_at, passed)
            joined_at = self.fetch_joined_at(user, server)
            passed = (ctx.message.timestamp - joined_at).days
            data += "Joined: {} ({} days ago)\n".format(joined_at, passed)
            data += "Roles: {}\n".format(", ".join(roles))
            if user.avatar_url != "":
                data += "Avatar:"
                data += "```"
                data += user.avatar_url
            else:
                data += "```"
            await self.bot.say(data)
            
    @commands.command(pass_context=True)
    async def emotes(self, ctx):
        """Server emotes."""
        server = ctx.message.server

        list = [e for e in server.emojis if not e.managed]
        emoji = ''
        for emote in list:
            emoji += "<:{0.name}:{0.id}> ".format(emote)
        try:
            await self.bot.say(emoji)
        except:
            await self.bot.say("Server has no emotes.")
            
    @commands.command(pass_context=True)
    async def avatar(self, ctx, *, user: discord.Member=None):
        """Retrieves a users avatar."""
        author = ctx.message.author
        if not user:
            user = author
        data = discord.Embed(colour=user.colour)
        data.set_image(url=user.avatar_url)
        data.set_author(name="Avatar for "+user.name, icon_url=user.avatar_url)
        data.set_footer(text=datetime.datetime.now().strftime("%A, %B %-d %Y at %-I:%M%p").replace("PM", "pm").replace("AM", "am"))
        await self.bot.say(embed=data)
        
    @commands.command(pass_context=True)
    async def permissions(self, ctx):
        user = await self._prompt(ctx, "Mention a user...")
        try:
            if user.mentions is not None:
                user = user.mentions[0]
        except:
            try:
                user = discord.utils.get(ctx.message.server.members, name=str(user.content))
            except:
                return await self.bot.say("User not found!:x:")
        perms = iter(ctx.message.channel.permissions_for(user))
        perms_we_have = "```diff\n"
        perms_we_dont = ""
        for x in perms:
            if "True" in str(x):
                perms_we_have += "+\t{0}\n".format(str(x).split('\'')[1])
            else:
                perms_we_dont += ("-\t{0}\n".format(str(x).split('\'')[1]))
        await self.bot.say("{0}{1}```".format(perms_we_have, perms_we_dont))

    async def _prompt(self, ctx, msg: str):
        await self.bot.say(msg)
        msg = await self.bot.wait_for_message(author=ctx.message.author, channel=ctx.message.channel)
        return msg

def setup(bot):
    n = Info(bot)
    bot.add_cog(n)
