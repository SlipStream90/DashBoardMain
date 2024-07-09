from flask import render_template, request, redirect, url_for, session, flash,jsonify
from models import fetch_email, recover_passkey, fetch_users,Profile_build_main,get_db_connection
from email_service import send_email
from forms import RegisterForm, VerificationForm, OTPForm, ForgetPass
from utils import otpmaker, check_password
import requests
import json
from authlib.integrations.flask_client import OAuth
from authlib.integrations.base_client import OAuthError
from config import appConf, SITE_KEY ,SECRET_KEY 
from werkzeug.security import generate_password_hash
from models import get_db_connection
import pytz
import time
from datetime import datetime, timedelta
import json
from functools import wraps
import os
from functools import wraps
from werkzeug.security import safe_str_cmp
import secrets

AUTH_TOKEN = "your_secret_auth_token"






def register_routes(app,oauth):
    @app.route("/", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            store = fetch_users()
            token = request.form.get('cf-turnstile-response')
            ip = request.remote_addr

            form_data = {
                'secret': SECRET_KEY,
                'response': token,
                'remoteip': ip
            }

            response = requests.post('https://challenges.cloudflare.com/turnstile/v0/siteverify', data=form_data)
            outcome = response.json()
            print(outcome)

            if not outcome['success']:
                flash('The provided Turnstile token was not valid!', 'error')
                return redirect(url_for('login'))

            email = request.form["email"]
            session["login_email"] = email
            password = request.form["password"]

            user = next((x for x in store if x[0] == email), None)

            if user and check_password(user[1], password):
                return redirect(url_for('two_step'))
            else:
                flash("Invalid email or password", "error")

        return render_template("login.html", site_key=SITE_KEY)

    @app.route("/home")
    def home():
        return render_template("home.html", session=session.get("user"),
                               pretty=json.dumps(session.get("user"), indent=4))

    @app.route("/signin-google")
    def googleCallback():
        try:
            token = oauth.myApp.authorize_access_token()
        except OAuthError:
            return redirect(url_for("login"))

        user_info_response = requests.get(
            f'https://www.googleapis.com/oauth2/v1/userinfo?access_token={token["access_token"]}',
            headers={'Authorization': f'Bearer {token["access_token"]}'}
        )
        user_info = user_info_response.json()

        person_data_response = requests.get("https://people.googleapis.com/v1/people/me?personFields=genders,birthdays",
                                            headers={"Authorization": f"Bearer {token['access_token']}"})
        person_data = person_data_response.json()

        token["user_info"] = user_info
        token["person_data"] = person_data
        session["user"] = token
        return redirect(url_for("home"))

    @app.route("/google-login")
    def googleLogin():
        session.clear()
        redirect_uri = url_for("googleCallback", _external=True)
        return oauth.myApp.authorize_redirect(redirect_uri=redirect_uri)

    @app.route("/logout")
    def logout():
        if "user" in session:
            token = session["user"].get("access_token")
            if token:
                requests.post("https://accounts.google.com/o/oauth2/revoke", params={"token": token})
        session.clear()
        return redirect(url_for("login"))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        form = RegisterForm()
        if form.validate_on_submit():
            hash_and_salted_password = generate_password_hash(
                form.password.data, method='pbkdf2:sha256', salt_length=8)
            first_name = form.first_name.data
            last_name = form.last_name.data
            email = form.email.data
            contact = form.contact.data
            password = hash_and_salted_password

            session.update({
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "password": password,
                "EMAIL": email,
                "contact": contact
            })

            if email in fetch_email():
                flash("This email is already registered. Please use a different email.", "danger")
            else:
                return redirect(url_for("mail_otp"))

        return render_template("register.html", form=form)

    @app.route("/verification", methods=["GET", "POST"])
    def verify_pass():
        form = VerificationForm()
        if form.validate_on_submit():
            email = form.email.data
            otp = otpmaker()
            session["verify_otp"] = otp

            if email in fetch_email():
                session["verify_email"] = email
                send_email(email, f"OTP: {otp}", "New Message")
                return redirect(url_for('forgot_pass'))

            flash("This email is not registered.", "danger")

        return render_template("verify_pass.html", form=form)


    @app.route("/DashBoard", methods=["GET", "POST"])
    def DashBoard():
        return render_template("DashBoard.html")

    @app.route("/contact", methods=["GET", "POST"])
    def contact():
        if request.method == "POST":
            data = request.form
            send_email(data["email"], f"Name: {data['name']}\nPhone: {data['phone']}\nMessage: {data['message']}", "New Message")
            return render_template("contact.html", msg_sent=True)
        return render_template("contact.html", msg_sent=False)

    def is_otp_expired():
        current_time = time.time()
        expiry_time = session.get('OTP_EXPIRY')
        if isinstance(expiry_time, (int, float)):
            return current_time > expiry_time
        elif isinstance(expiry_time, str):
            try:
                expiry_datetime = datetime.fromisoformat(expiry_time)
                return datetime.now() > expiry_datetime
            except ValueError:
                return True
        return True

    def send_new_otp(email, subject="New Message"):
        otp = otpmaker()
        send_email(email, f"OTP: {otp}", subject)
        session["otp"] = otp
        session['OTP_EXPIRY'] = time.time() + 30

    @app.route("/two-step", methods=["GET", "POST"])
    def two_step():
        form = OTPForm()
        email = session.get("login_email")

        if request.method == "GET" or (request.method == "POST" and 'resend_otp' in request.form):
            if not session.get('OTP_SENT', False) or is_otp_expired() or 'resend_otp' in request.form:
                send_new_otp(email)
                session['OTP_SENT'] = True
                if request.method == "POST":  
                    return "", 204  # Return empty response for AJAX request

        if request.method == "POST" and 'resend_otp' not in request.form:
            otp_input = request.form["otp"]
            if is_otp_expired():
                flash("OTP has expired. Please request a new one.", "danger")
            elif otp_input == session.get("otp"):
                session.clear()
                return redirect(url_for("DashBoard"))
            else:
                flash("Incorrect OTP", "danger")

        return render_template("2FA.html", form=form)

    @app.route("/forgot", methods=["GET", "POST"])
    def forgot_pass():
        form = ForgetPass()
        email = session.get("verify_email")

        if request.method == "GET" or (request.method == "POST" and 'resend_otp' in request.form):
            if not session.get('verify_otp') or is_otp_expired() or 'resend_otp' in request.form:
                send_new_otp(email, "Password Recovery OTP")
                if request.method == "POST":
                    return "", 204  # Return empty response for AJAX request

        if request.method == "POST" and 'resend_otp' not in request.form:
            if form.validate_on_submit():
                if is_otp_expired():
                    flash("OTP has expired. Please request a new one.", "danger")
                elif form.otp.data == session.get("verify_otp"):
                    hash_and_salted_password = generate_password_hash(
                        form.password.data,
                        method='pbkdf2:sha256',
                        salt_length=8
                    )
                    recover_passkey(hash_and_salted_password, email)
                    session.pop("verify_otp", None)
                    flash("Password Changed. Please log in.", "success")
                    return redirect(url_for('login'))
                else:
                    flash("Invalid OTP", "danger")

        return render_template("forgot_password.html", form=form)

    @app.route("/email-otp", methods=["GET", "POST"])
    def mail_otp():
        form = OTPForm()
        email = session["email"]

        if request.method == "GET" or (request.method == "POST" and 'resend_otp' in request.form):
            if not session.get('otp') or is_otp_expired() or 'resend_otp' in request.form:
                send_new_otp(email)
                if request.method == "POST":
                    return "", 204  # Return empty response for AJAX request

        if request.method == "POST" and 'resend_otp' not in request.form:
            if form.validate_on_submit():
                otp = form.otp.data
                if is_otp_expired():
                    flash("OTP has expired. Please request a new one.", "danger")
                elif otp == session.get("otp"):
                    data = {
                        "email": session["email"],
                        "password": session["password"],
                        "First Name": session["first_name"],
                        "Last Name": session["last_name"]
                    }
                    conn = get_db_connection()
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO auth (Email, Password, first_name, last_name, Contact) VALUES (%s, %s, %s, %s, %s)",
                        (data["email"], data["password"], data["First Name"], data["Last Name"], session["contact"])
                    )
                    conn.commit()
                    conn.close()
                    return redirect(url_for("login"))
                else:
                    flash("Incorrect OTP", "danger")

        return render_template("email_verify.html", form=form)
    

    #@app.route("/profile",methods=["GET","POST"])
    #def profile_build():
        form=Profile_store()
        Organization=form.OrgName.data
        Gender=form.Gender.data
        Post=form.Post.data
        Profile_build_main(Organization,Gender,Post)

    

    #SECRET_TOKEN = os.environ.get('SECRET_TOKEN', 'default_secret_token')
    SECRET_TOKEN = "tR7Hs9Ky3Lm1Pq4Xw2Zb8Nf5Vj7Cd6"

    def require_auth(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({"error": "Authorization header is missing"}), 401
            
            try:
                auth_type, token = auth_header.split()
                if auth_type.lower() != 'bearer':
                    return jsonify({"error": "Bearer token required"}), 401
                
                if not secrets.compare_digest(token, SECRET_TOKEN):
                    return jsonify({"error": "Invalid token"}), 401
            except ValueError:
                return jsonify({"error": "Invalid Authorization header format"}), 401

            return f(*args, **kwargs)
        return decorated

    @app.route('/protected')
    @require_auth
    def protected():
        return jsonify({"message": "This is a protected route"})


    @app.route("/device", methods=['GET'])
    @require_auth
    def handle_device():
        device_id = request.args.get('device_id')
        conn = get_db_connection()
        cur = conn.cursor()
        
        if not device_id:
            return jsonify({"error": "No device ID provided"}), 400
        
        try:
            # Use parameterized queries to prevent SQL injection
            cur.execute("UPDATE token_device SET Device_id = %s WHERE Device_id IS NULL", (device_id,))
            conn.commit()
            
            cur.execute("SELECT Token_id FROM token_device WHERE Device_id = %s", (device_id,))
            token = cur.fetchall()
            
            token_data = jsonify({"device_id": device_id, "token": token}), 200
            return token_data
        
        except Exception as e:
            conn.rollback()
            return jsonify({"error": str(e)}), 500
        
        finally:
            cur.close()
            conn.close()

   














   






    
