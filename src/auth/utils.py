# Utility functions for password hashing, password verification, and user ID generation
# Needed for admin.py

import bcrypt  # Import bcrypt for password hashing and checking

def hash_password(password):
    import bcrypt  # Redundant: bcrypt is already imported at the top
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')  # Hash the password and decode to string

def check_password(hashed_password, user_password):
    # Check if the provided password matches the hashed password
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password.encode('utf-8'))

def generate_user_id():
    import uuid  # Import uuid only in this function (could be imported at the top for clarity)
    return str(uuid.uuid4())  # Generate and return a unique user ID as a string