import re, generate, subprocess, os, env, logging
from tokenize import Ignore
from select import select
from typing import Sequence
from flask import Flask, flash, redirect, url_for, render_template, request, send_from_directory
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, extract, table, func, text, Sequence
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

app.logger.setLevel(logging.DEBUG)

POSTGRES_URL = env.DB_CONFIG['postgresUrl']
POSTGRES_USER = env.DB_CONFIG['postgresUser']
POSTGRES_PASS = env.DB_CONFIG['postgresPass']
POSTGRES_DB = env.DB_CONFIG['postgresDb']
DB_URL = 'postgresql://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER, pw=POSTGRES_PASS, url=POSTGRES_URL, db=POSTGRES_DB)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SECRET_KEY'] = 'Vive la République!'

db = SQLAlchemy(app)

class Monitor(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True )
    user = db.Column(db.String(120), unique=True, nullable=False)
    info = db.Column(JSONB)

    def __init__(self, user, info):
        self.user = user
        self.info = info

    def __repr__(self):
        return f"<User {self.user}>"

class User(db.Model, UserMixin):
     __tablename__ = 'systemusers'
     id = db.Column(db.Integer, primary_key=True)
     username = db.Column(db.String(20), unique=True, nullable=False)
     email = db.Column(db.String(40), unique=True, nullable=False)
     password = db.Column(db.String(172), nullable=False)

     def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

     def __repr__(self):
        return f"<User {self.username}>"

db.create_all()

# Create Default User
user = User.query.filter_by(username="sisyphus").first()
if user:
     pass
else:
     admin_user = User("sisyphus","sisyphus@gmail.com",generate_password_hash("sisyphus","sha256"))                  
     db.session.add(admin_user)
     db.session.commit()

# Flask Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
     return User.query.get(int(user_id))

@app.route("/")
def home():
     return render_template("home.html")

@app.route("/docs")
def docs():
     return render_template("docs.html")

@app.route("/generate-kubeconfig", methods=["POST", "GET"])
@login_required
def kube():
     if request.method == "POST":
       user_list_string = request.form["username"]
       user_list_list = re.split(',+', user_list_string)
       for username in user_list_list:
           groupname = request.form["groupname"]
           clustername = request.form["clustername"]
           kubeconfigname = username + "-" + clustername + "-kubeconfig"
           app.logger.debug('User Name is %s ,Group Name is %s ,Cluster Name is %s ,KubeConfig Name is %s ', username, groupname, clustername, kubeconfigname)

           new_generate = generate.KubeConfigGen(username,clustername,groupname)
           if new_generate.path_control():
               if new_generate.generate_csr():
                  new_generate.generate_kubeconfig()

                  infoo = {"clusters":[{"name":"devops-k8s-lab","groups":{"developer":"True"},"dates":{"developer":{"startDate":"21.12.2022"}}}]}

                  user = Monitor(username,infoo)
                  
                  db.session.add(user)
                  db.session.commit()

       #return send_from_directory("/Users/uguro/workspace/kubeConfig", kubeconfigname, as_attachment=True)
       return render_template("generate-kubeconfig.html")
     else:
       return render_template("generate-kubeconfig.html")

@app.route("/login", methods=["POST", "GET"])
def login():
     if request.method == "POST":
       uname = request.form["username"]
       upass = request.form["userpass"]
       app.logger.debug('Username is %s , Password is ******** ', uname )

       user = User.query.filter_by(username=uname).first()
       if user:
          # Check the hash of the password
          if check_password_hash(user.password, upass):
             login_user(user)
             #flash("Login Successful!")  Currently flash does not work.
             app.logger.debug('User %s successfully logged in! ', uname)
             return redirect(url_for("home"))
          else:
             #flash("Incorrect Password!")  Currently flash does not work.
             app.logger.info('Incorrect Password for user %s ', uname)
       else:
          #flash("User not found!")  Currently flash does not work.
          app.logger.info('User %s not found! ', uname)

     return render_template("login.html")

# Logout Function
@app.route("/logout", methods=["POST", "GET"])
@login_required
def logout():
     logout_user()
     #flash("You have been logged out!") Currently flash does not work.
     return redirect(url_for("login"))


@app.route("/new-user", methods=["POST", "GET"])
@login_required
def create_user():
     if request.method == "POST":
       username = request.form["username"]
       userpass = request.form["userpass"]
       useremail = request.form["useremail"]
       
       hashed_pw = generate_password_hash(userpass,"sha256")

       # I thought that to write a control flow to check if the user is already exist or not; But since same username or email could not used due to uniqueness of the column, it seems that its not necessary for now.

       app.logger.debug('Username is %s ,User Email is %s, Password is %s ', username , useremail , hashed_pw)

       systemuser = User(username, useremail, hashed_pw)
       db.session.add(systemuser)
       db.session.commit()

     return render_template("createuser.html")

if __name__ == "__main__":
    app.run(debug=True)
