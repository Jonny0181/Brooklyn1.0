import discord
import asyncio
import datetime
from discord.ext import commands
from subprocess import check_output, CalledProcessError
from utils import checks
from utils.chat_formatting import pagify, box

wrap = "```py\n{}```"

class Dev:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def github(self, ctx):
        """Post Brooklyn's github link."""
        link = "https://github.com/JonnyBoy2000/RBrooklyn"
        author = ctx.message.author.mention
        msg = """{} this command is on for coders that want to make a pull request on the github page for feature requests! If you are wanting to code features or make an pull request please visit the link below, all code will be looked over an reviewed before merged with the master branch.

**Link:** {}

Sometime in the near future I will make Brooklyn open for the public, and users be able to have their own instances of the bot! (In the working should been released in the next couple of months or if Brooklyn hits 2k servers!) Just a reminder, I love you all and thank you for the support! :heart:"""
        await self.bot.say(msg.format(author, link))

    @commands.command(pass_context=True)
    async def report(self, ctx, *, command_name: str):
        """Dm users."""
        try:
            e = discord.Embed(colour=discord.Colour.red())
            e.set_author(name="New report message!", icon_url=ctx.message.author.avatar_url)
            e.add_field(name="Reporter:", value="{}\n{}".format(ctx.message.author, ctx.message.author.id))
            e.add_field(name="Time:", value=datetime.datetime.now().strftime("%A, %B %-d %Y at %-I:%M%p").replace("PM", "pm").replace("AM", "am"), inline=False)
            e.add_field(name="Message:", value=command_name, inline=False)
            e.set_thumbnail(url=ctx.message.author.avatar_url)
            await self.bot.send_message(discord.User(id="146040787891781632"), embed=e)
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
