import sqlite3

# Changes for PHOIBLE 2.0:
# - doculects: Renamed from languages.
#              Added glottocode; renamed language_code to iso6393, which now can be null.
#              Added specific_dialect.
#              Removed trump.
#              Moved everything that's not provided by PHOIBLE to a new table. Not sure where these come from yet. Glottolog?
#              inventory_id *should* always be the same as id, but store it just in case. Can't hurt.
# - languages: Added. This is for data on the language itself (location, population, etc.), which is no longer provided by PHOIBLE.
#              No doculects-languages join table yet because I'm not sure how that'd work.
# - language_segments: Renamed from language_phonemes.
#                      Added marginal, which should be a nullable bool, but SQLite stores these as integers.
# - segments: Added glyph_id (Unicode hex values for the characters of the segment, joined with +).
#             Added segment_class.
#             Renamed segment to phoneme.
# - phonemes: Now redundant; removed.
# - allophones: Added.
#               Doesn't FK to segments because there are a lot of allophones listed that don't exist as segments.
#               It might be nice to get featural decompositions for these later?

schema = '''\
doculects (                                 \
    id INTEGER PRIMARY KEY,                 \
    inventory_id VARCHAR(255) NOT NULL,     \
    source VARCHAR(255) NOT NULL,           \
    glottocode VARCHAR(255) NOT NULL,       \
    iso6393 VARCHAR(255),                   \
    language_name VARCHAR(255) NOT NULL,    \
    specific_dialect VARCHAR(255)           \
)
languages (                                 \
    id INTEGER PRIMARY KEY,                 \
    glottocode VARCHAR(255) NOT NULL,       \
    iso6393 VARCHAR(255),                   \
    family VARCHAR(255),                    \
    genus VARCHAR(255),                     \
    country VARCHAR(255),                   \
    area VARCHAR(255),                      \
    population INTEGER,                     \
    latitude FLOAT,                         \
    longitude FLOAT                         \
)
doculect_segments (                                      \
    id INTEGER PRIMARY KEY,                              \
    doculect_id INTEGER NOT NULL,                        \
    segment_id INTEGER NOT NULL,                         \
    marginal INTEGER,                                    \
    FOREIGN KEY(doculect_id) REFERENCES doculects(id),   \
    FOREIGN KEY(segment_id) REFERENCES segments(id),     \
    UNIQUE (doculect_id, segment_id) ON CONFLICT REPLACE \
)
allophones (                                                           \
    doculect_segment_id INTEGER NOT NULL,                              \
    allophone VARCHAR(255) NOT NULL,                                   \
    FOREIGN KEY(doculect_segment_id) REFERENCES doculect_segments(id), \
    UNIQUE (doculect_segment_id, allophone) ON CONFLICT REPLACE        \
)
segments (                                \
    id INTEGER PRIMARY KEY,               \
    phoneme VARCHAR(255),                 \
    glyph_id VARCHAR(255),                \
    segment_class VARCHAR(255),           \
    tone VARCHAR(255),                    \
    stress VARCHAR(255),                  \
    syllabic VARCHAR(255),                \
    short VARCHAR(255),                   \
    long VARCHAR(255),                    \
    consonantal VARCHAR(255),             \
    sonorant VARCHAR(255),                \
    continuant VARCHAR(255),              \
    delayed_release VARCHAR(255),         \
    approximant VARCHAR(255),             \
    tap VARCHAR(255),                     \
    trill VARCHAR(255),                   \
    nasal VARCHAR(255),                   \
    lateral VARCHAR(255),                 \
    labial VARCHAR(255),                  \
    round VARCHAR(255),                   \
    labiodental VARCHAR(255),             \
    coronal VARCHAR(255),                 \
    anterior VARCHAR(255),                \
    distributed VARCHAR(255),             \
    strident VARCHAR(255),                \
    dorsal VARCHAR(255),                  \
    high VARCHAR(255),                    \
    low VARCHAR(255),                     \
    front VARCHAR(255),                   \
    back VARCHAR(255),                    \
    tense VARCHAR(255),                   \
    retracted_tongue_root VARCHAR(255),   \
    advanced_tongue_root VARCHAR(255),    \
    periodic_glottal_source VARCHAR(255), \
    epilaryngeal_source VARCHAR(255),     \
    spread_glottis VARCHAR(255),          \
    constricted_glottis VARCHAR(255),     \
    fortis VARCHAR(255),                  \
    ejective VARCHAR(255),                \
    implosive VARCHAR(255),               \
    click VARCHAR(255)                    \
)'''

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