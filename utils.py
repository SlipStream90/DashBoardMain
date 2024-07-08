import random
from werkzeug.security import check_password_hash
import string

def otpmaker():
    return "".join([str(random.randint(0, 9)) for _ in range(6)])

def check_password(hashed_password, user_password):
    return check_password_hash(hashed_password, user_password)

def generate_token(length=16):
    """Generate a random token of specified length"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

