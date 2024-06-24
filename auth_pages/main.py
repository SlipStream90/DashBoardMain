from datetime import datetime
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm
from sqlalchemy import Column, Integer, String, DateTime
import os
import smtplib
from auth import Auth
import pymysql
from auth import Auth
import pyotp


 

def mysqlconnect(): 
    # To connect MySQL database 
    conn = pymysql.connect(host = "tib.cvywu8ws0g6h.eu-north-1.rds.amazonaws.com",user = 'admin',password="Shanu0921",database= 'api_testing',port= 3306) 
      
    cur = conn.cursor() 
    cur.execute("select Email,Password from auth") 
    output = cur.fetchall() 
    print(output)
    global Store
    Store=output
    
    # To close the connection 
    conn.close()    

  

mysqlconnect()

app = Flask(__name__)

app.config['SECRET_KEY'] = '57ttYGBVSBCKJsshudsstyeat'
Bootstrap5(app)



@app.route("/",methods=["GET","POST"])
def login():
    
    if request.method == "POST":
        data = request.form
        email =  data["email"]
        password = data["password"] 
        print(email)
        print(password)
        for x in Store:
            if not x[0] == email :
                flash("Invalid Email")
            elif not check_password_hash(x[1], password):
                flash("Invalid password")
            else:
                return redirect(url_for("verify")) 
            
    return render_template("login.html",current_user=current_user)

       


#page for new account         

@app.route("/register",methods=["GET","POST"])
def register():

    form = RegisterForm()
    if form.validate_on_submit():
        
        #if user:
        #    # User already exists
        #    flash("You've already signed up with that email, log in instead!")

        #    return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )

        First_name = form.first_name.data
        Last_name = form.last_name.data
        email = form.email.data
        contact = form.contact.data

        password=hash_and_salted_password,

        auth = Auth().store_credentials(First_name,Last_name,email,password,contact)

        return redirect(url_for("login"))
    
    return render_template("login.html",form=form,current_user=current_user)

def otpmaker():
    key="Test"
    totp=pyotp.TOTP(key,interval=240)
    x=totp.now()
    global main
    main=''.join(x)

    return main


#page for 2fa verification
@app.route("/verification",methods=["GET","POST"])
def verify():
    if request.method=="POST":
        data=request.form
        email=data["email"]
        otp=otpmaker()
        for x in Store:
            if x[0]==email:
                port = 465  # For SSL
                smtp_server = "smtp.gmail.com"
                MAIL_ADDRESS = "databasetester015@gmail.com"
                MAIL_APP_PW = "azszaoypedtvrtua"
                subject = "New Message"
                body = f"OTP: {otp}"
                msg = MIMEMultipart()
                msg['From'] = MAIL_ADDRESS
                msg['To'] = 'adityasingh0602006@gmail.com'
                msg['Subject'] = subject

                msg.attach(MIMEText(body, 'plain'))
    
                with smtplib.SMTP_SSL(smtp_server, port) as server:
                    server.login(MAIL_ADDRESS, MAIL_APP_PW)
                    server.send_message(msg)
                return redirect(url_for("otp"))  

            else:
                flash("Email Id not matching")    
                
    return render_template("verify.html",current_user=current_user)



#page for 2fa verification
@app.route("/OTP",methods=["GET","POST"])
def otp():
    if request.method=="POST":
        data=request.form
        OTP=data["OTP"]
        if main==OTP:
            return redirect(url_for("DashBoard"))
        else:
            flash("Incorrect OTP")    
                
    return render_template("Verify2(otp).html",current_user=current_user)

@app.route("/DashBoard",methods=["GET","POST"])
def DashBoard():
    return render_template("DashBoard.html",current_user=current_user)



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
     return render_template("contact.html", msg_sent=False,current_user=current_user)


def send_email(name, email, phone, message):
    
    subject = "New Message"
    body = f"Name: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}"
    
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