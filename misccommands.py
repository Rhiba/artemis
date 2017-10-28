import discord
import json
import psycopg2
import random
from discord.ext import commands
from urllib.parse import urlparse
import requests
from command import Command

class hello(Command):
	def call(ctx,args):
		"""[name] - Says hello to you or another!"""
		if len(args) < 1:
			return "Hi {0.author.name}!".format(ctx)
		else:
			return "Hi {1}, love {0.author.name}!".format(ctx,args[0])

class say(Command):
	def call(ctx,args):
		return " ".join(args)

	'''
	@commands.command(aliases=["choice"])
	async def flip(self,*choices : str):
		"""<choice1> <choice2> [choice 3] - Chooses for you!"""
		await self.bot.say(random.choice(choices))

	@commands.command()
	async def listaliases(self,command : str):
		out_string = "Aliases for {0}: ".format(command)
		if command in self.bot.commands:
			if self.bot.commands[command].aliases:
				for alias in self.bot.commands[command].aliases:
					out_string = out_string + alias
					if not self.bot.commands[command].aliases[-1] == alias:
						out_string = out_string + ", "
			else:
				out_string = out_string + "<none>"

			await self.bot.say(out_string)
		else:
			await self.bot.say("Command {0} does not exist.".format(command))

	@commands.command()
	async def get_json(self, *string : str):
		url = urlparse(string[0])
		if url.scheme == None or url.scheme == '':
			await self.bot.say("No scheme specified: {0}".format(url.geturl()))
		elif not url.scheme == 'http' and not url.scheme == 'https':
			await self.bot.say("Invalid URL: {0}".format(url.geturl()))
		else:
			r = requests.get(url.geturl())
			try:
				r = r.json()
			except Exception as e:
				await self.bot.say("Request produced invalid JSON: {0}".format(url.geturl()))
				return
			await self.bot.say("{0}".format(str(r)))

def setup(bot):
	bot.add_cog(Misc(bot))
	'''
