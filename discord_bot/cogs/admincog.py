#!/usr/bin/env python
# Discord Bot cog!

import json
import discord
from discord.ext import commands

blue = 0x7289da
green = 0x43b581
yellow = 0xfaa61a
orange = 0xf04747


class AdminCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(pass_context=True, hidden=True)
	async def test(self, ctx):
		channels = ctx.guild.channels
		ch_names = [channel.name for channel in channels]
		roles = ctx.guild.roles
		role_names = [role.name for role in roles]
		print(ch_names)
		print(role_names)

	@commands.command(pass_context=True, hidden=True, aliases=['ignore'])
	async def ignore_channel(self, ctx):
		if str(self.bot.user.id) not in ctx.message.content:
			return

		with open(self.bot.config_fp, 'r+') as file:
			data = json.load(file)
			ch = ctx.channel
			if ch.id not in data['ignored_channels'].keys():
				data['ignored_channels'][ch.id] = {
					'name': ch.name,
					'server': {
						'name': ch.guild.name,
						'id': ch.guild.id
					}
				}

			await ctx.send("I will ignore messages in this channel.")

			file.seek(0)
			json.dump(data, file, indent=4)
			file.truncate()

	@commands.command(pass_context=True, hidden=True)
	async def welcome(self, ctx):
		if ctx.prefix != self.bot.config.get('admin_prefix') or ctx.message.author.id not in self.bot.config.get('admins'):
			return
		
		# todo: make this function only work on the welcome channel
		channel = ctx.channel
		messages = await channel.history().flatten()

		num_emoji = [':zero:',':one:',':two:',':three:',':four:',':five:',':six:',':seven:',':eight:',':nine:',':keycap_ten:']
		rules_list = [
			"Be kind to your fellow beings.",
			"Please keep self-promotion in the appropriate channels.",
			"Please post photos of your pets in the **#pets** text channel immediately."
		]
		rules = '\n'.join([f"- {num_emoji[i]} {rule}" for i, rule in enumerate(rules_list)])

		embed1 = discord.Embed(
			title="WELCOME TO *SWEEP'S FINEST* DISCORD SERVER",
			description="This is a discord server for my programming-focused twitch stream.",
			# url="",
			color=blue
		)
		embed1.add_field(
			name="SERVER RULES",
			value=f"\n{rules}\n\n----",
			inline=False
		)
		embed2 = discord.Embed(
			title="Acknowledgement",
			description=f"To gain access to the server (and the **#pets** channel), please click the :white_check_mark: emoji at the bottom of this message to show that you have read and understood the rules.\n\nIf there is no `BOT` online to let you in, please contact <@{self.bot.config.get('author')}> or a human admin directly or on Twitch.\n\nThank you!",
			color=green
		)
		if len(messages) < 2:
			# If the welcome messages don't exist, add them
			await ctx.send(content='Beep.', embed=embed1)
			msg = await ctx.send(content='Beep boop.', embed=embed2)
			await msg.add_reaction('✅')
		else:
			# If the welcome messages alread exist, edit them
			await messages[1].edit(content='Beep.', embed=embed1)
			await messages[0].edit(content='Beep boop.', embed=embed2)


	@commands.command(pass_context=True, hidden=True)
	async def cleanup(self, ctx):
		if ctx.prefix != self.bot.config.get('admin_prefix'):
			return
		msg = ctx.message
		channel = msg.channel
		messages = await channel.history().flatten()
		for m in messages:
			if channel.name in ['testing-ground', 'general', 'welcome']:
				await m.delete()
			elif m.content.startswith('.'):
				await m.delete()

	@commands.command(pass_context=True, hidden=True)
	async def reload(self, ctx):
		if ctx.prefix != self.bot.config.get('admin_prefix'):
			return
		self.bot.load_config()
		self.bot.load_cogs(reload=True)

	@commands.command(pass_context=True, hidden=True)
	async def setgame(self, ctx, *args):
		output = []
		if args:
			for a in args:
				nocap = ['and', 'as', 'as if', 'as long as', 'at', 'but', 'by', 'even if', 'for', 'from', 'if', 'if only',
						 'in', 'into', 'like', 'near', 'now that', 'nor', 'of', 'off', 'on', 'on top of', 'once', 'onto',
						 'or', 'out of', 'over', 'past', 'so', 'so that', 'than', 'that', 'till', 'to', 'up', 'upon',
						 'with', 'when', 'yet']
				output.append(a if a in nocap else a[0].upper() + a[1:])
			output = ' '.join(output)
			if ctx.prefix != self.bot.config.get('admin_prefix'):
				text = '{}, eh? Sure, that sounds fun.'.format(output)
				await ctx.send(text)
		await self.bot.change_playing(output)


def setup(bot):
	bot.add_cog(AdminCog(bot))
