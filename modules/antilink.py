import discord
from discord.ext import commands
import os
from utils.dataIO import fileIO
import os
import discord
import asyncio
import datetime
import unicodedata
from utils import checks
from random import randint
from random import choice as randchoice

db_data = {"Toggle" : False, "No Invite" : False, "Toggle Blacklist" : False, "Blacklisted": {}}


class AntiLink:
    """This is an useful command for deleting discord invite links/ any links | text
    -Usage:
        -When an invite link is sent, I will delete it automatically
            Same case goes when someone edits a text to one which contains an invite link
        -When someone sends a blacklisted link, I will delete it automatically(words can also be supported)
            Same case goes when someone edits a text to one which contains the blacklisted word"""
    
    def __init__(self, bot):
        self.bot = bot
        self.link_data = "data/antilink/antilink.json"
    
    @checks.botcom()
    @commands.group(pass_context = True, no_pm = True)
    async def antilink(self, ctx):
        channel = ctx.message.channel
        server = ctx.message.server
        my = server.me
        data = fileIO(self.link_data, "load")
        if server.id not in data:
            data[server.id] = db_data
            fileIO(self.link_data, "save", data)
        if ctx.invoked_subcommand is None:
            e = discord.Embed(description="""b!antilink

Commands:
addword Adds word to the blacklist
toggle Enables or Disables the Antilink
antiinvite Enables or Disables the Antilink
links Enables or Disables the Antilink
status Shows antilink status
removeword Adds word to the blacklist

Type b!help command for more info on a command.
You can also type b!help category for more info on a category.""")
            e.set_author(name="Help for {}'s command group {}.".format(self.bot.user.name, ctx.command), icon_url=ctx.message.server.me.avatar_url)
            e.set_thumbnail(url=ctx.message.server.me.avatar_url)
            await self.bot.say(embed=e)

    @antilink.command(pass_context=True)
    async def status(self, ctx):
        """Shows antilink status."""
        channel = ctx.message.channel
        server = ctx.message.server
        directory = fileIO(self.link_data, "load")
        db = directory[server.id]
        if len(db["Blacklisted"]) != 0:
            words = "- {}".format("\n-".join(["{}".format(x) for x in db["Blacklisted"]]))
        else:
            words = "No Links/Words blacklisted for this server"
            colour = ''.join([randchoice('0123456789ABCDEF') for x in range(6)])
            colour = int(colour, 16)
            status = (str(db["Toggle"]).replace("True", "Enabled")).replace("False", "Disabled")
            e = discord.Embed()
            e.colour = colour
            e.description = "Showing AntiLink Settings For {0}\nDo {1.prefix}help {1.command.qualified_name} for more info".format(server.name, ctx)
            e.set_author(name = "AntiLink Settings")
            e.add_field(name = "AntiLink Status", value = status)
            e.add_field(name = "AntiInvite Enabled", value = db["No Invite"])
            e.add_field(name = "AntiLinks Enabled", value = db["Toggle Blacklist"])
            e.add_field(name = "Blacklisted Words", value = words, inline = False)
            e.set_footer(text = "AntiLink Settings", icon_url = server.icon_url)
            e.timestamp = ctx.message.timestamp
            try:
                await self.bot.send_message(channel, embed = e)
            except discord.Forbidden:
                msg = "```css\nAntiLink Settings for {0.name}.\nDo {1.prefix}help {1.command.qualified_name} for more info\n".format(server, ctx)
                msg += "AntiLink Status : {0}\nAntiInvite Enabled : {1}\nAntilinks Enabled : {2}\nBlacklisted Words: {3}\n```".format(status, db["No Invite"], db["Toggle Blacklist"], words)
                await self.bot.send_message(channel, msg)


    @antilink.command(pass_context = True)
    async def toggle(self, ctx):
        """Enables or Disables the Antilink"""
        server = ctx.message.server
        db = fileIO(self.link_data, "load")
        db[server.id]["Toggle"] = not db[server.id]["Toggle"]
        if db[server.id]["Toggle"] is True:
            msg = "Successfully Enabled the Antilinks System\nNote: I need the \"Manage Messages\" Permission to delete messages"
        else:
            msg = "I have successfully disabled the Antilinks System."
        await self.bot.reply(msg)
        fileIO(self.link_data, "save", db)

    @antilink.command(pass_context = True)
    async def antiinvite(self, ctx):
        """Enables or Disables the Antilink"""
        server = ctx.message.server
        db = fileIO(self.link_data, "load")
        db[server.id]["No Invite"] = not db[server.id]["No Invite"]
        if db[server.id]["No Invite"] is True:
            msg = "Successfully Enabled AntiInvite\nI will delete all invite links from now on\nNote: I need the \"Manage Messages\" Permission to delete messages"
        else:
            msg = "I have successfully disabled antiinvite."
        await self.bot.reply(msg)
        fileIO(self.link_data, "save", db)
        
    @antilink.command(pass_context = True)
    async def links(self, ctx):
        """Enables or Disables the Antilink"""
        server = ctx.message.server
        db = fileIO(self.link_data, "load")
        db[server.id]["Toggle Blacklist"] = not db[server.id]["Toggle Blacklist"]
        if db[server.id]["Toggle Blacklist"] is True:
            msg = "Successfully Enabled Antilinks\nI will delete all blacklisted links/words from now on\nNote: I need the \"Manage Messages\" Permission to delete messages"
        else:
            msg = "I have successfully disabled Antilinks and will not delete blacklisted links/words from now on."
        await self.bot.reply(msg)
        fileIO(self.link_data, "save", db)

    @antilink.command(pass_context = True, name = "addword", aliases = ["addlink"])
    async def _addlinks_(self, ctx, *words : str):
        """Adds word to the blacklist
        Note: You can add mutiple words to the blacklist
        Usage:
        b!antilink adword \"This is taken as a word\" linka linkb linkc
        b!antilink addword linka linkb linkc
        b!antilink addword \"blacklisted word\""""
        server = ctx.message.server
        data = fileIO(self.link_data, "load")
        if not words:
            await self.bot.reply("Please pass the words/links you want me to blacklist")
            return
        for word in words:
            data[server.id]["Blacklisted"][word] = True
        wordlist = " , ".join(["\"{}\"".format(e) for e in words])
        fmt = "Successfully added these words to the list.\n{}".format(wordlist)
        await self.bot.reply(fmt)
        fileIO(self.link_data, "save", data)

    @antilink.command(pass_context = True, name = "removeword", aliases = ["removelink"])
    async def _removelinks_(self, ctx, *words : str):
        """Adds word to the blacklist
        Note: You can add mutiple words to the blacklist
        Usage:
        b!antilink add \"This is taken as a word\" linka linkb linkc
        b!antilink add linka linkb linkc
        b!antilink add \"blacklisted word\""""
        server = ctx.message.server
        data = fileIO(self.link_data, "load")
        if not words:
            await self.bot.reply("Please pass the words/links you want me to blacklist")
            return
        in_word = []
        for word in words:
            if word in data[server.id]["Blacklisted"]:
                in_word.append(word)
                del data[server.id]["Blacklisted"][word]
        wordlist = " , ".join(["\"{}\"".format(e) for e in in_word])
        fmt = "Successfully removed these words from the list.\n{}".format(wordlist)
        await self.bot.reply(fmt)
        fileIO(self.link_data, "save", data)

    async def on_message(self, message):
        data = fileIO(self.link_data, "load")
        if message.channel.is_private:
            return
        else:
            pass
        if not message.server.id in data:
            data[message.server.id] = db_data
            fileIO(self.link_data,"save", data)
        else:
            pass
        directory = fileIO(self.link_data, "load")
        db = directory[message.server.id]
        channel = message.channel
        idk = message.content
        if db["Toggle"] is True and db["No Invite"] is True:
            check = None
            if ("discord.gg/" in message.content) or ("discord" in idk and "." in idk and "gg" in idk and "/" in idk) or ("discordapp.com/invite/" in message.content) or ("discord.me/" in message.content) or ("discordapp" in idk and "." in idk and "com" in idk and "/" in idk and "invite" in idk and "/" in idk):
                check = True
            else:
                pass
            embeds = message.embeds
            if len(embeds) > 0 and message.author != self.bot.user:
                edb = embeds[0]
                if "type" in edb and edb["type"] == "rich":
                    des = edb["description"] if "description" in edb else "None"
                    tex = edb["title"] if "title" in edb else "None"
                    nam = edb["author"]["name"] if "author" in edb and "name" in edb["author"] else "None"
                else:
                    des = "None"
                    tex = "None"
                    nam = "None"
                if ("discord.gg/" in des) or ("discord" in des and "." in des and "gg" in des and "/" in des) or ("discordapp.com/invite/" in des) or ("discord.me/" in des) or ("discordapp" in des and "." in des and "com" in des and "/" in des and "invite" in des and "/" in des):
                    check = True
                else:
                    pass
                if ("discord.gg/" in tex) or ("discord" in tex and "." in tex and "gg" in tex and "/" in tex) or ("discordapp.com/invite/" in tex) or ("discord.me/" in tex) or ("discordapp" in tex and "." in tex and "com" in tex and "/" in tex and "invite" in tex and "/" in tex):
                    check = True
                else:
                    pass
                if ("discord.gg/" in nam) or ("discord" in nam and "." in nam and "gg" in nam and "/" in nam) or ("discordapp.com/invite/" in nam) or ("discord.me/" in nam) or ("discordapp" in nam and "." in nam and "com" in nam and "/" in nam and "invite" in nam and "/" in nam):
                    check = True
                else:
                    pass
            else:
                pass
            if check is True:
                try:
                    await self.bot.delete_message(message)
                except discord.Forbidden:
                    pass
                except discord.NotFound:
                    fmt = "{0.author.mention}, **Please do not send invite links in this server**".format(message)
                    try: 
                        await self.bot.send_message(channel, fmt)
                    except discord.Forbidden:
                        try:
                            await self.bot.send_message(author, fmt)
                        except discord.Forbidden:
                            pass
                else:
                    fmt = "{0.author.mention}, **Please do not send invite links in this server**".format(message)
                    try: 
                        await self.bot.send_message(channel, fmt)
                    except discord.Forbidden:
                        try:
                            await self.bot.send_message(author, fmt)
                        except discord.Forbidden:
                            pass
        else:
            pass
        if db["Toggle"] is True and db["Toggle Blacklist"] is True:
            check = None
            embeds = message.embeds
            edb = None
            if len(embeds) > 0:
                edb = embeds[0]
            des = "None"
            tex = "None"
            nam = "None"
            if edb is not None:
                if edb["type"] == "rich":
                    des = edb["description"] if "description" in edb else "None"
                    tex = edb["title"] if "title" in edb else "None"
                    nam = edb["author"]["name"] if "author" in edb and "name" in edb["author"] else "None"
                else:
                    pass
            else:
                des = "None"
                tex = "None"
                nam = "None"
            some_list = " ".join(e for e in [des, tex, nam, message.content])
            for word in db["Blacklisted"]:
                if word in some_list:
                    check = True
            if check is True:
                try:
                    await self.bot.delete_message(message)
                except discord.Forbidden:
                    pass
                except discord.NotFound:
                    pass
                else:
                    pass
    async def on_message_edit(self, before, after):
        data = fileIO(self.link_data, "load")
        if before.channel.is_private:
            return
        else:
            pass
        if before.server.id not in data:
            data[before.server.id] = db_data
            fileIO(self.link_data,"save",data)
        directory = fileIO(self.link_data, "load")
        db = directory[before.server.id]
        channel = before.channel
        if not before.content != after.content:
            pass
        else:
            message = after
            idk = message.content
            if db["Toggle"] is True and db["No Invite"] is True:
                check = None
                if ("discord.gg/" in message.content) or ("discord" in idk and "." in idk and "gg" in idk and "/" in idk) or ("discordapp.com/invite/" in message.content) or ("discord.me/" in message.content) or ("discordapp" in idk and "." in idk and "com" in idk and "/" in idk and "invite" in idk and "/" in idk):
                    check = True
                else:
                    pass
                embeds = message.embeds
                if len(embeds) > 0:
                    edb = embeds[0]
                    if "type" in edb and edb["type"] == "rich":
                        des = edb["description"] if "description" in edb else "None"
                        tex = edb["title"] if "title" in edb else "None"
                        nam = edb["author"]["name"] if "author" in edb and "name" in edb["author"] else "None"
                    else:
                        des = "None"
                        tex = "None"
                        nam = "None"
                    if ("discord.gg/" in des) or ("discord" in des and "." in des and "gg" in des and "/" in des) or ("discordapp.com/invite/" in des) or ("discord.me/" in des) or ("discordapp" in des and "." in des and "com" in des and "/" in des and "invite" in des and "/" in des):
                        check = True
                    else:
                        pass
                    if ("discord.gg/" in tex) or ("discord" in tex and "." in tex and "gg" in tex and "/" in tex) or ("discordapp.com/invite/" in tex) or ("discord.me/" in tex) or ("discordapp" in tex and "." in tex and "com" in tex and "/" in tex and "invite" in tex and "/" in tex):
                        check = True
                    else:
                        pass
                    if ("discord.gg/" in nam) or ("discord" in nam and "." in nam and "gg" in nam and "/" in nam) or ("discordapp.com/invite/" in nam) or ("discord.me/" in nam) or ("discordapp" in nam and "." in nam and "com" in nam and "/" in nam and "invite" in nam and "/" in nam):
                        check = True
                    else:
                        pass
                if check is True:
                    try:
                        await self.bot.delete_message(message)
                    except discord.Forbidden:
                        pass
                    except discord.NotFound:
                        fmt = "{0.author.mention}, **Please do not send invite links in this server**".format(message)
                        try: 
                            await self.bot.send_message(channel, fmt)
                        except discord.Forbidden:
                            try:
                                await self.bot.send_message(author, fmt)
                            except discord.Forbidden:
                                pass
                    else:
                        fmt = "{0.author.mention}, **Please do not send invite links in this server**".format(message)
                        try: 
                            await self.bot.send_message(channel, fmt)
                        except discord.Forbidden:
                            try:
                               await self.bot.send_message(author, fmt)
                            except discord.Forbidden:
                                pass
            else:
                pass
            if db["Toggle"] is True and db["Toggle Blacklist"] is True:
                check = None
                embeds = message.embeds
                edb = None
                if len(embeds) > 0:
                    edb = embeds[0]
                des = "None"
                tex = "None"
                nam = "None"
                if edb is not None:
                    if edb["type"] == "rich":
                        des = edb["description"] if "description" in edb else "None"
                        tex = edb["title"] if "title" in edb else "None"
                        nam = edb["author"]["name"] if "author" in edb and "name" in edb["author"] else "None"
                    else:
                        pass
                else:
                    des = "None"
                    tex = "None"
                    nam = "None"
                some_list = " ".join(e for e in [des, tex, nam, message.content])
                for word in db["Blacklisted"]:
                    if word in some_list:
                        check = True
                if check is True:
                    try:
                        await self.bot.delete_message(message)
                    except discord.Forbidden:
                        pass
                    except discord.NotFound:
                        pass
                    else:
                        pass
    async def on_server_join(self, server):
        data = fileIO(self.link_data, "load")
        data[server.id] = db_data
        fileIO(self.link_data, "save", data)
        
def check_folders():
    if os.path.exists("data/antilink"):
        pass
    else:
        try:
            print("Creating data/antilink folder...")
            os.makedirs("data/antilink")
        except FileExistsError:
            pass
        else:
            print("created data/antilinks folder")

def check_files():
    f = "data/antilink/antilink.json"
    if not fileIO(f, "check"):
        print("Creating antilink antilink.json...")
        fileIO(f, "save", {})

def setup(bot):
    check_folders()
    check_files()
    n = AntiLink(bot)
    bot.add_cog(n)
