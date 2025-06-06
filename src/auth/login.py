from flask import Flask, request, session, jsonify  # Import Flask and related modules
import sqlite3  # For SQLite database connection
import hashlib  # For password hashing
import os  # For file path operations

# Set up base directory and database path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATABASE = os.path.join(BASE_DIR, "data", "users.db")

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secret key for session management

def get_db():
    # Connect to the SQLite database and set row factory for dict-like access
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    # Hash a password using SHA-256 (no salt)
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password, provided_password):
    # Verify a password against the stored hash
    if '$' in stored_password:
        # If the stored password contains a salt, split and hash accordingly
        salt, hash_ = stored_password.split('$', 1)
        return hashlib.sha256((salt + provided_password).encode()).hexdigest() == hash_
    else:
        # Otherwise, hash the provided password and compare
        return hashlib.sha256(provided_password.encode()).hexdigest() == stored_password

@app.route('/login', methods=['POST'])
def login():
    # Handle login POST request
    data = request.form  # Get form data from request
    username = data.get("username")
    password = data.get("password")

    db = get_db()  # Connect to the database
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))  # Query user by username
    user = cursor.fetchone()  # Fetch user record
    db.close()  # Close database connection

    # Check if user exists and password is correct
    if user and verify_password(user["password_hash"], password):
        session["user_id"] = user["id"]  # Store user ID in session
        return jsonify({"message": "Login successful", "user_id": user["id"]}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401  # Invalid credentials

@app.route('/logout')
def logout():
    # Handle logout by removing user_id from session
    session.pop("user_id", None)
    return jsonify({"message": "Logged out"}), 200

if __name__ == '__main__':
    # Run the Flask app in debug mode on port 5001
    app.run(debug=True, port=5001)