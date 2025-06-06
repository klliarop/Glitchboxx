import sqlite3  # For SQLite database operations
import uuid     # For generating unique user IDs
import os       # For file path operations
from auth.utils import hash_password, check_password as verify_password  # Import password utilities

ADMIN_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "../data", "admin.db")  # Compute admin DB path

def connect_admin_db():
    # Connect to the admin database
    return sqlite3.connect(ADMIN_DB_PATH)

def create_admin_table():
    # Create the admins table if it doesn't exist
    conn = connect_admin_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_admin(username, password):
    # Add a new admin user with a hashed password
    user_id = str(uuid.uuid4())
    password_hash = hash_password(password)
    conn = connect_admin_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO admins (id, username, password_hash) VALUES (?, ?, ?)
    ''', (user_id, username, password_hash))
    conn.commit()
    conn.close()

def is_admin_user(username, password):
    # Check if the provided username and password match an admin user
    conn = connect_admin_db()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM admins WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return verify_password(row[0], password)
    return False