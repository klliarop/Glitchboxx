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

def format_message(message):
    return f"*** {message} ***"
