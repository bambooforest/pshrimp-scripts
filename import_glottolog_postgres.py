'''Imports Glottolog data needed for Pshrimp to a Postgres database.'''

from db_postgres import init_db
from pyglottolog.api import Glottolog
from import_postgres import insert, get_id
from collections import OrderedDict
import csv

from os.path import expanduser
GLOTTOLOG_LOCATION = expanduser('~/Documents/glottolog-3.4')

api = Glottolog(GLOTTOLOG_LOCATION)

def language(glottocode):
	'''Dialects don't have most information defined, so go upstairs to a language.'''

	# Ideally there would be error handling here in case there's a family.
	# In practice, it just crashed and I edited the csv file.
	languoid = api.languoid(glottocode)

	if languoid.level.name == 'dialect':
		while languoid.level.name == 'dialect':
			languoid = languoid.parent

	return languoid

def data(glottocode):
	languoid = language(glottocode)
	print(languoid)

	latitude = languoid.latitude or None
	longitude = languoid.longitude or None

	iso6393 = languoid.iso_code # api provides iso and iso_code - what's the difference?

	family = None
	genus = None
	if not languoid.isolate:
		family = languoid.lineage[0][0]
		if len(languoid.lineage) > 1:
			genus = languoid.lineage[1][0] # not sure what to do with this
		else:
			genus = family

	area = languoid.macroareas[0]

	return OrderedDict({
		'glottocode': glottocode, # use the glottocode we passed in, even if it's of a dialect and we had to go upstairs to get other info
		'latitude': latitude, 
		'longitude': longitude, 
		'iso6393': iso6393, 
		'family': family, 
		'genus': genus, 
		'macroarea': area.name
	})


conn, sql = init_db()

# Figure out what's done already and skip it
sql.execute('SELECT glottocode FROM languages GROUP BY glottocode')
done = set([i[0] for i in sql.fetchall()])

print('{} languages already done.'.format(len(done)))

with open('phoible.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
    	if row['Glottocode'] not in done:
    		props = data(row['Glottocode'])

    		# Add language
	    	insert('languages', props, return_id=True, sql=sql)
	    	language_id = sql.fetchone()[0]
	    	print(language_id)
	    	conn.commit()
	    	done.add(row['Glottocode'])

# Now do the countries
# There's no good reason for doing this down here; it's just that I imported all the other language data first.
sql.execute('SELECT id FROM countries')
done_countries = set([i[0] for i in sql.fetchall()])
sql.execute('SELECT languages.glottocode FROM languages JOIN languages_countries ON languages.id = languages_countries.language_id')
done_glottocodes = set([i[0] for i in sql.fetchall()])

with open('phoible.csv', encoding='utf-8') as f:
	reader = csv.DictReader(f)
	for row in reader:
		glottocode = row['Glottocode']
		if glottocode not in done_glottocodes:
			countries = language(glottocode).countries
			language_id = get_id('languages', 'glottocode', glottocode, sql)
			if language_id is None:
				raise Exception('Missing language for glottocode {}'.format(glottocode))
			for country in countries:
				if country.id not in done_countries:
					insert('countries', OrderedDict({'id': country.id, 'name': country.name}), sql=sql)
					done_countries.add(country.id)
				insert('languages_countries', OrderedDict({'language_id': language_id, 'country_id': country.id}), return_id=False, sql=sql)
				print('{}: {}'.format(language_id, country.name))
			done_glottocodes.add(glottocode)

conn.commit()
conn.close()