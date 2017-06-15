import os
import aiohttp
import traceback
import sys
import re
import json
import time
import asyncio
import discord
import datetime
from utils import checks
from discord.ext import commands
from utils.dataIO import fileIO
from random import choice as randchoice

prefix = "b!"
description = ''
shard_id = 2
shard_count = 3
bot = commands.Bot(command_prefix=(prefix), description=description, shard_id=shard_id, shard_count=shard_count)
start_time = time.time()
starttime2 = time.ctime(int(time.time()))
bot.pm_help = None
wrap = "```py\n{}\n```"
aiosession = aiohttp.ClientSession(loop=bot.loop)

async def _restart_bot():
    await bot.logout()
    subprocess.call([sys.executable, "shard_1.py"])

modules = [
    'modules.music2',
    'modules.fun',
    'modules.joinmsg',
    'modules.gfx',
    'modules.autorole',
    'modules.repl2',
    'modules.bump',
    'modules.terminal',
    'modules.casino',
    'modules.dev',
    'modules.ignore',
    'modules.tags',
    'modules.welcomer',
    'modules.weather',
    'modules.antilink',
    'modules.antiraid',
    'modules.info',
    'modules.modlog',
    'modules.mod']

@bot.event
async def on_message(message):
    db = fileIO("data/ignore/ignore_list.json", "load")
    author = message.author
    server = message.server
    channel = message.channel
    settings = {"Channels" : [], "Users" : [], "Roles" : []}
    if message.content.startswith("b!"):
        if server.id not in db:
            db[server.id] = settings
            fileIO("data/ignore/ignore_list.json", "save", db)
            print("[ Ignore ] Adding {} to ignore_list.json..".format(server.name))
        if channel.id in db[server.id]["Channels"]:
            ok = await bot.send_message(message.channel, "This channel is in the ignore list, please use another channel.")
            await asyncio.sleep(10)
            await bot.delete_message(ok)
            print("[ Ignore ] Ignoring {} in ignored channel {}.".format(message.author.name, message.channel.name))
        elif author.id in db[server.id]["Users"]:
            ok = await bot.send_message(message.channel, "You are in the ignore list, please consult a mod or admin for your server.")
            await asyncio.sleep(10)
            await bot.delete_message(ok)
            print("[ Ignore ] Ignoring {} ignored user.".format(message.author.name))
        elif set(r.id for r in author.roles) & set(db[server.id]["Roles"]):
            ok = await bot.send_message(message.channel, "You are a member of an ignored role. Please consult a mod or admin for your server.")
            print("[ Ignore ] Ignoring {} apart of ignore role.".format(message.author.name))
            await asyncio.sleep(10)
            await bot.delete_message(ok)
        else:
            await bot.process_commands(message)

@bot.event
async def on_command(command, ctx):
    if ctx.message.channel.is_private:
        server = "Private Message"
    else:
        server = "{}/{}".format(ctx.message.server.id, ctx.message.server.name)
    print("[{} at {}] [Command] [{}] [{}/{}]: {}".format(time.strftime("%m/%d/%Y"), time.strftime("%I:%M:%S %p %Z"), server, ctx.message.author.id, ctx.message.author, ctx.message.content))

@bot.event
async def on_message_edit(before, message):
    db = fileIO("data/ignore/ignore_list.json", "load")
    author = message.author
    server = message.server
    channel = message.channel
    settings = {"Channels" : [], "Users" : [], "Roles" : []}
    if message.content.startswith("b!"):
        if server.id not in db:
            db[server.id] = settings
            fileIO("data/ignore/ignore_list.json", "save", db)
            print("[ Ignore ] Adding {} to ignore_list.json..".format(server.name))
        if channel.id in db[server.id]["Channels"]:
            ok = await bot.send_message(message.channel, "This channel is in the ignore list, please use another channel.")
            await asyncio.sleep(10)
            await bot.delete_message(ok)
            print("[ Ignore ] Ignoring {} in ignored channel {}.".format(message.author.name, message.channel.name))
        elif author.id in db[server.id]["Users"]:
            ok = await bot.send_message(message.channel, "You are in the ignore list, please consult a mod or admin for your server.")
            await asyncio.sleep(10)
            await bot.delete_message(ok)
            print("[ Ignore ] Ignoring {} ignored user.".format(message.author.name))
        elif set(r.id for r in author.roles) & set(db[server.id]["Roles"]):
            ok = await bot.send_message(message.channel, "You are a member of an ignored role. Please consult a mod or admin for your server.")
            print("[ Ignore ] Ignoring {} apart of ignore role.".format(message.author.name))
            await asyncio.sleep(10)
            await bot.delete_message(ok)
        else:
            await bot.process_commands(message)

@bot.event
async def on_command_error(error, ctx):
    channel = ctx.message.channel
    if isinstance(error, commands.MissingRequiredArgument):
        await bot.send_message(ctx.message.channel, ":x: Missing a required argument. Help : ```css\n{0}{1:<{width}}\n\n{2}```".format(ctx.prefix, ctx.command.name, ctx.command.short_doc, width=5))
    elif isinstance(error, commands.BadArgument):
        await bot.send_message(ctx.message.channel, ":x: Bad argument provided. Help : ```css\n{0}{1:<{width}}\n\n{2}```".format(ctx.prefix, ctx.command.name, ctx.command.short_doc, width=5))
    elif isinstance(error, commands.CheckFailure):
        await bot.send_message(channel, "{} :x:  Checks failure, you do not have the correct role permissions to use this command.".format(ctx.message.author.mention))
    elif isinstance(error, commands.CommandOnCooldown):
        await bot.send_message(channel, ":x: This command is on cooldown. Try again in {:.2f}s".format(error.retry_after))
    else:
        if ctx.command:
            await bot.send_message(ctx.message.channel, "{} :bangbang: An error occured while processing the `{}` command.\n\nPlease use `b!report <command name>`!!".format(ctx.message.author.mention, ctx.command.name))
        print('Ignoring exception in command {}'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

@bot.event
async def on_resumed():
    print("\nResumed connectivity!")

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    for extension in modules:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

class Default():
    def __init__(self, bot):
        self.bot = bot

@bot.command(hidden=True, pass_context=True)
@checks.is_owner()
async def setgame(self, ctx, *, game=None):
    """Sets Brooklyn's playing status
        Leaving this empty will clear it."""
    server = ctx.message.server
    current_status = server.me.status if server is not None else None
    if game:
        game = game.strip()
        await self.bot.change_presence(game=discord.Game(name=game), status=current_status)
    else:
        await self.bot.change_presence(game=None, status=current_status)
    await self.bot.say(":ok_hand:")

@bot.command(hidden=True, pass_context=True)
@checks.is_owner()
async def shutdown(ctx):
    """Shuts down the bot"""
    await bot.say("Bye, I'm not coming back.")
    print("{} has shut down the bot!".format(ctx.message.author))
    await _shutdown_bot()

@bot.command(hidden=True, pass_context=True)
@checks.is_owner()
async def restart(ctx):
    """Restarts the bot"""
    await bot.say("Be right back, hopefully.")
    print("{} has restarted the bot!".format(ctx.message.author))
    await _restart_bot()

@bot.command()
async def uptime():
    """Displays how long the bot has been online for"""
    second = time.time() - start_time
    minute, second = divmod(second, 60)
    hour, minute = divmod(minute, 60)
    day, hour = divmod(hour, 24)
    week, day = divmod(day, 7)
    await bot.say("I've been online for %d weeks, %d days, %d hours, %d minutes, %d seconds!" % (week, day, hour, minute, second))

@bot.command(hidden=True, pass_context=True)
@checks.is_owner()
async def setavatar(ctx, *, url : str=None):
    """Sets Brooklyn's avatar"""
    if ctx.message.attachments:
        url = ctx.message.attachments[0]["url"]
    elif url is None:
        await bot.say("I need a link to be able to change my avatar, ffs even my owner if retarded. :face_palm:")
        return
    try:
        with aiohttp.Timeout(10):
            async with aiosession.get(url.strip("<>")) as image:
                await bot.edit_profile(avatar=await image.read())
    except Exception as e:
        await bot.say(":x: Unable to change avatar!", embed=discord.Embed(description="{}".format(e), colour=discord.Colour.red()))
    await bot.say(":heart_eyes:")

@bot.command(hidden=True)
@checks.is_owner()
async def load(*, module: str):
    """Loads a part of the bot."""
    module = "modules." + module
    try:
        if module in modules:
            await bot.say("Alright, loading {}".format(module))
            bot.load_extension(module)
            await bot.say("Loading finished!")
        else:
            await bot.say("You can't load a module that doesn't exist!")
    except Exception as e:
        await bot.say(wrap.format(type(e).__name__ + ': ' + str(e)))

@bot.command(hidden=True)
@checks.is_owner()
async def unload(*, module: str):
    """Unloads a part of the bot."""
    module = "modules." + module
    try:
        if module in modules:
            await bot.say("Oh, ok, unloading {}".format(module))
            bot.unload_extension(module)
            await bot.say("Unloading finished!")
        else:
            await bot.say("You can't unload a module that doesn't exist!")
    except Exception as e:
        await bot.say(wrap.format(type(e).__name__ + ': ' + str(e)))
        
@bot.command(hidden=True)
@checks.is_owner()
async def reload(*, module: str):
    """Reloads a part of the bot."""
    module = "modules." + module
    try:
        if module in modules:
            await bot.say("Oh, ok, reloading {}".format(module))
            bot.unload_extension(module)
            bot.load_extension(module)
            await bot.say("Reloading finished!")
        else:
            await bot.say("You can't reload a module that doesn't exist!")
    except Exception as e:
        await bot.say(wrap.format(type(e).__name__ + ': ' + str(e)))

@bot.command(hidden=True, pass_context=True)
@checks.is_owner()
async def debug(ctx, *, code: str):
    """Evaluates code."""
    try:
        result = eval(code)
        if code.lower().startswith("print"):
            result
        elif asyncio.iscoroutine(result):
            await result
        else:
            await bot.say(wrap.format(result))
    except Exception as e:
        await bot.say(wrap.format(type(e).__name__ + ': ' + str(e)))

@bot.command(hidden=True, pass_context=True)
@checks.is_owner()
async def setname(ctx, *, name: str):
    """Sets the bots name."""
    try:
        await bot.edit_profile(username=name)
        await bot.say("Username successfully changed to `{}`".format(name))
    except Exception as e:
        await bot.say(wrap.format(type(e).__name__ + ': ' + str(e)))

bot.add_cog(Default(bot))
loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(bot.login(""))
    loop.run_until_complete(bot.connect())
except Exception:
    loop.run_until_complete(os.system("shard_3.py"))
finally:
    loop.close()
