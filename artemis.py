import discord
from discord.ext import commands
import json

bot = commands.Bot(command_prefix='?', description="Artemis: Rhiba's life organiser.")
with open('creds.json') as data:
	creds = json.load(data)

token = creds["token"]

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.event
async def on_message(message):
	if message.author.bot:
		return
	await bot.process_commands(message)

@bot.command()
async def hello(user: discord.User):
    await bot.say("Hi!")

bot.run(token)
