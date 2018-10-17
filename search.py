def phoneme_condition(term):
	if isinstance(term, dict):
		arr = []
		for k in term:
			arr.append(f'segments.{k} = \'{term[k]}\'')
			return ' AND '.join(arr)
	elif isinstance(term, str):
		return f'phonemes.phoneme LIKE \'{term}\''
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
	term_cond = phoneme_condition(term)

	if num is None:
		num_cond = ''
	else:
		num_cond = f'HAVING count(*) {gtlt} {num}'

	return f'''\
	    languages.id IN (
	    SELECT languages.id
		FROM languages
		    JOIN language_phonemes ON languages.id = language_phonemes.language_id
		    JOIN phonemes ON language_phonemes.phoneme_id = phonemes.id
		    JOIN segments ON phonemes.phoneme = segments.segment
		    WHERE {term_cond}
		    GROUP BY languages.id
	        {num_cond}
		)'''

def does_not_contain_query(term):
	'''Generate a query for languages having no segments matching `term`.'''

	term_cond = phoneme_condition(term)

	return f'''\
	languages.id NOT IN
		(SELECT languages.id
		FROM languages
			JOIN language_phonemes ON languages.id = language_phonemes.language_id
			JOIN phonemes ON language_phonemes.phoneme_id = phonemes.id
			JOIN segments ON phonemes.phoneme = segments.segment
		WHERE {term_cond}
		GROUP BY languages.id)
	'''

class Query:
	def __init__(self, contains=True, term='', num=None, gtlt='='):
		self.term = term # either a dict of {feature: value} or a string representing a phoneme
		self.contains = contains
		if contains:
			self.num = num
			self.gtlt = gtlt

class QueryTree:
	def __init__(self, left, relation, right):
		self.l = left # left side of the query tree - a QueryTree or a Query
		self.r = right # right side of the query tree
		self.rel = relation # 'AND' or 'OR'

def get_sql(q):
	if hasattr(q, 'l'):
		return f'({get_sql(q.l)} {q.rel} {get_sql(q.r)})'
	if q.contains:
		return contains_query(q.term, q.num, q.gtlt)
	else:
		return does_not_contain_query(q.term)

def search(qtree):
	return f'''\
		SELECT languages.id, languages.language_name
		FROM languages
		WHERE {get_sql(qtree)}
		;'''

if __name__ == '__main__':
	from db import init_db
	from search_parser import parse
	import sys
	conn, sql = init_db()
	s = search(parse(sys.argv[1]))
	res = sql.execute(s)
	for line in res:
		print(line[1])