import sqlite3
import uuid

DATABASE_PATH = 'data/users.db'

def connect_db():
    conn = sqlite3.connect(DATABASE_PATH)
    return conn

def create_user_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_user(username, password_hash):
    user_id = str(uuid.uuid4())
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (id, username, password_hash) VALUES (?, ?, ?)
    ''', (user_id, username, password_hash))
    conn.commit()
    conn.close()

def get_user(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def initialize_db():
    create_user_table()
