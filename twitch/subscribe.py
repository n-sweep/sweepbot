#!/usr/bin/env python3

import os
import json
import asyncio
import aiohttp
import requests
import numpy as np
import webbrowser as wb

alpha = 'abcdefghijklmnopqrstuvwxyz1234567890'
d = os.path.dirname(os.path.realpath(__file__))
fp = os.path.join(d, 'config.json')

with open(fp, 'r+') as f:
    config = json.load(f)


def generate_secret(n=24):
    secret = np.random.choice(list(alpha), size=n)
    return ''.join(secret)

async def subscribe():

    # secret = generate_secret(10)
    endpoint = 'https://wise-sloth-23.loca.lt/twitch/webhook'
    
    headers = {
        'Client-ID': config['CLIENT_ID'],
        'Authorization': 'Bearer ' + config['APP_TOKEN'],
        'Content-Type': 'application/json'
    }

    payload = {
        'type': 'channel.follow',
        'version': '1',
        'condition': {
            'broadcaster_user_id': str(config['BROADCASTER_ID'])
        },
        'transport': {
            'method': 'webhook',
            'callback': endpoint,
            'secret': 'nineteenninetynine'
        }
    }

    async with aiohttp.ClientSession() as session:
        async with session.post('https://api.twitch.tv/helix/eventsub/subscriptions',
                        data=json.dumps(payload), headers=headers) as r:
            print(dict(await r.json()))


def delete_subs():
    headers = {
        'Client-ID': config['CLIENT_ID'],
        'Authorization': 'Bearer '  + config['APP_TOKEN']
        }

    r = requests.get('https://api.twitch.tv/helix/eventsub/subscriptions',
                        headers=headers)

    # delete all subs
    for sub in dict(r.json())['data']:
        print(sub)
        requests.delete('https://api.twitch.tv/helix/eventsub/subscriptions?id=' + sub['id'],
                            headers=headers)


async def main():
    # delete_subs()
    await subscribe()


if __name__ == '__main__':
    asyncio.run(main())
