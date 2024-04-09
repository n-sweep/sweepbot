import json
from twitchio.ext import commands
import logging

logging.basicConfig(filename='/mnt/app/test.log', level=logging.INFO)

class Bot(commands.Bot):

    channel = 'n_sweep'
    today_msg = "I have no idea what we are doing."

    def __init__(self):
        super().__init__(
            token=self.access_token,
            prefix='!',
            initial_channels=[self.channel]
        )

    @property
    def config(self):
        with open("/mnt/app/config.json", 'r') as f:
            return json.load(f)

    @property
    def access_token(self):
        return self.config['access_token']

    async def event_ready(self):
        # chan = self.get_channel(self.channel)
        logging.info(f'Logged in as | {self.nick}')
        logging.info(f'User id is | {self.user_id}')
        # await chan.send("I am the bot with no name. sweep_bot at your service.")

    async def event_message(self, message):
        author = message.author.name if message.author else 'bot'
        logging.info(f'{author}: {message.content}')
        chk_string = message.content.lower()

        if message.echo:
            return

        if "mrdestructoid" in chk_string:
            await message.channel.send('MrDestructoid')

        await self.handle_commands(message)

    # [TODO]: now playing? requires spotify api. cmus?

    @commands.command()
    async def today(self, ctx: commands.Context):
        msg = ctx.message
        author = msg.author
        await msg.channel.send(f"{author.is_mod}")

    @commands.command(aliases=("so"))
    async def shoutout(self, ctx: commands.Context):
        username = ctx.message.content.split(' ')[1]
        user = self.get_user(username.replace('@', ''))
        if user:
            await user.shoutout()
        else:
            await ctx.send(f'join us in following {username} immediately MrDestructoid')


bot = Bot()
bot.run()
