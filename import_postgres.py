from db_postgres import init_db
from inflection import underscore
from collections import OrderedDict
import csv

conn, sql = init_db()

def get_id(table, field, value):
    '''Get (assumed to be unique) id of the thing in `table` where `field` = `value`. Returns False if it's not there.'''
    # NB: Passing table/column names as parameters doesn't work. This does not appear to be documented.
    sql.execute('SELECT id FROM {} WHERE {} = %s'.format(table, field), (value,))
    res = sql.fetchone()
    return res[0] if res else None

def insert(table, props, return_id = True):
    '''Insert OrderedDict `props` ({col_name: prop}) into `table`.'''
    # ON CONFLICT REPLACE for allophones - looks like there's a lot of dups.
    s = 'INSERT INTO {} ({}) VALUES ({}) ON CONFLICT DO NOTHING'.format(table, ','.join(props.keys()), ','.join([f'%({val})s' for val in props.keys()]))
    if return_id:
        s += ' RETURNING id'
    sql.execute(s, props)

def dfilter(d, keys):
    '''Return a new OrderedDict consisting of only the key/value pairs in dict d with keys listed in the `keys` set.
    Also munge them so they fit nicely in the DB.'''
    return OrderedDict((munge_key(k), munge_value(v)) for k, v in d.items() if munge_key(k) in keys)

def dinsert(table, d, keys):
    '''dfilter, then insert'''
    insert(table, dfilter(d, keys))

def munge_key(k):
    key_replacements = {
        'raisedLarynxEjective': 'ejective',
        'loweredLarynxImplosive': 'implosive',
        'lateral': 'lateralis'
    }
    if k in key_replacements:
        return key_replacements[k]
    return underscore(k)

def munge_value(v):
    value_replacements = {
        '0': None,      # for segment features
        'NA': None,     # for marginal, allophones, etc.
        'FALSE': False, # for marginal
        'TRUE': True    # for marginal
    }
    if v in value_replacements:
        return value_replacements[v]
    # Segments can have two values separated by a |.
    # It looks like this is UPSID's 'dental-alveolar', or whatever it is.
    # There are also a few uses in GM.
    # For now, we'll just store these as whatever's to the right of the first pipe.
    # Which looks like it'll usually be the alveolar.
    if '|' in v:
        return v.split('|')[1]
    return v

LANGUAGE_FILTER = set([
    'inventory_id', 
    'source', 
    'glottocode', 
    'iso6393', 
    'language_name', 
    'specific_dialect'
])

SEGMENT_FILTER = set([
    'phoneme',
    'glyph_id',
    'segment_class',
    'tone',
    'stress',
    'syllabic',
    'short',
    'long',
    'consonantal',
    'sonorant',
    'continuant',
    'delayed_release',
    'approximant',
    'tap',
    'trill',
    'nasal',
    'lateralis',
    'labial',
    'round',
    'labiodental',
    'coronal',
    'anterior',
    'distributed',
    'strident',
    'dorsal',
    'high',
    'low',
    'front',
    'back',
    'tense',
    'retracted_tongue_root',
    'advanced_tongue_root',
    'periodic_glottal_source',
    'epilaryngeal_source',
    'spread_glottis',
    'constricted_glottis',
    'fortis',
    'ejective',
    'implosive',
    'click'
])

# This is going to take two passes.
# In the first pass, we'll add all the segments.
# In the second pass, we'll add everything else.
# This is because segments may appear in an allophone list before their features are given.
# Also, remember to call munge_value on row['Phoneme'].

if __name__ == '__main__':
    # Import segments
    with open('phoible.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        i = 0
        finished_segments = set()
        for row in reader:
            i += 1
            if (i % 100 == 0):
                print('Importing segments\tRead {} lines'.format(i))
            if munge_value(row['Phoneme']) in finished_segments:
                continue
            if get_id('segments', 'phoneme', munge_value(row['Phoneme'])) is None:
                dinsert('segments', row, SEGMENT_FILTER)
                finished_segments.add(munge_value(row['Phoneme']))
    conn.commit()
    # Import everything else
    with open('phoible.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        i = 0
        added_languages = {}
        for row in reader:
            i += 1
            if (i % 100 == 0):
                print('Importing inventories\tRead {} lines'.format(i))
            # Language
            if row['InventoryID'] not in added_languages:
                docul_id = get_id('doculects', 'inventory_id', row['InventoryID'])
                if docul_id is None:
                    dinsert('doculects', row, LANGUAGE_FILTER)
                    docul_id = sql.fetchone()[0] # ID is returned
                added_languages[row['InventoryID']] = docul_id
            # Language segment
            seg_id = get_id('segments', 'phoneme', munge_value(row['Phoneme']))
            if seg_id is None:
                raise ValueError('No segment for {}!'.format(munge_value(row['Phoneme'])))
            insert('doculect_segments', OrderedDict([
                ('doculect_id', docul_id),
                ('segment_id', seg_id),
                ('marginal', munge_value(row['Marginal']))
            ]))
            returning = sql.fetchone()
            if returning is None: # sometimes segments are listed twice; ON CONFLICT DO NOTHING means no id is returned
                sql.execute('SELECT id FROM doculect_segments WHERE doculect_id = %s AND segment_id = %s', (docul_id, seg_id))
                docul_seg_id = sql.fetchone()[0]
            else:
                docul_seg_id = returning[0]
            # Allophones
            if row['Allophones'] != 'NA':
                for allophone in row['Allophones'].split(' '):
                    insert('allophones', OrderedDict([
                        ('doculect_segment_id', docul_seg_id),
                        ('allophone', allophone)
                    ]), False)
    conn.commit()