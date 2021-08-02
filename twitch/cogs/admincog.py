#!/usr/bin/env python
# A Twitch bot cog!

import twitchio
from twitchio.ext import commands
from going_live import message

@commands.cog()
class AdminCog:
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='live')
    async def live(self, ctx, *args):
        text = ' '.join(args)
        message(text)