import discord
from discord.ext import commands
import json
import random

bot = commands.Bot(command_prefix=commands.when_mentioned_or('?'), description="Artemis: Rhiba's life organiser.")
with open('creds.json') as data:
	creds = json.load(data)
with open('authed_users.json') as data:
	users = json.load(data)

authed_users = users["authorised_for_all"]
token = creds["token"]

def check_auth(user):
	for i in authed_users:
		if i == user:
			return True

	return False

@bot.event
async def on_ready():
	print('Logged in as:')
	print(bot.user.name)
	print('------')
	print('Authorised users:')
	for i in authed_users:
		print(i)
	print('------')

@bot.event
async def on_message(message):
	if message.author.bot:
		return
	await bot.process_commands(message)

@bot.command(pass_context=True)
async def hello(ctx, name: str = None, *args):
	"""[name] - Says hello to you or another!"""
	if name == None:
		await bot.say("Hi {0.message.author.name}!".format(ctx))
	else:
		await bot.say("Hi {1}, love {0.message.author.name}!".format(ctx,name))

@bot.command(aliases=["echo"])
async def say(*string : str):
	''' <sentence> - Repeats back! '''
	await bot.say(" ".join(string))

@bot.command(aliases=["choice"])
async def flip(*choices : str):
	"""<choice1> <choice2> [choice 3] - Chooses for you!"""
	await bot.say(random.choice(choices))

@bot.command()
async def list_aliases(command : str):
	out_string = "Aliases for {0}: ".format(command)
	if command in bot.commands:
		if bot.commands[command].aliases:
			for alias in bot.commands[command].aliases:
				out_string = out_string + alias
				if not bot.commands[command].aliases[-1] == alias:
					out_string = out_string + ", "
		else:
			out_string = out_string + "<none>"

		await bot.say(out_string)
	else:
		await bot.say("Command {0} does not exist.".format(command))

bot.run(token)
