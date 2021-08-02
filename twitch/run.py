#!/usr/bin/env python
# A Twitch Bot

import os
from bot.core import Bot

def main():
    fp = os.path.join(os.path.dirname(__file__), 'config.json')
    bot = Bot(fp)
    bot.run()

if __name__ == '__main__':
    main()
