import discord
from discord.ext import commands
import json

bot = commands.Bot(command_prefix=commands.when_mentioned_or('?'), description="Artemis: Rhiba's life organiser.")
with open('creds.json') as data:
	creds = json.load(data)

token = creds["token"]

@bot.event
async def on_ready():
    print('Logged in as:')
    print(bot.user.name)
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

bot.run(token)
