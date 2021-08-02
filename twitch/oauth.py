#!/usr/bin/env python3

import os
import json
import hmac
import hashlib
import asyncio
import aiohttp
import requests
import numpy as np
import webbrowser as wb

ff = wb.get('/mnt/c/"Program Files"/"Mozilla Firefox"/firefox.exe %s')
alpha = 'abcdefghijklmnopqrstuvwxyz1234567890'
d = os.path.dirname(os.path.realpath(__file__))
fp = os.path.join(d, 'config.json')

with open(fp, 'r+') as f:
    config = json.load(f)


def generate_secret(n=24):
    secret = np.random.choice(list(alpha), size=n)
    return ''.join(secret)


async def verify_webhook_signature(request, secret):
    signature = request.headers['Twitch-Eventsub-Message-Signature'].replace("sha256=", '')
    msg_id = request.headers['Twitch-Eventsub-Message-Id']
    msg_ts = request.headers['Twitch-Eventsub-Message-Timestamp']
    body = await request.text()
    hmac_msg = (msg_id + msg_ts + body)

    expected_signature = hmac.new(
        secret.encode(),
        msg=hmac_msg.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    return signature == expected_signature

async def get_irc_token(open_browser=False):
    response_type = 'token'
    scope = 'user:edit chat:read chat:edit'
    endpoint = 'irc'
    return await authorize_user(response_type, scope, endpoint, open_browser)


async def get_access_token(open_browser=False):
    response_type = 'code'
    scope = 'user:edit chat:read chat:edit'
    endpoint = 'code'
    return await authorize_user(response_type, scope, endpoint, open_browser)


async def authorize_user(response_type, scope, endpoint, open_browser=False):
    """
        OAuth authorization code flow - requires sign-in and returns user access token
    """
    
    state = generate_secret()

    payload = {
        'client_id': config['CLIENT_ID'],
        'redirect_uri': f'http://localhost:8080/twitch/{endpoint}',
        'response_type': response_type,
        'scope': scope,
        'state': state
    }

    async with aiohttp.ClientSession() as session:
        async with session.get('https://id.twitch.tv/oauth2/authorize', params=payload) as r:
            if open_browser:
                ff.open(str(r.url))
            else:
                print(r.url)

    return state

async def verify_user_access_token(code):
    payload = {
        'client_id': config['CLIENT_ID'],
        'client_secret': config['CLIENT_SECRET'],
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': 'http://localhost:8080/'
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post('https://id.twitch.tv/oauth2/token', params=payload) as r:
            return await r.json()

def get_app_access_token():
    """
        OAuth client credentials flow - returns app access token
    """
    payload = {
        'client_id': config['CLIENT_ID'],
        'client_secret': config['CLIENT_SECRET'],
        'grant_type': 'client_credentials'
    }

    r = requests.post('https://id.twitch.tv/oauth2/token', payload)

    token = r.json()['access_token']

    with open(fp, 'r+') as f:
                conf = json.load(f)
                conf['APP_TOKEN'] = token
                f.seek(0)
                json.dump(conf, f, indent=4)
                f.truncate()


async def revoke(token):
    payload = {
        'client_id': config['CLIENT_ID'],
        'token': token
    }

    async with aiohttp.ClientSession() as session:
        async with session.post('https://id.twitch.tv/oauth2/revoke', params=payload) as r:
            print(r)
    headers = {
        'Client-ID': config['CLIENT_ID'],
        'Authorization': 'Bearer ' + get_access_token()
        }

    r = requests.get('https://api.twitch.tv/helix/eventsub/subscriptions',
                        headers=headers)

    # delete all subs
    for sub in dict(r.json())['data']:
        requests.delete('https://api.twitch.tv/helix/eventsub/subscriptions?id=' + sub['id'],
                            headers=headers)


async def main():
    state = await get_irc_token(open_browser=True)
    print(state)


if __name__ == '__main__':
    # asyncio.run(main())
    get_app_access_token()
