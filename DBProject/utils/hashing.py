import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def secure_compare(a, b):
    if a is None or b is None:
        return False
    return a == b
