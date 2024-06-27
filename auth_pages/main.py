from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, abort, render_template, redirect, url_for, flash, request ,session ,make_response
from flask_bootstrap import Bootstrap5
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm,VerificationForm
import smtplib
from auth import Auth
import pymysql
from auth import Auth
import pyotp
from authlib.integrations.flask_client import OAuth
import json
import requests
from authlib.integrations.base_client import OAuthError
from functools import wraps
from flask_wtf.csrf import CSRFProtect
from flask import flash, redirect, url_for, render_template
from werkzeug.security import generate_password_hash


SITE_KEY = "0x4AAAAAAAdUmFGg2g9knIqh"
SECRET_KEY = "0x4AAAAAAAdUmMJVOcNUpPg6Veq9RP_LucU"

def fetch_email(): 
    # To connect MySQL database 
    conn = pymysql.connect(host = "tib.cvywu8ws0g6h.eu-north-1.rds.amazonaws.com",user = 'admin',password="Shanu0921",database= 'api_testing',port= 3306) 
      
    cur = conn.cursor() 
    cur.execute("select Email from auth") 
    output = cur.fetchall() 
    result = [ i[0] for i in output]

    # To close the connection 
    conn.close()  

    return result  



def mysqlconnect(): 
    # To connect MySQL database 
    conn = pymysql.connect(host = "tib.cvywu8ws0g6h.eu-north-1.rds.amazonaws.com",user = 'admin',password="Shanu0921",database= 'api_testing',port= 3306) 
      
    cur = conn.cursor() 
    cur.execute("select Email,Password from auth") 
    output = cur.fetchall() 
    
    # To close the connection 
    conn.close()    

    return output



app = Flask(__name__)

app.config['SECRET_KEY'] = '57ttYGBVSBCKJsshudsstyeat'
Bootstrap5(app)

appConf = {
    "OAUTH2_CLIENT_ID": "235325144157-2ajn6g0dck5it7q7lb511lo4evkj69mk.apps.googleusercontent.com",
    "OAUTH2_CLIENT_SECRET": "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",
    "OAUTH2_META_URL": "https://accounts.google.com/.well-known/openid-configuration",
    "FLASK_SECRET": "ajkdvbahvakdvsdkvjbnsdkvb",
    "FLASK_PORT": 5001
}

csrf = CSRFProtect(app)


app.secret_key = appConf.get("FLASK_SECRET")
oauth = OAuth(app)

oauth.register(
    "myApp",
    client_id=appConf.get("OAUTH2_CLIENT_ID"),
    client_secret=appConf.get("OAUTH2_CLIENT_SECRET"),
    server_metadata_url=appConf.get("OAUTH2_META_URL"),
    client_kwargs={
        "scope": "openid profile email https://www.googleapis.com/auth/user.birthday.read https://www.googleapis.com/auth/user.gender.read https://www.googleapis.com/auth/userinfo.profile"
    }
)


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        store=mysqlconnect()
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
            print('The provided Turnstile token was not valid!', 'error') 
            return redirect(url_for('login'))


        data = request.form
        email = data["email"]
        password = data["password"]

        user = next((x for x in store if x[0] == email), None)

        if user:
            if check_password_hash(user[1], password):
                return redirect(url_for('verify'))
            else:
                flash("Invalid password", "error")
        else:
            flash("Invalid email", "error")

    return render_template("login.html", site_key=SITE_KEY)



@app.route("/home")
def home():
    return render_template("home.html", session=session.get("user"),
                           pretty=json.dumps(session.get("user"), indent=4))


@app.route("/signin-google")
def googleCallback():

    try:
        token = oauth.myApp.authorize_access_token()

    except OAuthError as e:
        # Handle access denied or other OAuth errors
        # flash(f"Authentication failed: {str(e)}", "error")
        return redirect(url_for("login"))

    # Fetch user info from Google API
    user_info_response = requests.get(
        f'https://www.googleapis.com/oauth2/v1/userinfo?access_token={token["access_token"]}',
        headers={'Authorization': f'Bearer {token["access_token"]}'}
    )

    user_info = user_info_response.json()

    # Fetch additional user info
    personDataUrl = "https://people.googleapis.com/v1/people/me?personFields=genders,birthdays"
    person_data_response = requests.get(personDataUrl, headers={
        "Authorization": f"Bearer {token['access_token']}"
    })
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
            revoke_url = "https://accounts.google.com/o/oauth2/revoke"
            requests.post(revoke_url, params={"token": token})

    session.clear()
    return redirect(url_for("login"))



#page for new account         


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )

        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        contact = form.contact.data
        password = hash_and_salted_password

        # Check if email already exists
        existing_emails = fetch_email()
        print(fetch_email())
        if email in existing_emails:
            flash("This email is already registered. Please use a different email.", "danger")
        else:
            auth = Auth().store_credentials(first_name, last_name, email, password, contact)
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))

    return render_template("register.html", form=form)

def otpmaker():
    key="Test"
    totp=pyotp.TOTP(key,interval=240)
    x=totp.now()
    global main
    main=''.join(x)

    return main
@app.route("/forget",methods=["GET","POST"])
def forgetpassword():
    form = VerificationForm()
    print(fetch_email())
    if form.validate_on_submit():
        email = form.email.data
        otp = otpmaker()
        store=fetch_email()
        for x in store:
            if x == email:
                print(x[0])  
                port = 465  # For SSL
                smtp_server = "smtp.gmail.com"
                MAIL_ADDRESS = "ramborudra3@gmail.com"
                Test_Receiver = "adityasingh0602006@gmail.com"
                MAIL_APP_PW = "pkseyysjcofditlk"
                subject = "New Message"
                body = f"OTP: {otp}"
                msg = MIMEMultipart()
                msg['From'] = MAIL_ADDRESS
                msg['To'] = Test_Receiver
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))
                with smtplib.SMTP_SSL(smtp_server, port) as server:
                    server.login(MAIL_ADDRESS, MAIL_APP_PW)
                    server.send_message(msg)
                 # Assuming you have an 'otp' route
            else:
                print("Email not found", "error")
                    
                
    return render_template("verify.html", form=form)



#page for 2fa verification
@app.route("/verification", methods=["GET", "POST"])
def verify():
    form = VerificationForm()
    print(fetch_email())
    if form.validate_on_submit():
        email = form.email.data
        otp = otpmaker()
        store=fetch_email()
        for x in store:
            if x == email:
                print(x[0])  
                port = 465  # For SSL
                smtp_server = "smtp.gmail.com"
                MAIL_ADDRESS = "ramborudra3@gmail.com"
                Test_Receiver = "adityasingh0602006@gmail.com"
                MAIL_APP_PW = "pkseyysjcofditlk"
                subject = "New Message"
                body = f"OTP: {otp}"
                msg = MIMEMultipart()
                msg['From'] = MAIL_ADDRESS
                msg['To'] = Test_Receiver
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))
                with smtplib.SMTP_SSL(smtp_server, port) as server:
                    server.login(MAIL_ADDRESS, MAIL_APP_PW)
                    server.send_message(msg)
                 # Assuming you have an 'otp' route
            else:
                print("Email not found", "error")
                    
                
    return render_template("verify.html", form=form)



@app.route("/DashBoard",methods=["GET","POST"])
def DashBoard():
    return render_template("DashBoard.html")



port = 465  # For SSL
smtp_server = "smtp.gmail.com"
MAIL_ADDRESS = "ramborudra3@gmail.com"
MAIL_APP_PW = "pkseyysjcofditlk"

@app.route("/contact", methods=["GET", "POST"])
def contact():
     if request.method == "POST":
         data = request.form
         send_email(data["name"], data["email"], data["phone"], data["message"])
         return render_template("contact.html", msg_sent=True)
     return render_template("contact.html", msg_sent=False)


def send_email(name, email, phone, message):

    subject = "New Message"
    body = f"Name: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message} "
    
    msg = MIMEMultipart()
    msg['From'] = MAIL_ADDRESS
    msg['To'] = MAIL_ADDRESS
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))
    
    with smtplib.SMTP_SSL(smtp_server, port) as server:
        server.login(MAIL_ADDRESS, MAIL_APP_PW)
        server.send_message(msg)












if __name__ == "__main__":
    app.run(debug=True, port=5001)