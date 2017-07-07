import discord
import asyncio
import datetime
import json
from discord.ext import commands
from subprocess import check_output, CalledProcessError
from utils import checks
from utils.dataIO import dataIO, fileIO
from utils.chat_formatting import pagify, box

wrap = "```py\n{}```"
with open('config.json') as f:
	config = json.load(f)
owner = config['OWNER_ID']
class Dev:
    def __init__(self, bot):
        self.bot = bot
        self.config = dataIO.load_json('config.json')

    @commands.command(pass_context=True)
    async def github(self, ctx):
        """Post Brooklyn's github link."""
        link = "https://github.com/JonnyBoy2000/Brooklyn1.0"
        author = ctx.message.author.mention
        server = "https://discord.gg/fmuvSX9"
        msg = """{} Brooklyn is an open source Discord bot for the public. Brooklyn was coded by Young:tm: with love and pation for users to make their server more alive!

**Github:** {}
**Sever:** {}

If you ever have problems with the bot please stop by the support server so we can guide you through your issue. :heart:

**DISCLAIMER:** Brooklyn is packed with reds audio modules, and some of the utils. I do claim any credit for making the code. All respect goes to the developers and contributers to red. :ok_hand:"""
        await self.bot.say(msg.format(author, link, server))

    @commands.command(pass_context=True)
    async def report(self, ctx, *, command_name: str):
        """Dm users."""
        try:
            e = discord.Embed(colour=discord.Colour.red())
            e.set_author(name="New report message!", icon_url=ctx.message.author.avatar_url)
            e.add_field(name="Reporter:", value="{}\n{}".format(ctx.message.author, ctx.message.author.id))
            e.add_field(name="Message:", value=command_name, inline=False)
            e.set_thumbnail(url=ctx.message.author.avatar_url)
            await self.bot.send_message(discord.User(id=self.config["OWNER_ID"]), embed=e)
            await self.bot.send_message(discord.User(id=owner), embed=e)
        except Exception as e:
            await self.bot.say(embed=discord.Embed(description=wrap.format(type(e).__name__ + ': ' + str(e)), colour=discord.Colour.red()))
        else:
            await self.bot.say("Succesfully sent :heavy_check_mark:")

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def whisper(self, ctx, user_id: str, *, msg: str):
        """Dm users."""
        user = await self.bot.get_user_info(user_id)
        try:
            e = discord.Embed(colour=discord.Colour.red())
            e.title = "You've recieved a message from a developer!"
            e.add_field(name="Developer:", value=ctx.message.author, inline=False)
            e.add_field(name="Time:", value=datetime.datetime.now().strftime("%A, %B %-d %Y at %-I:%M%p").replace("PM", "pm").replace("AM", "am"), inline=False)
            e.add_field(name="Message:", value=msg, inline=False)
            e.set_thumbnail(url=ctx.message.author.avatar_url)
            await self.bot.send_message(user, embed=e)
        except:
            await self.bot.say(':x: Failed to send message to user_id `{}`.'.format(user_id))
        else:
            await self.bot.say('Succesfully sent message to {}'.format(user_id))

    @commands.command(hidden=True, pass_context=True)
    @checks.is_owner()
    async def eval(self, ctx, *, code: str):
        """Evaluates code."""
        server = ctx.message.server
        author = ctx.message.author
        channel = ctx.message.channel
        message = ctx.message
        ctx = ctx
        try:
            result = eval(code)
            if code.lower().startswith("print"):
                result
            elif asyncio.iscoroutine(result):
                await result
            else:
                e = discord.Embed(colour=discord.Colour.green())
                e.add_field(name="Input:", value=wrap.format(code), inline=False)
                e.add_field(name="Output:", value=wrap.format(result), inline=False)
                await self.bot.say(embed=e)
        except Exception as e:
            await self.bot.say(embed=discord.Embed(description=wrap.format(type(e).__name__ + ': ' + str(e)), colour=discord.Colour.red()))

    @commands.group(pass_context=True)
    @checks.is_owner()
    async def pip(self, ctx):
        """Pip tools."""
        if ctx.invoked_subcommand is None:
            e = discord.Embed(description="""b!pip

Pip tools.

Commands:
  upgrade   Upgrade pip programs for Python 3.5
  uninstall Uninstall pip programs for Python 3.5
  install   Install pip programs for Python 3.5

Type b!help command for more info on a command.
You can also type b!help category for more info on a category.""")
            e.set_author(name="Help for {}'s command group {}.".format(self.bot.user.name, ctx.command), icon_url=ctx.message.server.me.avatar_url)
            e.set_thumbnail(url=ctx.message.server.me.avatar_url)
            await self.bot.say(embed=e)
            
    @pip.command()
    async def install(self, *, packagename):
        """Install pip programs for Python 3.5"""
        try:
            output = check_output("pip3 install {}".format(packagename), shell=True)
            await self.bot.say("`{}` installed succesfully!".format(packagename))
        except CalledProcessError as error:
            output = error.output
            await self.bot.say(output)

    @pip.command()
    async def uninstall(self, *, packagename):
        """Uninstall pip programs for Python 3.5"""
        try:
            output = check_output("pip3 uninstall {}".format(packagename), shell=True)
            await self.bot.say("`{}` uninstalled succesfully!".format(packagename))
        except CalledProcessError as error:
            output = error.output
            await self.bot.say(output)

    @pip.command()
    async def upgrade(self, *, packagename):
        """Upgrade pip programs for Python 3.5"""
        try:
            output = check_output("pip3 install {} --upgrade".format(packagename), shell=True)
            await self.bot.say("`{}` upgraded succesfully!".format(packagename))
        except CalledProcessError as error:
            output = error.output
            await self.bot.say(output)

def setup(bot):
    bot.add_cog(Dev(bot))
