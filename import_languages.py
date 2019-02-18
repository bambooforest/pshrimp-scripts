from db import init_db
import csv
from collections import OrderedDict
from import_inventories import get_id, dfilter

# This assumes you've already run import_inventories.

def fix_population(i):
    if i == 'No_known_speakers' or i == 'Extinct' or i == 'Ancient' or i == 'No_estimate_available' \
    or i == 'Missing E16 page':
        return None
    return i.replace(',','')

def fix_lfooitude(f):
    if f == 'NULL':
        return None
    # going to special-case this because afaict it only appears once
    f = f.replace('`N','0')
    # and this
    f = f.replace('-00','')
    return f.replace(':','.')

if __name__ == '__main__':
    conn, sql = init_db()

    with open('phoible-aggregated.tsv', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # Get the language from the database by the inventory ID just in case
            # Inventory ID (PHOIBLE's ID) *should* be equal to ours, but let's be paranoid...
            lang_id = get_id('languages', 'inventory_id', row['InventoryID'], sql)

            # language_family_root
            sql.execute('UPDATE languages SET language_family_root = ? WHERE inventory_id = ?', (row['LanguageFamilyRoot'], lang_id))
            # language_family_genus
            sql.execute('UPDATE languages SET language_family_genus = ? WHERE inventory_id = ?', (row['LanguageFamilyGenus'], lang_id))
            # country
            sql.execute('UPDATE languages SET country = ? WHERE inventory_id = ?', (row['Country'], lang_id))
            # area
            sql.execute('UPDATE languages SET area = ? WHERE inventory_id = ?', (row['Area'], lang_id))
            # population
            sql.execute('UPDATE languages SET population = ? WHERE inventory_id = ?', (fix_population(row['Population']), lang_id))
            # latitude
            sql.execute('UPDATE languages SET latitude = ? WHERE inventory_id = ?', (fix_lfooitude(row['Latitude']), lang_id))
            # longitude
            sql.execute('UPDATE languages SET longitude = ? WHERE inventory_id = ?', (fix_lfooitude(row['Longitude']), lang_id))

    conn.commit()