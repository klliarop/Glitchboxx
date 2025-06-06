from flask import Flask, request, jsonify  # Import Flask and related modules
import sqlite3  # For SQLite database connection
import uuid  # For generating unique user IDs
import hashlib  # For password hashing
import os  # For file path operations

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))  # Set up base directory
DATABASE = os.path.join(BASE_DIR, "data", "users.db")  # Set database path

app = Flask(__name__)  # Initialize Flask app
app.secret_key = 'your_secret_key'  # Secret key for session management

def validate_username(username):
    if len(username) < 3 or len(username) > 20:
        return False
    if not username.isalnum():
        return False
    return True

def validate_password(password):
    if len(password) < 8:
        return False
    return True

def get_db():
    # Connect to the SQLite database and set row factory for dict-like access
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password_with_salt(password, salt=None):
    # Hash a password with a random salt using SHA-256
    if not salt:
        salt = os.urandom(16).hex()  # Generate a random salt if not provided
    hash_ = hashlib.sha256((salt + password).encode()).hexdigest()  # Hash the salt+password
    return f"{salt}${hash_}"  # Return salt and hash separated by $

def create_user(username, password):
    # Create a new user with a unique ID and salted password hash
    user_id = str(uuid.uuid4())  # Generate unique user ID
    password_hash = hash_password_with_salt(password)  # Hash password with salt
    db = get_db()  # Connect to database
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO users (id, username, password_hash) VALUES (?, ?, ?)", (user_id, username, password_hash))  # Insert user
        db.commit()
    except sqlite3.IntegrityError:
        return None  # Username already exists
    finally:
        db.close()  # Close database connection
    return user_id  # Return new user ID

@app.route('/register', methods=['POST'])
def register():
    # Handle registration POST request
    data = request.form  # Get form data from request
    username = data.get("username")
    password = data.get("password")

    if not validate_username(username):
        return jsonify({"message": "Invalid username"}), 400
    if not validate_password(password):
        return jsonify({"message": "Password too short. Must be at least 8 characters long."}), 400

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400  # Require both fields

    user_id = create_user(username, password)  # Attempt to create user
    if user_id:
        return jsonify({"message": "Registration successful", "user_id": user_id}), 200  # Success
    else:
        return jsonify({"message": "Username already exists"}), 400  # Username taken

if __name__ == '__main__':
    app.run(debug=True, port=5002)  # Run Flask app in debug mode on port 5002