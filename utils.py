import random
from werkzeug.security import check_password_hash
import pyotp

def otpmaker():
    key="Test"
    totp=pyotp.TOTP(key,interval=240)
    x=totp.now()
    global main
    main=''.join(x)
    return main

def check_password(hashed_password, user_password):
    return check_password_hash(hashed_password, user_password)
