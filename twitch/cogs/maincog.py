#!/usr/bin/env python
# A Twitch bot cog!

import asyncio
import twitchio
from random import choice
from twitchio.ext import commands

@commands.cog()
class MainCog:
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
    
    async def event_ready(self):
        'Called once when the bot connects'
        print(f"{self.config.get('BOT_NICK')} is online!")
        ws = self.bot._ws
        chan = '#' + self.config.get('BROADCASTER_NAME')
        nick =self.config.get('BOT_NICK')
        # await ws.send_privmsg(chan, f"I am the bot with no name. {nick}, at your service.")

    async def event_raw_data(self, data):
        print(f'[RAW EVENT]:  {data}')
    
    async def event_webhook(self, data):
        print(f'[WEBHOOK EVENT]:  {data}')
    
    async def event_raw_pubsub(self, data):
        await self.bot.party(0.25, 10)
        print(f'[PUBSUB EVENT]:  {data}')
    
    async def event_message(self, ctx):
        'Runs each time a message is sent in chat'

        # make sure the bot ignores itself
        if ctx.author.name.lower() == self.config.get('BOT_NICK').lower():
            return
        
        self.bot.session_msgs += 1
        
        if 'hello' in ctx.content:
            greetings = ['Greetings', 'Hi', 'Hello', 'Heya', 'Howdy']
            await ctx.channel.send(f"{choice(greetings)}, @{ctx.author.name}")

        if 'MrDestructoid' in ctx.content:
            text  = "MrDestructoid"
            if f"@{self.config.get('BOT_NICK')}" in ctx.content:
                await ctx.channel.send(f"@{ctx.author.name} no u " + text)
            else:
                await ctx.channel.send(text)
        
        # await self.bot.handle_commands(ctx)
    
    @commands.command(name='hydrate')
    async def hydrate(self, ctx):
        await ctx.send(f"Hey @n_sweep, @{ctx.author.name} wants you to remember to stay hydrated!")
    
    @commands.command(name='discord')
    async def discord(self, ctx):
        link = self.config.get('DISCORD_LINK')
        await ctx.send(f"Our Discord server is open for business! {link}")
 
    @commands.command(name='shoutout', aliases=['so'])
    async def shoutout(self, ctx, *args):
        if ctx.author.is_mod:
            username = args[0].strip('@')
            u = (await self.bot.get_users(username))[0]
            txt = f"Make sure to check out {u.display_name} at http://twitch.tv/{u.display_name}"
            await ctx.send(txt)
    
    @commands.command(name='git', aliases=['github', 'guthib'])
    async def git(self, ctx):
        await ctx.send('https://github.com/n-sweep')

    @commands.command(name='test')
    async def test(self, ctx):
        pass
