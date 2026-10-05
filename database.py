import sqlite3
from datetime import datetime
from config import DATABASE_PATH

def connect():
    return sqlite3.connect(DATABASE_PATH)

def init_db():
    conn = connect()
    conn.execute("""CREATE TABLE IF NOT EXISTS opportunities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        url TEXT UNIQUE,
        source TEXT,
        categories TEXT,
        score INTEGER,
        published_date TEXT,
        deadline TEXT,
        status TEXT,
        benefit TEXT,
        requirements TEXT,
        created_at TEXT,
        notified INTEGER DEFAULT 0,
        main_category TEXT DEFAULT "altro"
    )""")
    try:
        conn.execute('ALTER TABLE opportunities ADD COLUMN main_category TEXT DEFAULT "altro"')
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

def add_opportunity(title,url,source,categories,score,published_date="",deadline="",status="DA_VERIFICARE",benefit="",requirements="",main_category="altro"):
    conn=connect()
    try:
        conn.execute("""INSERT INTO opportunities
        (title,url,source,categories,score,published_date,deadline,status,benefit,requirements,created_at,main_category)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        (title,url,source,",".join(categories),score,published_date,deadline,status,benefit,requirements,datetime.utcnow().isoformat(),main_category))
        conn.commit()
        inserted=True
    except sqlite3.IntegrityError:
        inserted=False
    conn.close()
    return inserted

def get_unnotified():
    conn=connect()
    rows=conn.execute("""SELECT id,title,url,source,categories,score,deadline,status,benefit
                         FROM opportunities WHERE notified=0 ORDER BY score DESC""").fetchall()
    conn.close()
    return rows

def mark_notified(ids):
    if not ids: return
    conn=connect()
    conn.executemany("UPDATE opportunities SET notified=1 WHERE id=?", [(i,) for i in ids])
    conn.commit()
    conn.close()

def get_latest(limit=20):
    conn=connect()
    rows=conn.execute("""SELECT title,url,source,categories,score,deadline,status,benefit
                         FROM opportunities ORDER BY id DESC LIMIT ?""",(limit,)).fetchall()
    conn.close()
    return rows

def get_by_category(category, limit=20):
    conn=connect()
    rows=conn.execute("""SELECT title,url,source,categories,score,deadline,status,benefit
                         FROM opportunities WHERE main_category=? ORDER BY id DESC LIMIT ?""",(category,limit)).fetchall()
    conn.close()
    return rows
