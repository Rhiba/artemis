import discord
from discord.ext import commands
import json
import random
import psycopg2
import re
import datetime

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
	print('Superusers:')
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
		pos_regex_no_quote = r"([^\+\"\s]+)\+\+(\s|$)"
		pos_regex_quote = r"\"([^\"]+)\"\+\+(\s|$)"
		pos_matches_no_quote = [i[0] for i in re.findall(pos_regex_no_quote,message.content)]
		pos_matches_quote = [i[0] for i in re.findall(pos_regex_quote,message.content)]
		pos_items = list(set(pos_matches_no_quote)) + list(set(pos_matches_quote) - set(pos_matches_no_quote))
		print(pos_items)

		neg_regex_no_quote = r"([^\+\"\s]+)\-\-(\s|$)"
		neg_regex_quote = r"\"([^\"]+)\"\-\-(\s|$)"
		neg_matches_no_quote = [i[0] for i in re.findall(neg_regex_no_quote,message.content)]
		neg_matches_quote = [i[0] for i in re.findall(neg_regex_quote,message.content)]
		neg_items = list(set(neg_matches_no_quote)) + list(set(neg_matches_quote) - set(neg_matches_no_quote))
		print(neg_items)

		neut_regex_no_quote = r"([^\+\"\s]+)(\-\+|\+\-)(\s|$)"
		neut_regex_quote = r"\"([^\"]+)\"(\-\+|\+\-)(\s|$)"
		neut_matches_no_quote = [i[0] for i in re.findall(neut_regex_no_quote,message.content)]
		neut_matches_quote = [i[0] for i in re.findall(neut_regex_quote,message.content)]
		neut_items = list(set(neut_matches_no_quote)) + list(set(neut_matches_quote) - set(neut_matches_no_quote))
		print(neut_items)
		
		# For each of 3 lists, check if item exists, if so karma it, if not, add it and then print out line of scores
		for item in pos_items:
			prep_statement = "SELECT * FROM karma WHERE name = (%s);"
			cursor.execute(prep_statement, [item.lower()])
			rows = cursor.fetchall()
			if rows == []:
				insert_statement = "INSERT INTO karma(name,added,altered,score,pluses,minuses,neutrals) VALUES (%s,%s,%s,1,1,0,0);"
				ts = datetime.datetime.now(datetime.timezone.utc)
				print(str(ts))
				cursor.execute(insert_statement, (item.lower(),str(ts),str(ts)))
				conn.commit()
			else:
				iden, score, pluses, minuses, neutrals = rows[0][0], rows[0][4] + 1, rows[0][5] + 1, rows[0][6], rows[0][7]
				altered = str(datetime.datetime.now(datetime.timezone.utc))
				update_statement = "UPDATE karma SET (altered,score,pluses,minuses,neutrals) = (%s,%s,%s,%s,%s) WHERE id = (%s);"
				cursor.execute(update_statement,(altered,score,pluses,minuses,neutrals,iden))
				conn.commit()

		for item in neg_items:
			prep_statement = "SELECT * FROM karma WHERE name = (%s);"
			cursor.execute(prep_statement, [item.lower()])
			rows = cursor.fetchall()
			if rows == []:
				insert_statement = "INSERT INTO karma(name,added,altered,score,pluses,minuses,neutrals) VALUES (%s,%s,%s,-1,0,1,0);"
				ts = datetime.datetime.now(datetime.timezone.utc)
				print(str(ts))
				cursor.execute(insert_statement, (item.lower(),str(ts),str(ts)))
				conn.commit()
			else:
				iden, score, pluses, minuses, neutrals = rows[0][0], rows[0][4] - 1, rows[0][5], rows[0][6] + 1, rows[0][7]
				altered = str(datetime.datetime.now(datetime.timezone.utc))
				update_statement = "UPDATE karma SET (altered,score,pluses,minuses,neutrals) = (%s,%s,%s,%s,%s) WHERE id = (%s);"
				cursor.execute(update_statement,(altered,score,pluses,minuses,neutrals,iden))
				conn.commit()

		for item in neut_items:
			prep_statement = "SELECT * FROM karma WHERE name = (%s);"
			cursor.execute(prep_statement, [item.lower()])
			rows = cursor.fetchall()
			if rows == []:
				insert_statement = "INSERT INTO karma(name,added,altered,score,pluses,minuses,neutrals) VALUES (%s,%s,%s,0,0,0,1);"
				ts = datetime.datetime.now(datetime.timezone.utc)
				print(str(ts))
				cursor.execute(insert_statement, (item.lower(),str(ts),str(ts)))
				conn.commit()
			else:
				iden, score, pluses, minuses, neutrals = rows[0][0], rows[0][4], rows[0][5], rows[0][6], rows[0][7] + 1
				altered = str(datetime.datetime.now(datetime.timezone.utc))
				update_statement = "UPDATE karma SET (altered,score,pluses,minuses,neutrals) = (%s,%s,%s,%s,%s) WHERE id = (%s);"
				cursor.execute(update_statement,(altered,score,pluses,minuses,neutrals,iden))
				conn.commit()


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
