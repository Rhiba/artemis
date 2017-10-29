import discord
import json
import psycopg2
import random
from command import Command
from discord.ext import commands

class karma(Command):
	def call(ctx,args):
		if len(args) < 1:
			return ["Please enter a karma item to search for! :face_palm:"]
		with open('creds.json') as data:
			creds = json.load(data)
		token = creds["token"]
		dbinfo = creds["dbinfo"]
		connect_str = "dbname='{0}' user='{1}' host='{2}' password='{3}'".format(dbinfo["dbname"],dbinfo["user"],dbinfo["host"],dbinfo["password"])
		conn = psycopg2.connect(connect_str)
		cursor = conn.cursor()
		prep_statement = "SELECT score FROM karma WHERE name = (%s);"
		name = args[0].lower()
		cursor.execute(prep_statement, [args[0].lower()])
		rows = cursor.fetchall()
		if rows == []:
			return ["Sorry, there is no entry for {0} in my database! :confused:".format(name)]
		else:
			return ["{0} has a score of {1}!".format(name,rows[0][0])]
	def desc():
		return "<item> - Returns the amount of karma for the item."


class reason(Command):
	def call(ctx,args):
		if len(args) < 1:
			return ["Please enter a karma item to search for! :face_palm:"]
		with open('creds.json') as data:
			creds = json.load(data)
		token = creds["token"]
		dbinfo = creds["dbinfo"]
		connect_str = "dbname='{0}' user='{1}' host='{2}' password='{3}'".format(dbinfo["dbname"],dbinfo["user"],dbinfo["host"],dbinfo["password"])
		conn = psycopg2.connect(connect_str)
		cursor = conn.cursor()
		prep_statement = "SELECT karma_reasons.reason, karma_reasons.change FROM karma, karma_reasons WHERE karma.name = (%s) AND karma.id = karma_reasons.kid;"
		name = args[0].lower()
		cursor.execute(prep_statement, [args[0].lower()])
		rows = cursor.fetchall()
		if rows == []:
			return ["Sorry, there is no entry for {0} in my database! :confused:".format(name)]

		rows = [i for i in rows if not i[0] == ""]
		if rows == []:
			return ["Sorry, there are no reasons for {0} in my database! :confused:".format(name)]

		row = random.choice(rows)
		if row[1] == -1:
			return ["{} has lost karma {}".format(name,row[0])]
		elif row[1] == 1:
			return ["{} has gained karma {}".format(name,row[0])]
		else:
			return ["{} has retained karma {}".format(name,row[0])]
	
	def desc():
		return "<item> - Returns a random reason for this items karma."
