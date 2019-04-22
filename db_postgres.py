import psycopg2

schema = '''\
doculects (                                 \
    id SERIAL PRIMARY KEY,                  \
    inventory_id VARCHAR(255) NOT NULL,     \
    source VARCHAR(255) NOT NULL,           \
    glottocode VARCHAR(255) NOT NULL,       \
    iso6393 VARCHAR(255),                   \
    language_name VARCHAR(255) NOT NULL,    \
    specific_dialect VARCHAR(255)           \
)
languages (                                 \
    id SERIAL PRIMARY KEY,                  \
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
segments (                                \
    id SERIAL PRIMARY KEY,                \
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
    lateralis VARCHAR(255),               \
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
)
doculect_segments (                                      \
    id SERIAL PRIMARY KEY,                               \
    doculect_id INTEGER NOT NULL,                        \
    segment_id INTEGER NOT NULL,                         \
    marginal BOOLEAN,                                    \
    FOREIGN KEY(doculect_id) REFERENCES doculects(id),   \
    FOREIGN KEY(segment_id) REFERENCES segments(id),     \
    UNIQUE (doculect_id, segment_id)                     \
)
allophones (                                                           \
    doculect_segment_id INTEGER NOT NULL,                              \
    allophone VARCHAR(255) NOT NULL,                                   \
    FOREIGN KEY(doculect_segment_id) REFERENCES doculect_segments(id), \
    UNIQUE (doculect_segment_id, allophone)                            \
)'''

def init_db():
    conn_string = "dbname=pshrimp user=postgres password=postgres"
    conn = psycopg2.connect(conn_string)
    sql = conn.cursor()
    build_schema = [f'CREATE TABLE IF NOT EXISTS {table}' for table in schema.split('\n')]
    for t in build_schema:
        sql.execute(t)
    return (conn, sql)

if __name__ == '__main__':
    conn, sql = init_db()
    conn.commit()
    conn.close()