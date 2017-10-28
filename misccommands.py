import discord
import json
import psycopg2
import random
from discord.ext import commands
from urllib.parse import urlparse
import requests
from command import Command

class hello(Command):
	def call(ctx,args):
		"""[name] - Says hello to you or another!"""
		if len(args) < 1:
			return "Hi {0.author.name}!".format(ctx)
		else:
			return "Hi {1}, love {0.author.name}!".format(ctx,args[0])
	def desc():
		return "[person] - Says hello to you or someone you specify."

class say(Command):
	def call(ctx,args):
		return " ".join(args)
	def desc():
		return "<words> - Echos what you tell it to."

class help(Command):
	def call(ctx,args):
		output = ''
		descs = args[0]
		comms = args[1]
		if len(comms) < 1:
			# List all commands
			for k,v in descs.items():
				output = output + k + ": " + v + "\n"
		else:
			no_comms = []
			for comm in comms:
				if comm.lower() in descs.keys():
					output = output + comm.lower() + ": " + descs[comm.lower()] + "\n"
				else:
					no_comms.append(comm)

			if len(no_comms) > 0:
				for c in no_comms:
					output = output + "No such command: {0}.".format(c) + "\n"
		return "```\n" + output + "```"

	def desc():
		return "[commands] - List all commands, or search specific commands."

class flip(Command):
	def call(ctx,args):
		return random.choice(args)
	
	def desc():
		return "<choice1> <choice2> [choices] - Chooses for you!"

class get_json(Command):
	def call(ctx,args):
		url = urlparse(args[0])
		if url.scheme == None or url.scheme == '':
			return "No scheme specified: {0}".format(url.geturl())
		elif not url.scheme == 'http' and not url.scheme == 'https':
			return "Invalid URL: {0}".format(url.geturl())
		else:
			r = requests.get(url.geturl())
			try:
				r = r.json()
			except Exception as e:
				return "Request produced invalid JSON: {0}".format(url.geturl())

			return "{0}".format(str(r))
	def desc():
		return "<url> - GETs JSON from URL."

class read_json(Command):
	# This needs completely redoing
	def call(ctx,args):
		attr = args[0]
		try:
			jn = json.loads(' '.join(args[1:]).replace("'",'"'))
		except Exception as e:
			return "Invalid JSON: {0}".format(e)
		out = ''
		try:
			out = str(jn[attr])
		except Exception as e:
			return "No such attribute: {0}.".format(attr)

		return out

	def desc():
		return "<attr> <json> - Return the value of a specific attribute from some JSON."
