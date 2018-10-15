def contains_query(term, num=None, gt=False):
	'''Generate a query for languages having `gt?` `num` phonemes meeting the condition `term`.
	Parameters:
	- `term`: A search term. Either a `str` (search for languages that have a specific phoneme)
	  or a `dict` (search for phonemes having certain features).
	  For example:
	    `contains_query('q')` finds every language that has a /q/.
	    `contains_query({'epilaryngeal_source': '+'})` finds every language with a phoneme that 
	      has a '+' for the 'epilaryngeal_source' feature.
	- `num`: The number condition. If `None`, find all languages with any phonemes that match `term`.
	  For example:
	    `contains_query({'round': '+'}, 5)` finds every language with five +round phonemes.
	- `gt`: Either `True` or `False`. If `True`, find languages with greater than `num` things;
	    if false, find languages with exactly `num` things.
	    '''
	if isinstance(term, dict):
		term_cond = []
		for k in term:
			term_cond.append(f'segments.{k} = \'{term[k]}\'')
			term_cond = ' AND '.join(term_cond)
	elif isinstance(term, str):
		term_cond = f'phonemes.phoneme = {term}'
	else:
		raise 

	if num is None:
		num_cond = ''
	else:
		num_cond = f'HAVING count(*) {">" if gt else "="} {num}'

	search = f'''\
	    SELECT languages.id, languages.language_name
	    FROM languages
	        JOIN language_phonemes ON languages.id = language_phonemes.language_id
	        JOIN phonemes ON language_phonemes.phoneme_id = phonemes.id
	        JOIN segments ON phonemes.phoneme = segments.segment,
		    (
		        SELECT languages.id
		        FROM languages
		            JOIN language_phonemes ON languages.id = language_phonemes.language_id
		            JOIN phonemes ON language_phonemes.phoneme_id = phonemes.id
		            JOIN segments ON phonemes.phoneme = segments.segment
		        WHERE {term_cond}
		        GROUP BY languages.id
	            {num_cond}
		    ) a
		WHERE a.id = languages.id AND
		{term_cond}
		GROUP BY languages.id
		;'''

	return search

if __name__ == '__main__':
	from db import init_db
	conn, sql = init_db()
	res = sql.execute(contains_query({'round': '+'}, 30, True)).fetchall()
	for line in res:
		print(line[1])