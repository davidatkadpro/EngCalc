"""
MicroPython BTree database manager.

Goal
-----
Provide a light, reusable wrapper over `btree` with:
- CRUD operations
- Automatic serialization for dict/list/tuple/str/float/int
- Type-safe getters
- Bulk import helpers (mapping and list-of-dicts with key field)
- Minimal overhead suitable for ESP32/ESP8266/RP2040

Usage
-----
from lib.sys.db import BTreeDB

with BTreeDB('data.db') as db:
    db.create('version', 1)
    db.set('settings', {'units': 'SI'})
    v = db.get_int('version')
    s = db.get_dict('settings')
    db.import_mapping({'a': 1, 'b': 2}, prefix='nums')
    db.ingest_list([
        {'id': 'S235', 'fy': 235.0},
        {'id': 'S355', 'fy': 355.0},
    ], key_field='id', prefix='steel')

Notes
-----
- Keys are stored as bytes; strings are UTF‑8 encoded internally.
- Values are stored as bytes with a 2‑byte type tag (e.g., b"i:") followed by data.
- Call `flush()` to persist; context manager auto‑flushes and closes.
"""

try:
    import ujson as json
except Exception:  # pragma: no cover (desktop fallback)
    import json  # type: ignore


class BTreeDB:
    """Thin wrapper around MicroPython `btree` with typed values.

    Parameters
    ----------
    path: str
        File path for the database (e.g., 'data.db').
    pagesize, cache_size, minkeypage: int
        Passed to `btree.open` when available (kept default for minimal RAM use).
    autosync: bool
        If True, flush after each write. Defaults to False for speed.
    key_prefix: str | None
        Optional global prefix applied to all keys for namespacing.
    """

    # Type tags (1 char + ':') kept short to reduce storage overhead
    _T_INT = b"i:"
    _T_FLOAT = b"f:"
    _T_STR = b"s:"
    _T_DICT = b"d:"
    _T_LIST = b"l:"
    _T_TUPLE = b"t:"

    def __init__(self, path='data.db', *, pagesize=0, cache_size=0, minkeypage=0,
                 autosync=False, key_prefix=None):
        self.path = path
        self.pagesize = pagesize
        self.cache_size = cache_size
        self.minkeypage = minkeypage
        self.autosync = autosync
        self.key_prefix = key_prefix

        self._f = None
        self._db = None

    # ---- lifecycle ----
    def open(self):
        if self._db is not None:
            return self
        # Import here to keep module import cheap on CPython.
        import btree  # type: ignore
        try:
            f = open(self.path, 'r+b')
        except OSError:
            f = open(self.path, 'w+b')
        self._f = f
        self._db = btree.open(f, pagesize=self.pagesize, cache_size=self.cache_size, minkeypage=self.minkeypage)
        return self

    def close(self):
        if self._db is not None:
            try:
                self._db.flush()
            except Exception:
                pass
            try:
                self._db.close()
            except Exception:
                pass
            self._db = None
        if self._f is not None:
            try:
                self._f.close()
            except Exception:
                pass
            self._f = None

    def flush(self):
        if self._db is not None:
            self._db.flush()

    # Context manager
    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc, tb):
        self.close()

    # ---- key/value helpers ----
    def _k(self, key, prefix=None):
        if isinstance(key, bytes):
            kb = key
        else:
            # accept int/str
            kb = str(key).encode('utf-8')
        p = prefix if prefix is not None else self.key_prefix
        if p:
            if not isinstance(p, bytes):
                p = str(p).encode('utf-8')
            return p + b":" + kb
        return kb

    @classmethod
    def _enc(cls, value):
        # Encode supported types into tagged bytes
        if isinstance(value, bool):
            # Store bool as int to avoid ambiguity
            return cls._T_INT + (b"1" if value else b"0")
        if isinstance(value, int):
            return cls._T_INT + str(value).encode('utf-8')
        if isinstance(value, float):
            # Use repr for consistent round-trip
            return cls._T_FLOAT + repr(value).encode('utf-8')
        if isinstance(value, str):
            return cls._T_STR + value.encode('utf-8')
        if isinstance(value, dict):
            return cls._T_DICT + json.dumps(value).encode('utf-8')
        if isinstance(value, list):
            return cls._T_LIST + json.dumps(value).encode('utf-8')
        if isinstance(value, tuple):
            # Serialize tuple as JSON array but keep tag to restore tuple
            return cls._T_TUPLE + json.dumps(list(value)).encode('utf-8')
        raise TypeError("Unsupported value type: {}".format(type(value)))

    @classmethod
    def _dec(cls, raw):
        if not raw or len(raw) < 2 or raw[1:2] != b":":
            raise ValueError("Invalid encoded value")
        tag = raw[:2]
        body = raw[2:]
        if tag == cls._T_INT:
            return int(body)
        if tag == cls._T_FLOAT:
            # body is ASCII repr of float
            return float(body)
        if tag == cls._T_STR:
            return body.decode('utf-8')
        if tag == cls._T_DICT:
            return json.loads(body)
        if tag == cls._T_LIST:
            return json.loads(body)
        if tag == cls._T_TUPLE:
            return tuple(json.loads(body))
        raise ValueError("Unknown type tag: {}".format(tag))

    def _assert_open(self):
        if self._db is None:
            raise RuntimeError("Database not open. Use 'with BTreeDB(...) as db:' or call open().")

    # ---- CRUD ----
    def exists(self, key, *, prefix=None):
        self._assert_open()
        k = self._k(key, prefix)
        try:
            _ = self._db[k]  # type: ignore[index]
            return True
        except KeyError:
            return False

    def create(self, key, value, *, prefix=None):
        """Insert only; raises if key exists."""
        self._assert_open()
        k = self._k(key, prefix)
        try:
            _ = self._db[k]  # type: ignore[index]
            raise KeyError("Key already exists: {}".format(key))
        except KeyError:
            # not present; good to insert
            pass
        self._db[k] = self._enc(value)  # type: ignore[index]
        if self.autosync:
            self.flush()

    def set(self, key, value, *, prefix=None):
        """Upsert value for key."""
        self._assert_open()
        k = self._k(key, prefix)
        self._db[k] = self._enc(value)  # type: ignore[index]
        if self.autosync:
            self.flush()

    def get(self, key, *, prefix=None, default=None, expected_type=None):
        """Get value; optionally enforce expected_type.

        expected_type can be one of: dict, list, tuple, str, int, float
        """
        self._assert_open()
        k = self._k(key, prefix)
        try:
            raw = self._db[k]  # type: ignore[index]
        except KeyError:
            if default is not None:
                return default
            raise
        val = self._dec(raw)
        if expected_type is not None and not isinstance(val, expected_type):
            raise TypeError("Value for key '{}' is not {}".format(key, expected_type))
        return val

    def update(self, key, value, *, prefix=None):
        """Update existing key; raises if missing."""
        self._assert_open()
        k = self._k(key, prefix)
        # Ensure exists to keep semantics consistent
        try:
            _ = self._db[k]  # type: ignore[index]
        except KeyError:
            raise KeyError("Key does not exist: {}".format(key))
        self._db[k] = self._enc(value)  # type: ignore[index]
        if self.autosync:
            self.flush()

    def delete(self, key, *, prefix=None, missing_ok=True):
        self._assert_open()
        k = self._k(key, prefix)
        try:
            del self._db[k]  # type: ignore[index]
            if self.autosync:
                self.flush()
            return True
        except KeyError:
            if missing_ok:
                return False
            raise

    # ---- Type-safe getters ----
    def get_int(self, key, *, prefix=None, default=None):
        return self.get(key, prefix=prefix, default=default, expected_type=int)

    def get_float(self, key, *, prefix=None, default=None):
        return self.get(key, prefix=prefix, default=default, expected_type=float)

    def get_str(self, key, *, prefix=None, default=None):
        return self.get(key, prefix=prefix, default=default, expected_type=str)

    def get_dict(self, key, *, prefix=None, default=None):
        return self.get(key, prefix=prefix, default=default, expected_type=dict)

    def get_list(self, key, *, prefix=None, default=None):
        return self.get(key, prefix=prefix, default=default, expected_type=list)

    def get_tuple(self, key, *, prefix=None, default=None):
        return self.get(key, prefix=prefix, default=default, expected_type=tuple)

    # ---- Iteration utilities ----
    def keys(self, *, prefix=None):
        """Iterate UTF‑8 decoded keys (optionally under a prefix)."""
        self._assert_open()
        p = prefix if prefix is not None else self.key_prefix
        if p is not None:
            if not isinstance(p, bytes):
                p = str(p).encode('utf-8')
            p = p + b":"
            it = self._db  # type: ignore[attr-defined]
            for k in it:
                if k.startswith(p):
                    yield k[len(p):].decode('utf-8')
        else:
            for k in self._db:  # type: ignore[attr-defined]
                yield k.decode('utf-8')

    # ---- Bulk helpers ----
    def import_mapping(self, mapping, *, prefix=None, overwrite=True):
        """Bulk import a JSON‑compatible dict of key->value.

        Returns a stats dict: {'inserted': x, 'updated': y, 'skipped': z}
        """
        self._assert_open()
        inserted = updated = skipped = 0
        for k, v in mapping.items():
            kb = self._k(k, prefix)
            exists = False
            try:
                _ = self._db[kb]  # type: ignore[index]
                exists = True
            except KeyError:
                exists = False
            if exists:
                if overwrite:
                    self._db[kb] = self._enc(v)  # type: ignore[index]
                    updated += 1
                else:
                    skipped += 1
            else:
                self._db[kb] = self._enc(v)  # type: ignore[index]
                inserted += 1
        if self.autosync:
            self.flush()
        return {'inserted': inserted, 'updated': updated, 'skipped': skipped}

    def ingest_list(self, items, key_field, *, prefix=None, overwrite=True, require_key=True):
        """Ingest a list of dicts using `key_field` value as the DB key.

        Each item is stored as a dict value under the composed key.
        Returns stats dict including counts for missing-key and existing-key cases.
        """
        self._assert_open()
        inserted = updated = skipped_existing = missing_key = 0
        for item in items:
            if not isinstance(item, dict):
                # Skip non-dicts to keep function robust.
                continue
            if key_field not in item:
                missing_key += 1
                if require_key:
                    # Strict mode: skip but count
                    continue
                # If not required, generate a key from index-like growth (not stored here to keep API simple)
                continue
            key = item[key_field]
            kb = self._k(key, prefix)
            exists = False
            try:
                _ = self._db[kb]  # type: ignore[index]
                exists = True
            except KeyError:
                exists = False
            if exists:
                if overwrite:
                    self._db[kb] = self._enc(item)  # type: ignore[index]
                    updated += 1
                else:
                    skipped_existing += 1
            else:
                self._db[kb] = self._enc(item)  # type: ignore[index]
                inserted += 1
        if self.autosync:
            self.flush()
        return {
            'inserted': inserted,
            'updated': updated,
            'skipped_existing': skipped_existing,
            'missing_key': missing_key,
        }
