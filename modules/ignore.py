import os
import discord
import asyncio
from utils import checks
from discord.ext import commands
from random import choice, randint
from utils.dataIO import fileIO, dataIO

settings = {"Channels" : [], "Users" : [], "Roles" : []}

class Ignore:
    def __init__(self, bot):
        self.bot = bot
        self.load = "data/ignore/ignore_list.json"
		    
    @checks.botcom()
    @commands.group(pass_context=True, name="ignore")
    async def _ignore(self, ctx):
        """Ignore a channel, user and or role for your server."""
        if ctx.invoked_subcommand is None:
            e = discord.Embed(description="""b!ignore

Ignore a channel, user and or role for your server.

Commands:
  user      Ignore a role.
  role      Ignore a role.
  channel   Ignore a channel.

Type b!help command for more info on a command.
You can also type b!help category for more info on a category.""")
            e.set_author(name="Help for {}'s command group {}.".format(self.bot.user.name, ctx.command), icon_url=ctx.message.server.me.avatar_url)
            e.set_thumbnail(url=ctx.message.server.me.avatar_url)
            await self.bot.say(embed=e)

    @_ignore.command(pass_context=True)
    async def channel(self, ctx, *, channel : discord.Channel):
        """Ignore a channel."""
        server = ctx.message.server
        db = fileIO(self.load, "load")
        if server.id in db:
            if channel.id not in db[server.id]["Channels"]:
                db[server.id]["Channels"].append(channel.id)
                fileIO(self.load, "save", db)
                await self.bot.say("Channel added to the ignore list.")
                return
            if channel.id in db[server.id]["Channels"]:
                await self.bot.say("This channel is already in the ignore list.")
                return

    @_ignore.command(pass_context=True)
    async def role(self, ctx, *, role : discord.Role):
        """Ignore a role."""
        server = ctx.message.server
        db = fileIO(self.load, "load")
        if server.id in db:
            if role.id not in db[server.id]["Roles"]:
                db[server.id]["Roles"].append(role.id)
                fileIO(self.load, "save", db)
                await self.bot.say("Role added to the ignore list.")
                return
            if role.id in db[server.id]["Roles"]:
                await self.bot.say("This role is already in the ignore list.")
                return

    @_ignore.command(pass_context=True)
    async def user(self, ctx, *, user : discord.Member):
        """Ignore a role."""
        server = ctx.message.server
        db = fileIO(self.load, "load")
        if server.id in db:
            if user.id not in db[server.id]["Users"]:
                db[server.id]["Users"].append(user.id)
                fileIO(self.load, "save", db)
                await self.bot.say("User added to the ignore list.")
                return
            if user.id in db[server.id]["Users"]:
                await self.bot.say("This user is already in the ignore list.")
                return

    @checks.botcom()
    @commands.group(pass_context=True, name="unignore")
    async def _unignore(self, ctx):
        """Unignore a channel, user and or role for your server."""
        if ctx.invoked_subcommand is None:
            e = discord.Embed(description="""b!ignore

Unignore a channel, user and or role for your server.

Commands:
  user      Unignore a role.
  role      Unignore a role.
  channel   Unignore a channel.

Type b!help command for more info on a command.
You can also type b!help category for more info on a category.""")
            e.set_author(name="Help for {}'s command group {}.".format(self.bot.user.name, ctx.command), icon_url=ctx.message.server.me.avatar_url)
            e.set_thumbnail(url=ctx.message.server.me.avatar_url)
            await self.bot.say(embed=e)

    @_unignore.command(name="channel", pass_context=True)
    async def _channel(self, ctx, *, channel : discord.Channel):
        """Unignore a channel."""
        server = ctx.message.server
        db = fileIO(self.load, "load")
        if server.id in db:
            if channel.id not in db[server.id]["Channels"]:
                await self.bot.say("Channel is not in the ignore list.")
                return
            if channel.id in db[server.id]["Channels"]:
                db[server.id]["Channels"].remove(channel.id)
                fileIO(self.load, "save", db)
                await self.bot.say("This channel has been removed from the ignore list.")
                return

    @_unignore.command(name="role", pass_context=True)
    async def _role(self, ctx, *, role : discord.Role):
        """Unignore a role."""
        server = ctx.message.server
        db = fileIO(self.load, "load")
        if server.id in db:
            if role.id not in db[server.id]["Roles"]:
                await self.bot.say("Role is not in the ignore list.")
                return
            if role.id in db[server.id]["Roles"]:
                db[server.id]["Roles"].remove(role.id)
                fileIO(self.load, "save", db)
                await self.bot.say("This role has been removed from the ignore list.")
                return

    @_unignore.command(name="user", pass_context=True)
    async def _user(self, ctx, *, user : discord.Member):
        """Unignore a role."""
        server = ctx.message.server
        db = fileIO(self.load, "load")
        if server.id in db:
            if user.id not in db[server.id]["Users"]:
                await self.bot.say("User is not in the ignore list.")
                return
            if user.id in db[server.id]["Users"]:
                db[server.id]["Users"].remove(user.id)
                fileIO(self.load, "save", db)
                await self.bot.say("This user has been removed from the ignore list.")
                return

def check_folder():
    if not os.path.exists('data/ignore'):
        print('Creating data/ignore folder...')
        os.makedirs('data/ignore')


def check_file():
    f = 'data/ignore/ignore_list.json'
    if not fileIO(f, 'check'):
        print('Creating default settings.json...')
        fileIO(f, 'save', {})

def setup(bot):
    check_folder()
    check_file()
    n = Ignore(bot)
    bot.add_cog(n)
