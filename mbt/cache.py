import pickle
import datetime as dt
import sqlite3
from mbt.config import Config


config = Config()


class Cache():
    """
    Simple SQLite cache
    """

    setup_stmts = """
    create table if not exists cache (
        updated_at timestamp not null,
        key int not null,
        data blob not null
    );

    create index if not exists cache_key on cache (key);
    """

    def __init__(self, path=None):
        self.path = path or config.cache_path
        self.conn = sqlite3.Connection(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(self.setup_stmts)

    def set(self, *keys, data):
        key = hash(''.join(str(s) for s in keys))
        updated_at = str(dt.datetime.now())
        data = pickle.dumps(data)
        self.conn.execute("""
        insert into cache (updated_at, key, data) 
        values (?,?,?)
        """, (updated_at, key, data))

    # TODO: add expiration
    def get(self, *keys):
        key = hash(''.join(str(s) for s in keys))
        resp = self.conn.execute('select data from cache where key={key}'.format(key=key)).fetchone()
        if len(resp) > 0:
            return pickle.loads(resp['data'])
