import discord
import json
import psycopg2
import random
from discord.ext import commands

class Misc():
	def __init__(self,bot):
		self.bot = bot

	@commands.command(pass_context=True)
	async def hello(self,ctx, name: str = None, *args):
		"""[name] - Says hello to you or another!"""
		if name == None:
			await self.bot.say("Hi {0.message.author.name}!".format(ctx))
		else:
			await self.bot.say("Hi {1}, love {0.message.author.name}!".format(ctx,name))

	@commands.command(aliases=["echo"])
	async def say(self,*string : str):
		''' <sentence> - Repeats back! '''
		await self.bot.say(" ".join(string))

	@commands.command(aliases=["choice"])
	async def flip(self,*choices : str):
		"""<choice1> <choice2> [choice 3] - Chooses for you!"""
		await self.bot.say(random.choice(choices))

	@commands.command()
	async def listaliases(self,command : str):
		''' Lists aliases for other commands. '''
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

def setup(bot):
	bot.add_cog(Misc(bot))
