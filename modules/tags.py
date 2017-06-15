import discord
from discord.ext import commands
import os
import json
import aiohttp
from utils import checks

wrap = "```py\n{}\n```"

if os.path.isfile("data/tags.json"):
	pass
else:
	with open("data/tags.json", "w") as f:
		f.write("{}")

class Tags:
    def __init__(self, bot):
        self.bot = bot
        
    @commands.group(pass_context=True, invoke_without_command=True)
    async def tag(self, ctx, *, name:str):
        """Create tags for your server."""
        if ctx.invoked_subcommand is None:
            with open("data/tags.json", "r+") as f:
                db = json.load(f)
                try:
                    await self.bot.say(db[name])
                except:
                    await self.bot.say("Sorry, I couldn't find that tag...")

    @tag.command()
    @checks.botcom()
    async def add(self, name:str, *, content:str):
        """Add a tag for your server."""
        with open("data/tags.json", "r+") as f:
            db = json.load(f)
            db[name] = content
            with open("data/tags.json", "w") as f:
                json.dump(db, f)
                await self.bot.say(":white_check_mark:")
                
    @tag.command()
    @checks.botcom()
    async def delete(self, *, name:str):
        with open("data/tags.json", "r+") as f:
            db = json.load(f)
            try:
                db.pop(name)
                with open("tags.json", "w") as f:
                    json.dump(db, f)
            except:
                await self.bot.say("Fine...")
                
def setup(bot):
	bot.add_cog(Tags(bot))
