def build(term):
	if isinstance(term, dict):
		arr = []
		for k in term:
			arr.append(f'segments.{k} = \'{term[k]}\'')
			return ' AND '.join(arr)
	elif isinstance(term, str):
		return f'phonemes.phoneme = {term}'
	else:
		raise 

def contains_query(term, num=None, gtlt='='):
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
	term_cond = build(term)

	if num is None:
		num_cond = ''
	else:
		num_cond = f'HAVING count(*) {gtlt} {num}'

	search = f'''\
	    SELECT languages.id, languages.language_name
		FROM languages
		    JOIN language_phonemes ON languages.id = language_phonemes.language_id
		    JOIN phonemes ON language_phonemes.phoneme_id = phonemes.id
		    JOIN segments ON phonemes.phoneme = segments.segment
		    WHERE {term_cond}
		    GROUP BY languages.id
	        {num_cond}
		;'''

	return search

def does_not_contain_query(term):
	'''Generate a query for languages having no segments matching `term`.'''

	term_cond = build(term)

	search = f'''\
	SELECT languages.id, languages.language_name
	FROM languages
	WHERE languages.id NOT IN
		(SELECT languages.id
		FROM languages
			JOIN language_phonemes ON languages.id = language_phonemes.language_id
			JOIN phonemes ON language_phonemes.phoneme_id = phonemes.id
			JOIN segments ON phonemes.phoneme = segments.segment
		WHERE {term_cond}
		GROUP BY languages.id)
	;'''

	return search


def p(a):
	for line in a:
		print(line[1])
if __name__ == '__main__':
	from db import init_db
	conn, sql = init_db()
	
	print("More than 30 +round")
	res = sql.execute(contains_query({'round': '+'}, 30, '>')).fetchall()
	p(res)

	print("No +round")
	res = sql.execute(does_not_contain_query({'round': '+'}))
	p(res)

	print("Two vowels")
	res = sql.execute(contains_query({'syllabic': '+'}, 3, '<'))
	p(res)