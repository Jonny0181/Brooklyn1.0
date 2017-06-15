import discord
from discord.ext import commands
from utils import checks
from utils.dataIO import dataIO
import os
import asyncio

class AntiRaid:
    """Protect yourself from server raids."""

    def __init__(self, bot):
        self.bot = bot
        self.settings = dataIO.load_json("data/antiraid/settings.json")

    @checks.botcom()
    @commands.group(pass_context=True)
    async def antiraid(self, ctx):
        """Manage antiraid settings."""
        if not ctx.invoked_subcommand:
            e = discord.Embed(description="""b!antiraid

Manage antiraid settings.

Commands:
  setchannel Sets the channel new members should see when protected.
  members    Shows you how much people should join within 8 seconds before th...
  setmembers Sets after how many members join in 8 seconds the bot will prote...
  toggle     Toggle antiraid.

Type b!help command for more info on a command.
You can also type b!help category for more info on a category.""")
            e.set_author(name="Help for {}'s command group {}.".format(self.bot.user.name, ctx.command), icon_url=ctx.message.server.me.avatar_url)
            e.set_thumbnail(url=ctx.message.server.me.avatar_url)
            await self.bot.say(embed=e)
        if not ctx.message.server.id in self.settings:
            self.settings[ctx.message.server.id] = {'joined': 0, 'channel': None, 'members': 4, 'protected': False}
            self.save_settings()
            
    @antiraid.command(pass_context=True)
    @checks.botcom()
    async def setchannel(self, ctx, channel:discord.Channel):
        """Sets the channel new members should see when protected."""
        self.settings[ctx.message.server.id]['channel'] = channel.id
        self.save_settings()
        await self.bot.say("Channel set.")
            
    @antiraid.command(pass_context=True)
    @checks.botcom()
    async def toggle(self, ctx):
        """Toggle antiraid."""
        if self.settings[ctx.message.server.id]['protected']:
            self.settings[ctx.message.server.id]['protected'] = False
            await self.bot.say("Your server is no longer protected, anyone that joins will be able to see all channels.")
        else:
            self.settings[ctx.message.server.id]['protected'] = True
            await self.bot.say("Your server is now protected, anyone that joins will only be able to see the set channel.")
        self.save_settings()
        
    @antiraid.command(pass_context=True)
    @checks.botcom()
    async def setmembers(self, ctx, members:int):
        """Sets after how many members join in 8 seconds the bot will protect the server.
        0 is unlimited, so that will turn it off. Default is 4."""
        self.settings[ctx.message.server.id]['members'] = members
        self.save_settings()
        await self.bot.say("Members set")
    
    @antiraid.command(pass_context=True)
    async def members(self, ctx):
        """Shows you how much people should join within 8 seconds before the bot should turn on antiraid.
        0 is unlimited."""
        await self.bot.say("The bot will turn on antiraid when {} people join in 8 seconds.".format(self.settings[ctx.message.server.id]['members']))
    
    def save_settings(self):
        dataIO.save_json("data/antiraid/settings.json", self.settings)
        
    async def on_member_join(self, member):
        if (member.server.id in self.settings) and not ("bots" in member.server.name.lower()):
            try:
                temp = self.settings[member.server.id]['joined']
            except KeyError:
                self.settings[member.server.id]['joined'] = 0
            try:
                self.settings[member.server.id]['joined'] += 1
                self.save_settings()
                if self.settings[member.server.id]['members'] != 0:
                    if (self.settings[member.server.id]['joined'] >= self.settings[member.server.id]['members']) and not (self.settings[member.server.id]['protected']):
                        self.settings[member.server.id]['protected'] = True
                        self.save_settings()
                        for channel in member.server.channels:
                            if (channel.id == self.settings[member.server.id]['channel']) and (self.settings[member.server.id]['channel'] != None):
                                await self.bot.send_message(channel, "Antiraid has been turned on, more than {} people joined within 8 seconds.".format(self.settings[member.server.id]['members']))
                await asyncio.sleep(8)
                self.settings[member.server.id]['joined'] = 0
                self.save_settings()
            except KeyError:
                pass
            try:
                if self.settings[member.server.id]['protected']:
                    for channel in member.server.channels:
                        if channel.id != self.settings[member.server.id]['channel']:
                            perms = discord.PermissionOverwrite()
                            perms.read_messages = False
                            perms.send_messages = False
                            await self.bot.edit_channel_permissions(channel, member, perms)
                        else:
                            await self.bot.send_message(channel, "{}, you have been muted in every channel because antiraid is on, if you are not here to raid just wait patiently and your permissions will be restored.".format(member.mention))
            except KeyError:
                return
        
def check_folders():
    if not os.path.exists("data/antiraid"):
        print("Creating data/antiraid folder...")
        os.makedirs("data/antiraid")
        
def check_files():
    if not os.path.exists("data/antiraid/settings.json"):
        print("Creating data/antiraid/settings.json file...")
        dataIO.save_json("data/antiraid/settings.json", {})
        
def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(AntiRaid(bot))
