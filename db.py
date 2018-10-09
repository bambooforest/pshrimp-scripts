import sqlite3

schema = '''\
languages (id INTEGER PRIMARY KEY, inventory_id VARCHAR(255) NOT NULL,                               \
source VARCHAR(255) NOT NULL, language_code STRING NOT NULL, language_name VARCHAR(255) NOT NULL,    \
trump INTEGER NOT NULL, canonical_name VARCHAR(255), language_family_root VARCHAR(255),              \
language_family_genus VARCHAR(255), country VARCHAR(255), area VARCHAR(255), population INTEGER,     \
latitude FLOAT, longitude FLOAT)
phonemes (id INTEGER PRIMARY KEY, phoneme VARCHAR(255) NOT NULL,                                     \
klass VARCHAR(255) NOT NULL, combined_klass VARCHAR(255) NOT NULL,                                   \
num_of_combined_glyphs VARCHAR(255) NOT NULL)
language_phonemes (language_id INTEGER NOT NULL, phoneme_id INTEGER NOT NULL,                        \
FOREIGN KEY(language_id) REFERENCES languages(id), FOREIGN KEY(phoneme_id) REFERENCES phonemes(id))
segments (id INTEGER PRIMARY KEY, \
segment VARCHAR(255) NOT NULL, \
tone VARCHAR(255) NOT NULL, \
stress VARCHAR(255) NOT NULL, \
syllabic VARCHAR(255) NOT NULL, \
short VARCHAR(255) NOT NULL, \
long VARCHAR(255) NOT NULL, \
consonantal VARCHAR(255) NOT NULL, \
sonorant VARCHAR(255) NOT NULL, \
continuant VARCHAR(255) NOT NULL, \
delayed_release VARCHAR(255) NOT NULL, \
approximant VARCHAR(255) NOT NULL, \
tap VARCHAR(255) NOT NULL, \
trill VARCHAR(255) NOT NULL, \
nasal VARCHAR(255) NOT NULL, \
lateral VARCHAR(255) NOT NULL, \
labial VARCHAR(255) NOT NULL, \
round VARCHAR(255) NOT NULL, \
labiodental VARCHAR(255) NOT NULL, \
coronal VARCHAR(255) NOT NULL, \
anterior VARCHAR(255) NOT NULL, \
distributed VARCHAR(255) NOT NULL, \
strident VARCHAR(255) NOT NULL, \
dorsal VARCHAR(255) NOT NULL, \
high VARCHAR(255) NOT NULL, \
low VARCHAR(255) NOT NULL, \
front VARCHAR(255) NOT NULL, \
back VARCHAR(255) NOT NULL, \
tense VARCHAR(255) NOT NULL, \
retracted_tongue_root VARCHAR(255) NOT NULL, \
advanced_tongue_root VARCHAR(255) NOT NULL, \
periodic_glottal_source VARCHAR(255) NOT NULL, \
epilaryngeal_source VARCHAR(255) NOT NULL, \
spread_glottis VARCHAR(255) NOT NULL, \
constricted_glottis VARCHAR(255) NOT NULL, \
fortis VARCHAR(255) NOT NULL, \
ejective VARCHAR(255) NOT NULL, \
implosive VARCHAR(255) NOT NULL, \
click VARCHAR(255) NOT NULL)'''

def init_db():
	sqlite_db_path = './phoible.sqlite'
	conn = sqlite3.connect(sqlite_db_path)
	sql = conn.cursor()
	build_schema = [f'CREATE TABLE IF NOT EXISTS {table}' for table in schema.split('\n')]
	for t in build_schema:
		sql.execute(t)
	return (conn, sql)

if __name__ == '__main__':
	conn, sql = init_db()
	conn.commit()
	conn.close()