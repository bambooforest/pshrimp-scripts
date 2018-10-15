from db import init_db
from inflection import underscore
from collections import OrderedDict
import csv

conn, sql = init_db()

def insert(table, props):
	'''Insert OrderedDict `props` into `table`.'''
	s = 'INSERT INTO {} ({}) VALUES ({})'.format(table, ','.join(props.keys()), ','.join([f':{val}' for val in props.keys()]))
	sql.execute(s, tuple(props[k] for k in props))

def munge(d):
	new_d = OrderedDict()
	for k in d.keys():
		if k == 'raisedLarynxEjective':
			new_k = 'ejective' 
		elif k == 'loweredLarynxImplosive':
			new_k = 'implosive'
		else:
			new_k = underscore(k) 
		if d[k] != '0': # null
			new_d[new_k] = d[k]
	return new_d

if __name__ == '__main__':
	with open('phoible-segments-features.tsv', encoding='utf-8') as f:
		reader = csv.DictReader(f, delimiter='\t')
		for row in reader:
			print(row['segment'])
			insert('segments', munge(row))
	conn.commit()