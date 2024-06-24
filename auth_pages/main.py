from datetime import datetime
from datetime import date
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
    global totp
    totp=pyotp.TOTP(key,interval=240)
    x=totp.now()
    global main
    main=''.join(x)



#page for 2fa verification
@app.route("/verification",methods=["GET","POST"])
def verify():
    if request.method=="POST":
        data=request.form
        email=data["email"]
        otpmaker()
        for x in Store:
            if x[0]==email:
                content = main # Enter your content here
                mail = smtplib.SMTP('smtp.gmail.com', 587)
                mail.ehlo()
                mail.starttls()
                mail.login('t3405146@gmail.com', 'cipulacjxurclamn')
                header = 'To:' + 'User' + '\n' + 'From:' \
                    + 'Tib' + '\n' + 'Subject:One Time Password\n'
                content = header + content
                mail.sendmail('t3405146@gmail.com','adityasingh0602006@gmail.com', content) # (1) = Sender, (2) = Receiver
                mail.close()
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
            return redirect(url_for("home"))
        else:
            flash("Incorrect OTP")    
                
    return render_template("Verify2(otp).html",current_user=current_user)











if __name__ == "__main__":
    app.run(debug=True, port=5001)