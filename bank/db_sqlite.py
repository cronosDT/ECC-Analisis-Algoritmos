import sqlite3
from datetime import datetime, timedelta

DB_PATH = "signatures.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS signatures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            signature BLOB NOT NULL,
            timestamp DATETIME NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def save_signature_to_db(nombre: str, signature: bytes):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO signatures (nombre, signature, timestamp) VALUES (?, ?, ?)',
        (nombre, signature, datetime.utcnow()))
    conn.commit()
    conn.close()

def get_latest_signature_by_name(nombre: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT signature, timestamp FROM signatures WHERE nombre = ? ORDER BY timestamp DESC LIMIT 1',
        (nombre,))
    row = cursor.fetchone()
    conn.close()
    if row:
        signature, timestamp_str = row
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")
        return {
            "signature": signature,
            "timestamp": timestamp
        }
    return None

def is_signature_expired(signature_time, expiration_seconds=30):
    return datetime.utcnow() > signature_time + timedelta(seconds=expiration_seconds)
