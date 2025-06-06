import sqlite3  # For SQLite database operations
import uuid     # For generating unique user IDs

DATABASE_PATH = 'data/users.db'  # Path to the users database

def connect_db():
    # Connect to the users database
    conn = sqlite3.connect(DATABASE_PATH)
    return conn

def create_user_table():
    # Create the users table if it doesn't exist
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
    # Add a new user to the database
    user_id = str(uuid.uuid4())
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (id, username, password_hash) VALUES (?, ?, ?)
    ''', (user_id, username, password_hash))
    conn.commit()
    conn.close()

def get_user(username):
    # Retrieve a user record by username
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def initialize_db():
    # Initialize the database by creating the users table
    create_user_table()

def is_admin_user(username, password):
    # Check if the user is an admin and verify the password
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT password_hash, is_admin FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    db.close()
    if row and row[1] == 1:
        return verify_password(row[0], password)  # verify_password should be defined elsewhere
    return False