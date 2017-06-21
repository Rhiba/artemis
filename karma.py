import discord
from discord.ext import commands
import re
import datetime
import psycopg2

def process_karma(message,conn,cursor):
	reply = ""
	
	pos_regex_no_quote = r"([^\+\"\s]+)\+\+(\s|$)"
	pos_regex_quote = r"\"([^\"]+)\"\+\+(\s|$)"
	pos_matches_no_quote = [i[0] for i in re.findall(pos_regex_no_quote,message.content)]
	pos_matches_quote = [i[0] for i in re.findall(pos_regex_quote,message.content)]
	pos_items = list(set(pos_matches_no_quote)) + list(set(pos_matches_quote) - set(pos_matches_no_quote))

	neg_regex_no_quote = r"([^\+\"\s]+)\-\-(\s|$)"
	neg_regex_quote = r"\"([^\"]+)\"\-\-(\s|$)"
	neg_matches_no_quote = [i[0] for i in re.findall(neg_regex_no_quote,message.content)]
	neg_matches_quote = [i[0] for i in re.findall(neg_regex_quote,message.content)]
	neg_items = list(set(neg_matches_no_quote)) + list(set(neg_matches_quote) - set(neg_matches_no_quote))

	neut_regex_no_quote = r"([^\+\"\s]+)(\-\+|\+\-)(\s|$)"
	neut_regex_quote = r"\"([^\"]+)\"(\-\+|\+\-)(\s|$)"
	neut_matches_no_quote = [i[0] for i in re.findall(neut_regex_no_quote,message.content)]
	neut_matches_quote = [i[0] for i in re.findall(neut_regex_quote,message.content)]
	neut_items = list(set(neut_matches_no_quote)) + list(set(neut_matches_quote) - set(neut_matches_no_quote))
	
	new_scores_pos = update_from_list(pos_items,1,conn,cursor)
	new_scores_neg = update_from_list(neg_items,-1,conn,cursor)
	new_scores_neut = update_from_list(neut_items,0,conn,cursor)

	if len(pos_items) + len(neg_items) + len(neut_items) == 1:
		if not pos_items == []:
			reply = "I have given karma to {0}, the new score is {1}!".format(pos_items[0],new_scores_pos[0])
		elif not neg_items == []:
			reply = "I have removed karma from {0}, the new score is {1}.".format(neg_items[0],new_scores_neg[0])
		else:
			reply = "I have left the karma of {0} unchanged, the score remains as {1}.".format(neut_items[0],new_scores_neut[0])

	return reply

def update_from_list(items, k_score, conn, cursor):
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
		cursor.execute(prep_statement, [item.lower()])
		rows = cursor.fetchall()
		if rows == []:
			scores.append(k_score)
			insert_statement = "INSERT INTO karma(name,added,altered,score,pluses,minuses,neutrals) VALUES (%s,%s,%s,%s,%s,%s,%s);"
			ts = str(datetime.datetime.now(datetime.timezone.utc))
			cursor.execute(insert_statement, (item.lower(),ts,ts,k_score,plus,minus,neutral))
			conn.commit()
		else:
			scores.append(rows[0][4] + k_score)
			iden, score, pluses, minuses, neutrals = rows[0][0], rows[0][4] + k_score, rows[0][5] + plus, rows[0][6] + minus, rows[0][7] + neutral
			altered = str(datetime.datetime.now(datetime.timezone.utc))
			update_statement = "UPDATE karma SET (altered,score,pluses,minuses,neutrals) = (%s,%s,%s,%s,%s) WHERE id = (%s);"
			cursor.execute(update_statement,(altered,score,pluses,minuses,neutrals,iden))
			conn.commit()

	return scores
