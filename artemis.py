import discord
from discord.ext import commands
import json
import random
import psycopg2
import re
import datetime
from karma import process_karma

startup_extensions = ["karmacommands","misccommands"]
bot = commands.Bot(command_prefix=commands.when_mentioned_or('?'), description="Artemis: Rhiba's life organiser.")
with open('creds.json') as data:
	creds = json.load(data)
with open('artemis_config.json') as data:
	config = json.load(data)
token = creds["token"]
dbinfo = creds["dbinfo"]
users = []
# Connect to db and get superusers
try:
	connect_str = "dbname='{0}' user='{1}' host='{2}' password='{3}'".format(dbinfo["dbname"],dbinfo["user"],dbinfo["host"],dbinfo["password"])
	conn = psycopg2.connect(connect_str)
	cursor = conn.cursor()
	cursor.execute("""SELECT name FROM users WHERE is_superuser = True;""")
	rows = cursor.fetchall()
	superusers = [i[0] for i in rows]
	cursor.execute("""SELECT name FROM users WHERE is_superuser = False;""")
	rows = cursor.fetchall()
	users = [i[0] for i in rows]
	print("Loaded users and superusers.")

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
	print('Superusers:')
	for i in superusers:
		print(i)
	print('------')

@bot.event
async def on_message(message):
	if message.author.bot:
		return

	#add user to db if not exist
	if not str(message.author) in users and not str(message.author) in superusers:
		insert_statement = 'INSERT INTO users (name, is_superuser, can_alias) values (%s,%s,%s);'
		cursor.execute(insert_statement,(str(message.author),False,False))
		conn.commit()
		users.append(str(message.author))

	if message.content.startswith('<@'+bot.user.id+'>'):
		await bot.process_commands(message)
	elif message.content.startswith('?'):
		await bot.process_commands(message)
	else:
		reply = process_karma(message,conn,cursor,config["karma_timeout"])
		if not reply == "":
			await bot.send_message(message.channel,reply)

	bot.process_commands(message)


if __name__ == "__main__":
	for extension in startup_extensions:
		try:
			bot.load_extension(extension)
		except Exception as e:
			exc = '{}: {}'.format(type(e).__name__, e)
			print('Failed to load extension {}\n{}'.format(extension,exc))
	bot.run(token)
