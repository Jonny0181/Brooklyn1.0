from discord.ext import commands
import discord.utils
import json

def is_owner_check(message):
    return message.author.id == "146040787891781632"

def is_owner():
    return commands.check(lambda ctx: is_owner_check(ctx.message))

def check_perm(ctx, perms):
    msg = ctx.message
    if is_owner_check(msg):
        return True
    channel = msg.channel
    author = msg.author
    resolved = channel.permissions_for(author)
    return all(getattr(resolved, name, None) == value for name, value in perms.items())

def role_or_perm(ctx, check, **perms):
    if check_perm(ctx, perms):
        return True
    channel = ctx.message.channel
    author = ctx.message.author
    if channel.is_private:
        return False
    role = discord.utils.find(check, author.roles)
    return role is not None

def mod_or_perm(**perms):
    def predicate(ctx):
        return role_or_perm(ctx, lambda r: r.name in ('Mod', 'Admin'), **perms)
    return commands.check(predicate)

def admin_or_perm(**perms):
    def predicate(ctx):
        return role_or_perm(ctx, lambda r: r.name == 'Admin', **perms)
    return commands.check(predicate)



def botcom():
    return commands.check(lambda ctx: is_bot_com(ctx.message))
	
def is_bot_com(message):
	for role in message.server.roles:
		if role.name == "Bot Commander":
			if role in message.author.roles:
				return True
