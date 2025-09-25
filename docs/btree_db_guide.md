# BTree Database Manager Guide

This guide explains how to use the lightweight BTree-backed database manager in `lib/sys/db.py` on MicroPython devices (ESP32/ESP8266/RP2040).

## Overview
- Wrapper: `BTreeDB` over MicroPython `btree` file store.
- Features: CRUD, automatic serialization (dict/list/tuple/str/int/float), type-safe getters, key prefixing, bulk import helpers.
- Resource-friendly: lazy imports, compact tags, optional autosync.

## Quick Start
```python
from lib.sys.db import BTreeDB

with BTreeDB('data.db', autosync=True) as db:
    db.create('version', 1)
    db.set('settings', {'units': 'SI', 'theme': 'dark'})

    print(db.get_int('version'))            # 1
    print(db.get_dict('settings')['units']) # 'SI'
```

## CRUD Basics
```python
with BTreeDB('data.db') as db:
    db.set('k1', 123)               # upsert
    print(db.get('k1'))             # 123

    db.create('k2', [1, 2, 3])      # insert only
    db.update('k2', [1, 2, 3, 4])   # must exist
    db.delete('k2')                 # remove (True if deleted)

    print(db.exists('k1'))          # True
    db.flush()                      # persist if not using autosync
```

## Type-Safe Access
```python
with BTreeDB('data.db') as db:
    db.set('pi', 3.14159)
    db.set('title', 'EngCalc')
    db.set('cfg', {'mode': 'prod'})

    x = db.get_float('pi')          # float
    s = db.get_str('title')         # str
    c = db.get_dict('cfg')          # dict

    # Generic with expected type check (raises TypeError on mismatch)
    cfg = db.get('cfg', expected_type=dict)
```

## Namespacing (prefix)
Apply a namespace to keep keys organized.
```python
with BTreeDB('data.db', key_prefix='app1') as db:
    db.set('user:1', {'name': 'Ada'}) # stored under b'app1:user:1'

with BTreeDB('data.db') as db:
    db.set('user:2', {'name': 'Grace'}, prefix='app2')
```
Iterate keys under a prefix:
```python
with BTreeDB('data.db') as db:
    for k in db.keys(prefix='app2'):
        print(k)
```

## Bulk Import Helpers
- Mapping import:
```python
with BTreeDB('data.db') as db:
    stats = db.import_mapping({'A': 1, 'B': 2}, prefix='nums', overwrite=False)
    # {'inserted': 2, 'updated': 0, 'skipped': 0}
```
- List ingestion (use a field as the key; stores the whole dict as value):
```python
rows = [
    {'id': 'S235', 'fy': 235.0},
    {'id': 'S355', 'fy': 355.0},
]
with BTreeDB('data.db') as db:
    stats = db.ingest_list(rows, key_field='id', prefix='steel')
    # {'inserted': 2, 'updated': 0, 'skipped_existing': 0, 'missing_key': 0}
```

## Persistence & Performance Tips
- Autosync vs manual: `autosync=True` flushes after each write; otherwise call `flush()` strategically.
- Keep keys short (e.g., `s:S235` instead of long JSON paths).
- Booleans are stored as ints internally; prefer `get_int` when reading flags if applicable.
- Avoid frequent reopen/close in tight loops; reuse a single context.

## Error Handling
- `RuntimeError` if the DB is not open.
- `KeyError` for missing keys on `create`, `update`, or `get` without a default.
- `TypeError` when a value’s type doesn’t match the expected type.
- `ValueError` on low-level decode issues (corrupt data).

## MicroPython Notes
- `btree` is included in many ESP32/ESP8266 builds; verify your firmware supports it.
- The file is created if missing (`'w+b'`); ensure the filesystem has free space.
- Typical deployment with `mpremote`:
```bash
mpremote connect auto fs cp -r lib :/lib
mpremote connect auto fs cp main.py :/main.py
```

## Minimal API Reference
- Construction: `BTreeDB(path='data.db', autosync=False, key_prefix=None)`
- CRUD: `create`, `set`, `get`, `update`, `delete`, `exists`, `flush`, `keys`
- Typed getters: `get_int`, `get_float`, `get_str`, `get_dict`, `get_list`, `get_tuple`
- Bulk: `import_mapping(mapping, prefix=None, overwrite=True)`, `ingest_list(items, key_field, prefix=None, overwrite=True)`
