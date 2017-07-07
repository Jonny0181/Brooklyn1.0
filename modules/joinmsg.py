import discord
import json

with open('config.json') as f:
    config = json.load(f)
prefix = config['PREFIX']

class Joinmsg:
    def __init__(self, bot):
        self.bot = bot
        
    async def on_server_join(self, server):
        users = len([e.name for e in self.bot.get_all_members()])
        servers = len(self.bot.servers)
        e = discord.Embed(colour=discord.Colour.blue())
        e.set_thumbnail(url=server.me.avatar_url)
        e.add_field(name="Hi, my name is {}".format(self.bot.user.name), value="Thank you for adding me to your server. I'm going to have a great time here, and I hope you enjoy using me!", inline=False)
        e.add_field(name="My Features:", value="`1)` Music.\n`2)` Moderation.\n`3)` Utility.\n`4)` More will come, please be patient I am being recoded. :smiley:", inline=False)
        e.add_field(name="How To Use My Commands:", value="`1)` You will need a role Bot Commander for moderation commands.\n`2)` If  you don't want  to manual create the roles you can use the command `{0}commanderroles` but you will need to have the server permissions `manage_roles`.\n`3)` All my commands must start with the prefix `{0}`. Example: `{0}play`.\n`4)` If you want your server mods/admins to be able to use the moderation commands they will need the role \"Bot Commander\".\n\nOther than that you should be good to go! Thank you for choosing Brooklyn and have a great day!".format(prefix), inline=False)
        e.set_footer(text="Currently servering {} users and {} servers!".format(users, servers))
        await self.bot.send_message(server, embed=e)
        
def setup(bot):
    bot.add_cog(Joinmsg(bot))
