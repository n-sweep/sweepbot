import os
import asyncio
import json
import random
import urllib.parse as parse
import webbrowser
from aiohttp import web, ClientSession


def generate_state(n: int = 24) -> str:
    """Generate a state for validation"""
    alpha = 'abcdefghijklmnopqrstuvwyz0123456789'
    return ''.join([random.choice(alpha) for _ in range(n)])


class Server(web.Application):

    base_url = 'https://id.twitch.tv/oauth2/'
    auth_url = os.path.join(base_url, 'authorize')
    token_url = os.path.join(base_url, 'token')
    val_url = os.path.join(base_url, 'validate')
    redirect = 'http://localhost:8080/auth'
    state = None

    def __init__(self, config_fp: str) -> None:
        super().__init__()
        self.config_fp = config_fp
        self.load_config()
        self.add_routes([
            web.get('/auth', self.handle_auth),
        ])

    def run(self) -> None:
        """Wrapper for running the web app"""

        if not self.config.get('access_token'):
            asyncio.get_event_loop().run_until_complete(self.authorize(True))
        else:
            asyncio.get_event_loop().run_until_complete(self.validate())

        web.run_app(self)

    def load_config(self) -> None:
        """Load config from json file"""
        with open(self.config_fp, 'r') as f:
            self.config = json.load(f)

    def update_config(self, updates: dict) -> None:
        """Update and save config to json file

        Parameters
        ----------
        updates
            the content to be updated in the config dict
        """
        self.config.update(updates)
        with open(self.config_fp, 'w') as f:
            f.seek(0)
            json.dump(self.config, f, indent=4)
            f.truncate()

    async def handle_auth(self, request: web.Request) -> web.Response:
        """Authentication endpoint

        Parameters
        ----------
        request
            the request object from aiohttp

        Returns
        -------
        a web response
        """

        query = request.query
        if self.state != query.get('state'):
            return web.Response(text='error: state mismatch')

        params = {
            'client_id': self.config['client_id'],
            'client_secret': self.config['client_secret'],
            'code': query.get('code'),
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect,
        }

        async with ClientSession() as session:
            async with session.post(self.token_url, params=params) as resp:
                data = await resp.json()

        self.update_config({
            'access_token': data.get('access_token'),
            'refresh_token': data.get('refresh_token')
        })

        return web.Response(text='you may now close this window')

    async def authorize(self, open_browser: bool = False) -> None:
        """OAuth authorization code flow - requires sign-in and returns user access token

        Parameters
        ----------
        open_browser
            whether to open a browser or just print out the url
        """

        self.state = generate_state()

        payload = {
            'client_id': self.config['client_id'],
            'redirect_uri': self.redirect,
            'scope': self.config['scope'],
            'state': self.state,
            'response_type': 'code'
        }

        async with ClientSession() as session:
            async with session.get(self.auth_url, params=payload) as r:
                if open_browser:
                    webbrowser.open(str(r.url))
                else:
                    print(r.url)

    async def validate(self) -> None:
        """OAuth call to twitch API to validate the existing access token"""

        headers = {'Authorization': f'Bearer {self.config["access_token"]}'}

        async with ClientSession() as session:
            async with session.get(self.val_url, headers=headers) as resp:
                if resp.status == 200:
                    print('access token valid')
                else:
                    await self.refresh()

    async def refresh(self) -> None:
        """OAuth call to twitch API to refresh the access token"""

        payload = {
            'client_id': self.config['client_id'],
            'client_secret': self.config['client_secret'],
            'refresh_token': self.config['refresh_token'],
            'grant_type': 'refresh_token'
        }

        async with ClientSession() as session:
            async with session.post(self.token_url, params=payload) as resp:
                data = await resp.json()

        self.update_config({
            'access_token': data.get('access_token'),
            'refresh_token': data.get('refresh_token')
        })



def main():
    server = Server('./config.json')
    server.run()


if __name__ == '__main__':
    main()
