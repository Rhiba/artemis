import discord
import json
import psycopg2
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

def setup(bot):
	bot.add_cog(Karma(bot))
