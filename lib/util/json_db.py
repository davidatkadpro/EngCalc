import json
from lib.sys.db import BTreeDB


def ingest_json_db(json_file, key_field='designation', prefix='steel'):
    with open(json_file, 'r') as f:
        rows = json.load(f)
        
    with BTreeDB('data.db') as db:
        stats = db.ingest_list(rows, key_field, prefix)
        print(stats)

