from discord.ext import commands
import discord.utils
import json

with open('config.json') as f:
	config = json.load(f)

ownerid = config['OWNER_ID']

def is_owner_check(message):
    return message.author.id == ownerid

def is_owner():
    return commands.check(lambda ctx: is_owner_check(ctx.message))

def botcom():
    return commands.check(lambda ctx: is_bot_com(ctx.message))
	
def is_bot_com(message):
	for role in message.server.roles:
		if role.name == "Bot Commander":
			if role in message.author.roles:
				return True
