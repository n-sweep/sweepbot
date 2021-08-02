#!/usr/bin/env python3

import json
import hmac
import hashlib
from aiohttp import web
from twitch.oauth import verify_user_access_token, verify_webhook_signature

text = """hello, friend\n\nyou may close this window now"""

class Endpoint(web.Application):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.conf_fp = bot.conf_fp
        self.add_routes([
            web.route('*', '/', self.hello),
            web.route('*', '/twitch/webhook', self.webhook),
            web.route('*', '/twitch/auth', self.auth),
            web.route('*', '/twitch/irc', self.irc)
        ])
    
    def run(self):
        web.run_app(self)

    async def hello(self, request):
        return web.Response(text=text)
    
    async def webhook(self, request):
        data = await request.json()
        subscription = data['subscription']
        
        if subscription['status'] == 'webhook_callback_verification_pending':
            if await verify_webhook_signature(request, 'nineteenninetynine'):
                print('webhook subscription accepted')
                return web.Response(text=data['challenge'], status=200)
            return web.Response(status=403)
        if subscription['type'] == 'channel.follow':
            event = data['event']
            print('here is a follow event triggered by: {}'.format(event['user_name']))
            return web.Response(status=200)
    
    async def irc(self, request):
        return web.Response(text=text)

    async def auth(self, request):
        q = dict(request.query)
        state = q['state']
        if state in self.bot.secrets:
            self.bot.secrets.remove(state)
            payload = await verify_user_access_token(q['code'])
            with open(self.conf_fp, 'r+') as f:
                conf = json.load(f)
                conf['ACCESS_TOKEN'] = payload['access_token']
                conf['TOKEN_METADATA'] = payload
                self.bot.load_config()
                f.seek(0)
                json.dump(conf, f, indent=4)
                f.truncate()
        return web.Response(text=text)


if __name__ == '__main__':
    e = Endpoint()
    e.run()
