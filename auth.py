import json
import random
import webbrowser
import urllib.parse as parse
from aiohttp import web, ClientSession


def generate_state(n=24):
    alpha = 'abcdefghijklmnopqrstuvwyz0123456789'
    return ''.join([random.choice(alpha) for _ in range(n)])


class Server(web.Application):

    auth_url = 'https://id.twitch.tv/oauth2/authorize'
    token_url = 'https://id.twitch.tv/oauth2/token'
    redirect = 'http://localhost:8080/auth'
    state = None

    def __init__(self):
        super().__init__()
        self.load_config()
        self.add_routes([
            web.get('/auth', self.handle_auth),
        ])
        # self.authorize()

    def run(self):
        web.run_app(self)

    def load_config(self):
        with open('./config.json', 'r') as f:
            self.config = json.load(f)

    def update_config(self, updates):
        self.config.update(updates)
        with open('./config.json', 'w') as f:
            json.dump(self.config, f)

    async def handle_auth(self, request):
        query = request.query
        # scope = query.get('scope')

        if self.state != query.get('state'):
            return web.Response(text='error: state mismatch')

        params = {
            'client_id': self.config['client_id'],
            'client_secret': self.config['client_secret'],
            'code': query.get('code'),
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect,
        }

        response = await self.retrieve_token(params)

        self.update_config({
            'access_token': response.get('access_token'),
            'refresh_token': response.get('refresh_token')
        })

        return web.Response(text='you may now close this window')

    async def retrieve_token(self, params):
        async with ClientSession() as session:
            async with session.post(self.token_url, params=params) as resp:
                return await resp.json()

    def authorize(self):
        self.state = generate_state()

        params = {
            'response_type': 'code',
            'client_id': self.config['client_id'],
            'redirect_uri': self.redirect,
            'scope': 'channel:moderate user:edit chat:read chat:edit',
            'state': self.state,
        }

        url = f'{self.auth_url}?{parse.urlencode(params)}'
        webbrowser.open(url)


def main():
    server = Server()
    server.run()


if __name__ == '__main__':
    main()
