#!/usr/bin/env python
# Twitch bot guts

import os
import sys
import json
import twitchio
from threading import local
from twitchio import webhook
from random import choice, randint
from asyncio import sleep
from twitchio.ext import commands
from twitchio.errors import AuthenticationError

sys.path.insert(0, os.path.abspath('..'))

from utils import Timer, Periodic
from pyHS100 import SmartBulb


bulb = SmartBulb('192.168.0.246')

light_colors = {
    'red': 1,
    'orange': 25,
    'yellow': 50,
    'green': 125,
    'blue': 220,
    'purple': 300
}

class Bot(commands.Bot):

    config = None
    light_timer = None
    discord_timer = None
    session_msgs = 0
    party_switch = False
    secrets = []

    def __init__(self, config_fp):
        # Set config filepath & load config
        self.conf_fp = config_fp
        self.load_config()

        # Pass in credentials
        super().__init__(
            irc_token='oauth:' + self.config.get('IRC_TOKEN'),
            client_id=self.config.get('CLIENT_ID'),
            client_secret=self.config.get('CLIENT_SECRET'),
            nick=self.config.get('BOT_NICK'),
            prefix=self.config.get('PREFIX'),
            initial_channels=['#' + self.config.get('BROADCASTER_NAME')]
        )

        self.load_cogs()
        self.discord_timer = Periodic(1200, self.discord_periodic)
        bulb.set_color_temp(6500)
    
    async def loop_start(self):
        await super().start()

    async def party(self, i, t):
        self.party_switch = True
        for _ in range(int(t/i)):
            if not self.party_switch:
                break
            c = randint(0, 360)
            bulb.set_hsv(c, 100, 100)
            await sleep(i)
        bulb.set_color_temp(6500)

    def load_cogs(self):
        for c in self.config.get('COGS'): # ['maincog', 'admincog']
            ext = 'twitch.cogs.' + c
            self.load_module(ext)

    def load_config(self):
        'Loads our json config file based on filepath given on bot instantiation'
        with open(self.conf_fp, 'r+') as f:
            self.config = json.load(f)

    async def close(self):
        print('closing...')
        await super().close()
    
    async def discord_periodic(self):
        if self.session_msgs < 10:
            return
        link = self.config.get('DISCORD_LINK')
        txt = f"Our Discord server is open for business! {link}"
        ws = self._ws
        await ws.send_privmsg('#' + self.config.get('BROADCASTER_NAME'),txt)
        self.session_msgs = 0

    @commands.command(name='today')
    async def today(self, ctx, *args):
        'Will return or set the value of the [today] config attribute'
        if len(args):
            if ctx.author.id == self.config.get('BROADCASTER_ID'):
                # If an admin had provided arguments with this command, update the command value to reflect the new arguemnts.
                with open(self.conf_fp, 'r+') as f:
                    conf = json.load(f)
                    conf['TODAY'] = ' '.join(args)
                    f.seek(0)
                    json.dump(conf, f, indent=4)
                    f.truncate()
                self.load_config()
                await ctx.send("Command [!today] set successfully!")
            else:
                await ctx.send(f"Sorry @{ctx.author.name}, only an admin can reset the value of this command.")
        else:
            await ctx.send(self.config.get('TODAY'))
    
    @commands.command(name='music', aliases=['tunes'])
    async def music(self, ctx, *args):
        'Will return or set the value of the [music] config attribute'
        if len(args):
            if ctx.author.id == self.config.get('BROADCASTER_ID'):
                # If an admin had provided arguments with this command, update the command value to reflect the new arguemnts.
                with open(self.conf_fp, 'r+') as f:
                    conf = json.load(f)
                    conf['MUSIC'] = ' '.join(args)
                    f.seek(0)
                    json.dump(conf, f, indent=4)
                    f.truncate()
                self.load_config()
                await ctx.send("Command [!music] set successfully!")
            else:
                await ctx.send(f"Sorry @{ctx.author.name}, only an admin can reset the value of this command.")
        else:
            await ctx.send(self.config.get('MUSIC'))

    @commands.command(name='light', aliases=['color', 'colour'])
    async def light(self, ctx, *args):
        'Changes the color of my TPLink LB130 smart bulb'

        if args:
            if 'reset' in args[0].lower() and ctx.author.is_mod:
                if self.light_timer:
                    self.light_timer.cancel()
                if self.party_switch:
                    self.party_switch = False
                bulb.set_color_temp(6500)
                return
            
            if 'party' in args[0].lower():
                t = int(args[1]) if len(args) > 1 and args[1].isdigit() else 10
                await ctx.send('Wimmy wham wham wozzle! Party on dudes!')
                await self.party(0.25, t)
                return

            # TODO: clean up this junk
            try: 
                color = int(float(args[0]))
            except:
                if args[0] in light_colors:
                    color = light_colors[args[0]]
        else:
            color = randint(0,360)

        if 0 <= color <= 360:
            bulb.set_hsv(color, 100, 100)
            if self.light_timer:
                self.light_timer.cancel()
            self.light_timer = Timer(600, lambda: bulb.set_color_temp(6500))
        else:
            await ctx.send(f"@{ctx.author.name} !light can take an integer value from 0 to 360.")
