from flask import Flask, request, session, jsonify
import sqlite3
import hashlib
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATABASE = os.path.join(BASE_DIR, "data", "users.db")

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password, provided_password):
    return stored_password == hash_password(provided_password)

@app.route('/login', methods=['POST'])
def login():
    data = request.form
    username = data.get("username")
    password = data.get("password")

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    db.close()

    if user and verify_password(user["password_hash"], password):
        session["user_id"] = user["id"]
        return jsonify({"message": "Login successful", "user_id": user["id"]}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401

@app.route('/logout')
def logout():
    session.pop("user_id", None)
    return jsonify({"message": "Logged out"}), 200

# if __name__ == '__main__':
#     app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True, port=5001) 
