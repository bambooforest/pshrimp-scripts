from db import init_db
import csv
from inflection import underscore
from collections import OrderedDict

def get_id(table, field, value, sql):
	'''Get (assumed to be unique) id of the thing in `table` where `field` = `value`.'''
	# NB: Passing table/column names as parameters doesn't work. This does not appear to be documented.
	res = sql.execute('SELECT id FROM {} WHERE {} = ?'.format(table, field), (value,)).fetchone()
	return res[0] if res else False

def insert(table, props, sql):
	'''Insert OrderedDict `props` into `table`.'''
	s = 'INSERT INTO {} ({}) VALUES ({})'.format(table, ','.join(props.keys()), ','.join([f':{val}' for val in props.keys()]))
	sql.execute(s, tuple(props[k] for k in props))

def dfilter(d, keys):
	'''Return a new OrderedDict consisting of only the key/value pairs with keys listed in the `keys` array.
	Also munge them so they fit nicely in the DB.'''
	return OrderedDict((munge_key(k), v) for k, v in d.items() if k in keys)

def munge_key(k):
	'''Replace CamelCase with snake_case and rename `class` to `klass` (in Class and CombinedClass).'''
	return underscore(k).replace('class', 'klass')

if __name__ == '__main__':
	conn, sql = init_db()
	# LANGUAGE PROPERTIES:
	# InventoryID         - the ID of the source/language pair in PHOIBLE's database
	# Source              - the database PHOIBLE used as a source for the inventory
	# LanguageCode        - the ISO 639-(2? 3?) code for the language
	# LanguageName        - the name of the language
	# Trump               - holds the nth instance of the language in the DB (in case of multiple sources)
	langprops = {'InventoryID', 'Source', 'LanguageCode', 'LanguageName', 'Trump'}
	# PHONEME PROPERTIES:
	# PhonemeID           - the ID of the row (discard - not used anywhere else)
	# GlyphID             - the ID of the phoneme's IPA representation in PHOIBLE's DB (discard)
	# Phoneme             - the IPA representation of the phoneme
	# Class               - consonant, vowel, or tone
	# CombinedClass       - consonant, diacritic, vowel, etc.
	# NumOfCombinedGlyphs - number of codepoints comprising the IPA representation of the character
	phonprops = {'Phoneme', 'Class', 'CombinedClass', 'NumOfCombinedGlyphs'}
	
	with open('phoible-phonemes.tsv', encoding='utf-8') as f:
		reader = csv.DictReader(f, delimiter='\t')
		for row in reader:
			# Add the inventory (language/source pair, mostly - there are a few dups IIRC) if it doesn't exist
			lang_id = get_id('languages', 'inventory_id', row['InventoryID'], sql)
			if not lang_id:
				print(row['LanguageName']) # good enough for a progress marker
				insert('languages', dfilter(row, langprops), sql)
				lang_id = sql.lastrowid
			# Now add the phoneme if it doesn't exist
			phon_id = get_id('phonemes', 'phoneme', row['Phoneme'], sql)
			if not phon_id:
				insert('phonemes', dfilter(row, phonprops), sql)
				phon_id = sql.lastrowid
			# Now add the language/phoneme pair
			insert('language_phonemes', OrderedDict({'language_id': lang_id, 'phoneme_id': phon_id}), sql)
	
	conn.commit()