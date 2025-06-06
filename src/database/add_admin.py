import sqlite3  # For SQLite database operations
import uuid     # For generating unique user IDs
import bcrypt   # For secure password hashing

ADMIN_DB_PATH = "/home/user/Desktop/sandbox_db/data/admin.db"  # Path to the admin database

def hash_password(password):
    # Hash the password using bcrypt and return as a decoded string
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def add_admin(username, password):
    # Add a new admin user to the database with a hashed password
    user_id = str(uuid.uuid4())  # Generate a unique user ID
    password_hash = hash_password(password)  # Hash the provided password
    conn = sqlite3.connect(ADMIN_DB_PATH)  # Connect to the admin database
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO admins (id, username, password_hash) VALUES (?, ?, ?)
    ''', (user_id, username, password_hash))  # Insert the new admin record
    conn.commit()  # Commit the transaction
    conn.close()   # Close the database connection
  
if __name__ == "__main__":
   # add_admin("glitchbox_admin", "1J}ZrNSif9T,")  # Example (commented out) admin creation
    add_admin("admin", "admin")  # Add an admin with username "kl" and password "kl"