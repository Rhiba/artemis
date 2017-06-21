import discord
from discord.ext import commands
import json
import random
import psycopg2
import re

bot = commands.Bot(command_prefix=commands.when_mentioned_or('?'), description="Artemis: Rhiba's life organiser.")
with open('creds.json') as data:
	creds = json.load(data)
token = creds["token"]
dbinfo = creds["dbinfo"]

# Connect to db and get superusers
try:
	connect_str = "dbname='{0}' user='{1}' host='{2}' password='{3}'".format(dbinfo["dbname"],dbinfo["user"],dbinfo["host"],dbinfo["password"])
	conn = psycopg2.connect(connect_str)
	cursor = conn.cursor()
	cursor.execute("""SELECT name FROM users WHERE is_superuser = True;""")
	rows = cursor.fetchall()
	superusers = [i[0] for i in rows]

except Exception as e:
	print("Could not connect to db.")
	print(e)


def check_auth(user):
	for i in superusers:
		if i == user:
			return True
	return False

@bot.event
async def on_ready():
	print('Logged in as:')
	print(bot.user.name)
	print('------')
	print('Authorised users:')
	for i in superusers:
		print(i)
	print('------')

@bot.event
async def on_message(message):
	if message.author.bot:
		return
	
	if message.content.startswith('@artemis'):
		await bot.process_commands(message)
	elif message.content.startswith('?'):
		await bot.process_commands(message)
	else:
		regex_no_quote = r"([^\+\"\s]+)\+\+(\s|$)"
		regex_quote = r"\"([^\"]+)\"\+\+(\s|$)"
		matches_no_quote = [i[0] for i in re.findall(regex_no_quote,message.content)]
		matches_quote = [i[0] for i in re.findall(regex_quote,message.content)]

		items = matches_no_quote + list(set(matches_quote) - set(matches_no_quote))
		print(items)

	bot.process_commands(message)

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
async def listaliases(command : str):
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

@bot.command()
async def karma(name : str, *args):
	prep_statement = "SELECT score FROM karma WHERE name = (%s);"
	cursor.execute(prep_statement, [name.lower()])
	rows = cursor.fetchall()
	if rows == []:
		await bot.say("Sorry, there is no entry for {0} in my database! :confused:".format(name))
	else:
		await bot.say("{0} has a score of {1}!".format(name,rows[0][0]))

bot.run(token)
