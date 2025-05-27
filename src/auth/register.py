from flask import Flask, request, jsonify
import sqlite3
import uuid
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

def create_user(username, password):
    user_id = str(uuid.uuid4())
    password_hash = hash_password(password)
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO users (id, username, password_hash) VALUES (?, ?, ?)", (user_id, username, password_hash))
        db.commit()
    except sqlite3.IntegrityError:
        return None
    finally:
        db.close()
    return user_id

@app.route('/register', methods=['POST'])
def register():
    data = request.form
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    user_id = create_user(username, password)
    if user_id:
        return jsonify({"message": "Registration successful", "user_id": user_id}), 200
    else:
        return jsonify({"message": "Username already exists"}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5002)
