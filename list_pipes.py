# List all segments that contain a pipe.
# These are probably all UPSID dental-alveolars, but I want to be sure.

import csv

with open('phoible.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    printed = set()
    for row in reader:
    	phoneme = row['Phoneme']
    	if '|' in phoneme and phoneme not in printed:
    		printed.add(phoneme)
    		print(phoneme)