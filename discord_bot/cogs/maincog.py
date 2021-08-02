#!/usr/bin/env python
# Discord Bot cog!

from random import choice
import discord
from discord.ext import commands

blue = 0x7289da
green = 0x43b581
yellow = 0xfaa61a
orange = 0xf04747


class MainCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		bot.remove_command('help')

		@bot.event
		async def on_ready():
			print('\nLogged in as')
			print(bot.user.name)
			print(bot.user.id)
			print('Discord.py Version: {}'.format(discord.__version__))
			print('--------\n')

		@bot.event
		async def on_raw_reaction_add(payload):
			auth = payload.member
			if auth.id == bot.user.id:
				return

			# todo: we can make this check better
			guild_id = payload.guild_id == 796036813424427009
			channel_id = payload.channel_id == 796036814402093078
			emoji_name = payload.emoji.name == '✅'

			if guild_id and channel_id and emoji_name:
				# Give 'user' role to a new user to agrees to the rules with the appropriate reaction
				role = discord.utils.get(auth.guild.roles, name='user')
				await auth.add_roles(role)
				
				# Remove the User added reaction
				channel = await bot.fetch_channel(payload.channel_id)
				msg = await channel.fetch_message(payload.message_id)
				await msg.remove_reaction(payload.emoji, auth)

		@bot.event
		async def on_message(msg):
			try:
				ctx = await bot.get_context(msg)
				auth = msg.author
				if not ctx.valid or str(ctx.channel.id) in bot.config['ignored_channels'].keys():
					return
				if ctx.prefix == bot.config.get('admin_prefix'):
					await msg.delete()
					if auth.id in bot.config.get('admins'):
						pass
					else:
						return
				if True:
					await bot.invoke(ctx)
			except Exception as e:
				print(e)

		@bot.event
		async def on_command_error(ctx, error):
			print(error)
			if isinstance(error, commands.CommandNotFound):
				if ctx.prefix != bot.config.get('admin_prefix'):
					auth = ctx.message.author
					text = "Sorry <@{}>, I don't understand. Try `!help` for a list of commands I can respond to."
					await ctx.send(text.format(auth.id))
			else:
				raise error
		
		@bot.event
		async def on_member_update(before, after):
			print(before)
			print(after)

	@commands.command(description='Greets the caller.', pass_context=True, aliases=['greet', 'hi', 'hey'], hidden=True)
	async def hello(self, ctx, *args):
		"""
		Sends a greeting to the user who called the command.
		"""
		
		greetings = ['Greetings', 'Hi', 'Hello', 'Howdy', 'Hey']
		text = '{} <@!{}>.'.format(choice(greetings), ctx.message.author.id)
		await ctx.send(text)

	@commands.command(description='Pings the bot and returns the latency in seconds.', pass_context=True, hidden=True)
	async def ping(self, ctx):
		"""
		Pings the bot and returns the latency in seconds.
		"""

		latency = self.bot.latency
		await ctx.send('!pong ({})'.format(latency))

	@commands.command(description='Returns an info card for the bot.', pass_context=True)
	async def info(self, ctx):
		embed = discord.Embed(title="**{}**".format(self.bot.config['name']),
							 description=self.bot.config['description'],
							  color=yellow)
		embed.add_field(name='Author', value='<@{}>'.format(self.bot.config['author']))
		embed.add_field(name='Commands', value='I can respond to some commands, type **!commands** for a list.',
						inline=False)

		await ctx.send(embed=embed)

	@commands.command(pass_context=True, hidden=True, aliases=['command', 'commands'])
	async def help(self, ctx, *args):
		cmds = {c.name: c for c in self.bot.commands}
		prefix = self.bot.config.get('prefix')
		if args and args[0] in cmds:
			cmd = cmds[args[0]]
			embed = discord.Embed(title='Command: `{}{}`'.format(prefix, cmd.name), description=cmd.help,
								  color=yellow)
		else:
			embed = discord.Embed(title="**{}**".format(self.bot.config['name']),
								  description="Here's what I can do.",
								  color=yellow)
			text = []
			tmp = ' - `{}{}`  *{}*'
			help = tmp.format(prefix, 'help', 'Returns this message.')

			for cmd in cmds.values():
				if not cmd.hidden:
					text.append(tmp.format(prefix, cmd.name, cmd.description))

			text.sort()
			text.append(help + '\n\n\n*Try* `{}help command` *for information on individual commands*'.format(prefix))
			embed.add_field(name='**Available Commands:**', value='\n'.join(text), inline=False)

		await ctx.send(embed=embed)


def setup(bot):
	bot.add_cog(MainCog(bot))
