from flask import Flask, redirect, url_for, render_template, request, send_from_directory
import re, generate
import subprocess,os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
import dbConfig

app = Flask(__name__)

#######
POSTGRES_URL = dbConfig.CONFIG['postgresUrl']
POSTGRES_USER = dbConfig.CONFIG['postgresUser']
POSTGRES_PASS = dbConfig.CONFIG['postgresPass']
POSTGRES_DB = dbConfig.CONFIG['postgresDb']
DB_URL = 'postgresql://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER, pw=POSTGRES_PASS, url=POSTGRES_URL, db=POSTGRES_DB)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
db = SQLAlchemy(app)

class Monitor(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(120), unique=True, nullable=False)
    info = db.Column(JSONB)

    def __init__(self, id, user, info):
        self.id = id
        self.user = user
        self.info = info

    def __repr__(self):
        return f"<User {self.user}>"

db.create_all()

#######

@app.route("/")
def home():
     return render_template("home.html")

@app.route("/about")
def info():
     return render_template("about.html")

@app.route("/docs")
def docs():
     return render_template("docs.html")


@app.route("/generate-kubeconfig", methods=["POST", "GET"])
def kube():
     if request.method == "POST":
       user_list_string = request.form["username"]
       user_list_list = re.split(',+', user_list_string)
       for username in user_list_list:
           groupname = request.form["groupname"]
           clustername = request.form["clustername"]
           kubeconfigname = username + "-" + clustername + "-kubeconfig"
           print("User Name      : " + username)
           print("Group Name     : " + groupname)
           print("KubeConfig Name: " + kubeconfigname)

           new_generate = generate.KubeConfigGen(username,clustername,groupname)
           if new_generate.path_control():
               if new_generate.generate_csr():
                  new_generate.generate_kubeconfig()

                  infoo = {"clusters":[{"name":"devops-k8s-lab","groups":{"developer":"True"},"dates":{"developer":{"startDate":"21.12.2022"}}}]}
                  user = Monitor(1,username,infoo)
                  db.session.add(user)
                  db.session.commit()

       #return send_from_directory("/Users/uguro/workspace/kubeConfig", kubeconfigname, as_attachment=True)
       return render_template("generate-kubeconfig.html")
     else:
       return render_template("generate-kubeconfig.html")

@app.route("/rbac-template", methods=["POST", "GET"])
def rbac():
     return render_template("rbac-template.html")

@app.route("/role-ops", methods=["POST", "GET"])
def role():
     return render_template("role-ops.html")

@app.route("/test")
def test():
     return render_template("new.html")

@app.route("/login", methods=["POST", "GET"])
def login():
     if request.method == "POST":
       user = request.form["username"]
       return redirect(url_for("user", usr=user))
     else:
       return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)
