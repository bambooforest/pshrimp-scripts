'''Print a list of all segments whose featural decomposiitons aren't unique.'''

import csv
from collections import defaultdict

def features(row):
	'''Extract the featural decomposition of a segment from a row of the CSV dump.'''
	return row[11:]

def segment(row):
	'''Extract the segment from a row of the CSV dump.'''
	return row[6]

# Read all segments into a dict. The key is the featural decomposition; the value is a list of segments.
# Specifically, we're using a `defaultdict` here - this means that if we try to access a key that isn't
# defined, the defaultdict will assign a default value to that key.

segs = defaultdict(set)

with open('phoible.csv', encoding='utf-8') as f:
	reader = csv.reader(f)
	for row in reader:
		segs[';'.join(features(row))].add(segment(row))

# Filter out all key/value pairs in the dictionary `segs` where the value list contains only one item.
# These are the segments with unique featural decompositions; what remains are the segments with nonunique ones.

underspecified_segs = [v for v in segs.values() if len(v) > 1]

# Write the underspecified segments to a file.

with open('underspecified.txt', 'w+', encoding='utf-8') as out:
	for i in underspecified_segs:
		out.write(' '.join(i) + '\n')