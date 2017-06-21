import re
import datetime
import psycopg2

def process_karma(message,conn,cursor):
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
	
	update_from_list(pos_items,1,conn,cursor)
	update_from_list(neg_items,-1,conn,cursor)
	update_from_list(neut_items,0,conn,cursor)

def update_from_list(items, k_score, conn, cursor):
	plus, minus, neutral = 0, 0, 0
	if k_score == 1:
		plus = 1
	elif k_score == -1:
		minus = 1
	else:
		neutral = 1

	for item in items:
		prep_statement = "SELECT * FROM karma WHERE name = (%s);"
		cursor.execute(prep_statement, [item.lower()])
		rows = cursor.fetchall()
		if rows == []:
			insert_statement = "INSERT INTO karma(name,added,altered,score,pluses,minuses,neutrals) VALUES (%s,%s,%s,%s,%s,%s,%s);"
			ts = str(datetime.datetime.now(datetime.timezone.utc))
			cursor.execute(insert_statement, (item.lower(),ts,ts,k_score,plus,minus,neutral))
			conn.commit()
		else:
			iden, score, pluses, minuses, neutrals = rows[0][0], rows[0][4] + k_score, rows[0][5] + plus, rows[0][6] + minus, rows[0][7] + neutral
			altered = str(datetime.datetime.now(datetime.timezone.utc))
			update_statement = "UPDATE karma SET (altered,score,pluses,minuses,neutrals) = (%s,%s,%s,%s,%s) WHERE id = (%s);"
			cursor.execute(update_statement,(altered,score,pluses,minuses,neutrals,iden))
			conn.commit()
