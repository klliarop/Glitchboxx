import sqlite3  # For SQLite database operations

db_path = "/home/user/Desktop/sandbox_db/data/admin.db"  # Path to the admin database
conn = sqlite3.connect(db_path)  # Connect to the database
cursor = conn.cursor()  # Create a cursor object
cursor.execute('''
    CREATE TABLE IF NOT EXISTS admins (
        id TEXT PRIMARY KEY,  # Unique ID for each admin
        username TEXT NOT NULL UNIQUE,  # Unique username for each admin
        password_hash TEXT NOT NULL,  # Hashed password
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  # Timestamp of creation
    )
''')  # Create the admins table if it doesn't exist
conn.commit()  # Commit the transaction
conn.close()  # Close the database connection
print("admins table created (or already exists) in admin.db")  # Confirmation message