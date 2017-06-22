import discord
from discord.ext import commands
import re
import datetime
import psycopg2

def process_karma(message,conn,cursor):
	reply = ""

	filtered_content = message.content
	re.sub(u'```.*```','',filtered_content)

	#TODO: Match fullstops lmaooo
	pos_regex_no_quote = u"([^\+\"\s]+[^\+\"\s]+)\+\+(\s(for|because)\s+.+?(?=\s([^\+\"\s]+[^\+\"\s]+|\"[^\"]+\")(\+\+|\+\-|\-\+|\-\-))|\s(for|because)\s+.+$|\s\(.+\)|\s|$)"
	pos_regex_quote = u"\"([^\"]+)\"\+\+(\s(for|because)\s+.+?(?=\s([^\+\"\s]+[^\+\"\s]+|\"[^\"]+\")(\+\+|\+\-|\-\+|\-\-))|\s(for|because)\s+.+$|\s\(.+\)|\s|$)"
	# Reason here is index 1	
	pos_matches_no_quote = [(i[0],i[1].strip()) for i in re.findall(pos_regex_no_quote,filtered_content)]
	pos_matches_quote = [(i[0],i[1].strip()) for i in re.findall(pos_regex_quote,filtered_content)]
	pos_items_with_reasons = list(dict(pos_matches_no_quote+pos_matches_quote).items())
	pos_items = [i[0] for i in pos_items_with_reasons]

	neg_regex_no_quote = u"([^\+\"\s]+[^\+\"\s]+)\-\-(\s(for|because)\s+.+?(?=\s([^\+\"\s]+[^\+\"\s]+|\"[^\"]+\")(\+\+|\+\-|\-\+|\-\-))|\s(for|because)\s+.+$|\s\(.+\)|\s|$)"
	neg_regex_quote = u"\"([^\"]+)\"\-\-(\s(for|because)\s+.+?(?=\s([^\+\"\s]+[^\+\"\s]+|\"[^\"]+\")(\+\+|\+\-|\-\+|\-\-))|\s(for|because)\s+.+$|\s\(.+\)|\s|$)"
	# Reason here is index 1
	neg_matches_no_quote = [(i[0],i[1].strip()) for i in re.findall(neg_regex_no_quote,filtered_content)]
	neg_matches_quote = [(i[0],i[1].strip()) for i in re.findall(neg_regex_quote,filtered_content)]
	neg_items_with_reasons = list(dict(neg_matches_no_quote+neg_matches_quote).items())
	neg_items = [i[0] for i in neg_items_with_reasons]

	neut_regex_no_quote = u"([^\+\"\s]+[^\+\"\s]+)(\-\+|\+\-)(\s(for|because)\s+.+?(?=\s([^\+\"\s]+[^\+\"\s]+|\"[^\"]+\")(\+\+|\+\-|\-\+|\-\-))|\s(for|because)\s+.+$|\s\(.+\)|\s|$)"
	neut_regex_quote = u"\"([^\"]+)\"(\-\+|\+\-)(\s(for|because)\s+.+?(?=\s([^\+\"\s]+[^\+\"\s]+|\"[^\"]+\")(\+\+|\+\-|\-\+|\-\-))|\s(for|because)\s+.+$|\s\(.+\)|\s|$)"
	# Reason here is index 2
	neut_matches_no_quote = [(i[0],i[2].strip()) for i in re.findall(neut_regex_no_quote,filtered_content)]
	neut_matches_quote = [(i[0],i[2].strip()) for i in re.findall(neut_regex_quote,filtered_content)]
	neut_items_with_reasons = list(dict(neut_matches_no_quote+neut_matches_quote).items())
	neut_items = [i[0] for i in neut_items_with_reasons]

	if len(pos_items) + len(neut_items) + len(neg_items) == 0:
		return reply
	
	uid_statement = "SELECT * FROM users WHERE name = (%s);"
	cursor.execute(uid_statement,[str(message.author)])
	rows = cursor.fetchall()
	uid = rows[0][0]
	new_scores_pos = update_from_list(pos_items_with_reasons,1,conn,cursor,uid)
	new_scores_neg = update_from_list(neg_items_with_reasons,-1,conn,cursor,uid)
	new_scores_neut = update_from_list(neut_items_with_reasons,0,conn,cursor,uid)

	if len(pos_items) + len(neg_items) + len(neut_items) == 1:
		if not pos_items == []:
			reply = "I have given karma to {0}, the new score is {1}!".format(pos_items[0],new_scores_pos[0])
		elif not neg_items == []:
			reply = "I have removed karma from {0}, the new score is {1}.".format(neg_items[0],new_scores_neg[0])
		else:
			reply = "I have left the karma of {0} unchanged, the score remains as {1}.".format(neut_items[0],new_scores_neut[0])
	elif len(pos_items) + len(neg_items) + len(neut_items) > 1:
		reply = "I have changed the karma scores as requested, the scores are now: "

		# Need to filter out repeated ++ then -- in same line
		if not list(set(pos_items)&set(neg_items)&set(neut_items)) == []:
			#Karma does not change
			intersecting = list(set(pos_items)&set(neg_items)&set(neut_items))
			remove_from_items_and_scores(intersecting,pos_items,new_scores_pos)
			remove_from_items_and_scores(intersecting,neg_items,new_scores_neg)
			if len(neut_items) == 1 and len(pos_items) + len(neg_items) == 0:
				reply = "I have left the karma of {0} unchanged, the score remains as {1}.".format(neut_items[0],new_scores_neut[0])
				return reply
		elif not list(set(pos_items)&set(neg_items)) == []:
			intersecting = list(set(pos_items)&set(neg_items))
			remove_from_items_and_scores(intersecting,pos_items,new_scores_pos)
			if len(neg_items) == 1 and len(neut_items) + len(pos_items) == 0:
				reply = "I have left the karma of {0} unchanged, the score remains as {1}.".format(neg_items[0],new_scores_neg[0])
				return reply
		elif not list(set(pos_items)&set(neut_items)) == []:
			intersecting = list(set(pos_items)&set(neut_items))
			remove_from_items_and_scores(intersecting,pos_items,new_scores_pos)
			if len(neut_items) == 1 and len(neg_items) + len(pos_items) == 0:
				reply = "I have given karma to {0}, the new score is {1}!".format(neut_items[0],new_scores_neut[0])
				return reply
		elif not list(set(neg_items)&set(neut_items)) == []:
			intersecting = list(set(neg_items)&set(neut_items))
			remove_from_items_and_scores(intersecting,neg_items,new_scores_neg)
			if len(neut_items) == 1 and len(neg_items) + len(pos_items) == 0:
				reply = "I have removed karma from {0}, the new score is {1}.".format(neut_items[0],new_scores_neut[0])
				return reply


		all_items = pos_items + neg_items + neut_items
		all_scores = new_scores_pos + new_scores_neg + new_scores_neut
		reply = multi_karma_reply_format(reply,all_items,all_scores)

	return reply

def multi_karma_reply_format(reply, items, scores):
	for idx, i in enumerate(items):
		reply = reply + "{0} ({1})".format(i,scores[idx])
		if not i == items[-1]:
			reply = reply + ", "

	return reply

def remove_from_items_and_scores(intersecting, items, scores):
			to_remove = []
			for i in intersecting:
				to_remove.append(items.index(i))
				items.remove(i)
			to_remove.sort()
			to_remove.reverse()
			for j in to_remove:
				del scores[j]


def update_from_list(items, k_score, conn, cursor,uid):
	plus, minus, neutral = 0, 0, 0
	if k_score == 1:
		plus = 1
	elif k_score == -1:
		minus = 1
	else:
		neutral = 1

	scores = []
	for item in items:
		prep_statement = "SELECT * FROM karma WHERE name = (%s);"
		cursor.execute(prep_statement, [item[0].lower()])
		rows = cursor.fetchall()
		if rows == []:
			scores.append(k_score)
			insert_statement = "INSERT INTO karma(name,added,altered,score,pluses,minuses,neutrals) VALUES (%s,%s,%s,%s,%s,%s,%s);"
			ts = str(datetime.datetime.now(datetime.timezone.utc))
			cursor.execute(insert_statement, (item[0].lower(),ts,ts,k_score,plus,minus,neutral))
			conn.commit()
		else:
			scores.append(rows[0][4] + k_score)
			iden, score, pluses, minuses, neutrals = rows[0][0], rows[0][4] + k_score, rows[0][5] + plus, rows[0][6] + minus, rows[0][7] + neutral
			altered = str(datetime.datetime.now(datetime.timezone.utc))
			update_statement = "UPDATE karma SET (altered,score,pluses,minuses,neutrals) = (%s,%s,%s,%s,%s) WHERE id = (%s);"
			cursor.execute(update_statement,(altered,score,pluses,minuses,neutrals,iden))
			conn.commit()
		# Now get id then update reason
		prep_statement = "SELECT * FROM karma WHERE name = (%s);"
		cursor.execute(prep_statement, [item[0].lower()])
		rows = cursor.fetchall()
		kid = rows[0][0]
		added = str(datetime.datetime.now(datetime.timezone.utc))
		insert_reason_statement = "INSERT INTO karma_reasons (kid,uid,added,change,score,reason) VALUES (%s,%s,%s,%s,%s,%s);"
		cursor.execute(insert_reason_statement,(kid,uid,added,k_score,rows[0][4],item[1]))
		conn.commit()

	return scores
