#!/usr/bin/env python3
# Run Discord & Twitch Bots Simultaneously

import os
import asyncio
from discord_bot.bot.core import Bot as DiscordBot
from twitch.bot.core import Bot as TwitchBot
from twitch.endpoint import Endpoint


def main():

    # Get working directory & event loop
    d = os.path.dirname(os.path.realpath(__file__))
    loop = asyncio.get_event_loop()

    # Create bots
    disc_bot = DiscordBot(os.path.join(d, 'discord_bot/config.json'))
    twit_bot = TwitchBot(os.path.join(d, 'twitch/config.json'))
    
    # Loop bots
    loop.create_task(disc_bot.loop_start())
    loop.create_task(twit_bot.loop_start())

    # Create & run server endpoint
    app = Endpoint(bot=twit_bot)
    app.run()

if __name__ == '__main__':
    main()