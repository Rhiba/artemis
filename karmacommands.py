import discord
import json
import psycopg2
import random
from discord.ext import commands

class Karma():
	def __init__(self,bot):
		self.bot = bot
		with open('creds.json') as data:
			creds = json.load(data)

		token = creds["token"]
		dbinfo = creds["dbinfo"]
		connect_str = "dbname='{0}' user='{1}' host='{2}' password='{3}'".format(dbinfo["dbname"],dbinfo["user"],dbinfo["host"],dbinfo["password"])
		self.conn = psycopg2.connect(connect_str)
		self.cursor = self.conn.cursor()

	@commands.command()
	async def karma(self, name : str, *args):
		""" <item> - Returns the amount of karma for the item. """
		prep_statement = "SELECT score FROM karma WHERE name = (%s);"
		self.cursor.execute(prep_statement, [name.lower()])
		rows = self.cursor.fetchall()
		if rows == []:
			await self.bot.say("Sorry, there is no entry for {0} in my database! :confused:".format(name))
		else:
			await self.bot.say("{0} has a score of {1}!".format(name,rows[0][0]))

	@commands.command()
	async def reason(self, name : str, *args):
		""" <item> - Returns, if possible, a random reason for changing the karma of the item. """
		prep_statement = "SELECT karma_reasons.reason, karma_reasons.change FROM karma, karma_reasons WHERE karma.name = (%s) AND karma.id = karma_reasons.kid;"
		self.cursor.execute(prep_statement, [name.lower()])
		rows = self.cursor.fetchall()
		if rows == []:
			await self.bot.say("Sorry, there is no entry for {0} in my database! :confused:".format(name))

		rows = [i for i in rows if not i[0] == ""]
		if rows == []:
			await self.bot.say("Sorry, there are no reasons for {0} in my database! :confused:".format(name))

		row = random.choice(rows)
		if row[1] == -1:
			await self.bot.say("{} has lost karma {}".format(name,row[0]))
		elif row[1] == 1:
			await self.bot.say("{} has gained karma {}".format(name,row[0]))
		else:
			await self.bot.say("{} has retained karma {}".format(name,row[0]))

def setup(bot):
	bot.add_cog(Karma(bot))
