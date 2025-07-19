from collections import defaultdict

# Temporary memory (in-memory session tracking)
user_sessions = defaultdict(dict)

def update_user(phone, key, value):
    user_sessions[phone][key] = value

def get_user(phone):
    return user_sessions[phone]

def clear_user(phone):
    if phone in user_sessions:
        del user_sessions[phone]
