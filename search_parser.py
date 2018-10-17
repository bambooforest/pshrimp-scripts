from search import Query, QueryTree
import re

class Stream: # Python iterators don't let you peek; could use more-itertools but don't need to
	def __init__(self, arr):
		self.arr = arr
	def next(self):
		return self.arr.pop(0)
	def peek(self):
		return self.arr[0]
	def eof(self):
		return len(self.arr) == 0

class ParserError(Exception):
	pass

def is_qualifier(s):
	return re.match('^[<>]?[0-9]+$', s) or s == 'no'
def is_qualificand(s):
	return re.match('[+-]+[a-z_]+', s.replace(',',''))
def is_phoneme(s):
	return re.match('\/[^\/]+\/', s)
def is_conjunction(s):
	return s in ['and', 'or', '&', '|']

def parse_qualifier(s):
	if s == 'no':
		return (None, 0)
	gtlt = None
	if s[0] in ['<','>']:
		gtlt = s[0]
		s = s[1:]
	num = int(s)
	return (gtlt, num)
def parse_phoneme(s):
	return s.replace('/','')
def parse_qualificand(s):
	s = s.replace(',','')
	term = {}
	for section in s.split(';'):
		feature_vals = re.match('[+-]+', section)
		feature_vals = ','.join(feature_vals.group().split(' '))
		feature = re.search('[a-z_]+', section).group()
		term[feature] = feature_vals
	return term

def parse(s):
	'''Parse a search string. 

	What is a search string, you ask? A search string consists of terms. Here are some terms:
		>30 +round
		0 +round
		<4 +syllabic
		/m/
		no +round
		no /m/
		3 +,-sonorant

	A *term* consists of a *qualifier* and a *qualificand*.

	A *qualifier* consists of a non-negative integer, optionally preceded by a < or >.
	The word 'no' is treated as a synonym for '0'. If the qualificand is a phoneme, no qualifier
	is necessary.

	A *qualificand* consists of a phoneme or a feature. Phonemes are wrapped in /slashes/.
	Features are preceded by values, which consist of the characters + and -, optionally 
	joined by commas. (For example, +,-sonorant is treated identically to +-sonorant.) 
	To search for multiple features in the same qualificand, separate them with a semicolon.

	There are two *conjunctions*, 'and' and 'or'. These use postfix notation!
	'''

	tokens = Stream(list(filter(None, s.split(' '))))
	query_stack = []

	while not tokens.eof():
		curr = tokens.peek()
		if is_qualifier(curr):
			gtlt, num = parse_qualifier(tokens.next())
			if is_qualificand(tokens.peek()):
				term = parse_qualificand(tokens.next())
				query_stack.append(Query(contains=num>0, term=term, num=num, gtlt=gtlt or '='))
			elif is_phoneme(tokens.peek()):
				phoneme = parse_phoneme(tokens.next())
				query_stack.append(Query(contains=num>0, term=phoneme))
			else:
				raise ParserError(f'Qualifier ({curr}) followed by non-qualificand/phoneme ({tokens.peek()}))')
		elif is_phoneme(curr):
			query_stack.append(Query(contains=True, term=parse_phoneme(curr)))
			tokens.next()
		elif is_conjunction(curr):
			r = query_stack.pop()
			l = query_stack.pop()
			relation = {'AND': 'AND', '&': 'AND', 'OR': 'OR', '|': 'OR'}[curr.upper()]
			query_stack.append(QueryTree(l, relation, r))
			tokens.next()
		else:
			raise ParserError(f'Invalid token {curr}')
	return query_stack[0]