
"""Definition of the bot's barebones cog class."""

class Cog:
    """Base cog module. To be used as a template."""
    def __init__(self, bot):
        self.bot = bot
        self.loop = bot.loop
