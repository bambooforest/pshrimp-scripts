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
FOREIGN KEY(language_id) REFERENCES languages(id), FOREIGN KEY(phoneme_id) REFERENCES phonemes(id),  \
UNIQUE (language_id, phoneme_id) ON CONFLICT REPLACE)
segments (id INTEGER PRIMARY KEY, \
segment VARCHAR(255), \
tone VARCHAR(255), \
stress VARCHAR(255), \
syllabic VARCHAR(255), \
short VARCHAR(255), \
long VARCHAR(255), \
consonantal VARCHAR(255), \
sonorant VARCHAR(255), \
continuant VARCHAR(255), \
delayed_release VARCHAR(255), \
approximant VARCHAR(255), \
tap VARCHAR(255), \
trill VARCHAR(255), \
nasal VARCHAR(255), \
lateral VARCHAR(255), \
labial VARCHAR(255), \
round VARCHAR(255), \
labiodental VARCHAR(255), \
coronal VARCHAR(255), \
anterior VARCHAR(255), \
distributed VARCHAR(255), \
strident VARCHAR(255), \
dorsal VARCHAR(255), \
high VARCHAR(255), \
low VARCHAR(255), \
front VARCHAR(255), \
back VARCHAR(255), \
tense VARCHAR(255), \
retracted_tongue_root VARCHAR(255), \
advanced_tongue_root VARCHAR(255), \
periodic_glottal_source VARCHAR(255), \
epilaryngeal_source VARCHAR(255), \
spread_glottis VARCHAR(255), \
constricted_glottis VARCHAR(255), \
fortis VARCHAR(255), \
ejective VARCHAR(255), \
implosive VARCHAR(255), \
click VARCHAR(255) '''

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