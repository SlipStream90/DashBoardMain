<<<<<<< HEAD
import random
from werkzeug.security import check_password_hash
import pyotp

def otpmaker():
    key="Test"
    totp=pyotp.TOTP(key,interval=30)
    x=totp.now()
    global main
    main=''.join(x)
    return main

def check_password(hashed_password, user_password):
    return check_password_hash(hashed_password, user_password)
=======
import random
from werkzeug.security import check_password_hash

def otpmaker():
    return "".join([str(random.randint(0, 9)) for _ in range(6)])

def check_password(hashed_password, user_password):
    return check_password_hash(hashed_password, user_password)
>>>>>>> d9514b76b8bb3845c664cb087a3c05eee1a58c18
