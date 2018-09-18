import os
from flask import Flask, render_template, redirect, url_for, request
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)

app.config["MONGO_DBNAME"] = "onlinecookbook"
app.config["MONGO_URI"] = "mongodb://admin:Sameday123@ds161112.mlab.com:61112/onlinecookbook"

mongo = PyMongo(app)

@app.route('/')
def home():
    return render_template("home.html", users = mongo.db.Users.find())

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
    port=int(os.environ.get('PORT')),
    debug=True)