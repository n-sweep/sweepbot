#!/usr/bin/env python3

import os
import json
from discord_bot.webhook import DiscordWebhook

d = os.path.dirname(os.path.realpath(__file__))
config_fp = os.path.join(d, 'discord_bot/config.json')
with open(config_fp, 'r') as f:
    data = json.load(f)
    hook = data['webhooks']['general']
    whid = hook['id']
    whtoken = hook['token']

def message(content):
    wh = DiscordWebhook(whid, whtoken)
    wh.send_message(f"{content} https://twitch.tv/n_sweep")

def main():
    wh = DiscordWebhook(whid, whtoken)
    wh.send_message("it's cellular automaton time https://twitch.tv/n_sweep")

if __name__ == '__main__':
    main()
