import os
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'we-will-succeed-123'

app.config["MONGO_DBNAME"] = "onlinecookbook"
app.config["MONGO_URI"] = "mongodb://admin:Sameday123@ds161112.mlab.com:61112/onlinecookbook"

mongo = PyMongo(app)

# User functions ---------------------------------------------------------------

def user_has_logged_in(email):
    session['user'] = email

def determine_current_user(session_data):
    if 'user' in session:
        return session['user']
    else:
        return "guest"

def validate_password_on_log_in(email_given, password_given):
    
    """
    Here we will append a message to a list if the email address exists, if the password matches an okay status will be added,
    if the password is wrong an incorrect status will be added.  If the email address doesn't exist no message will be added
    and a message will be advised accordingly
    """
    
    users = mongo.db.Users.find()    
    log_on_validation_status = []
        
    for user in users:
        if email_given == user["email"] and password_given == user["password"]:
            user_has_logged_in(email_given)
            log_on_validation_status.append("username & password match")
            break
        elif email_given == user["email"] and password_given != user["password"]:
            log_on_validation_status.append("username found, password incorrect")
            break
        
    if log_on_validation_status == []:
        flash("I'm sorry, email address {} does not appear to have been registered.  Please sign up now or try again!".format(email_given))
    elif log_on_validation_status[0] == "username & password match":
        return True
    elif log_on_validation_status[0] == "username found, password incorrect":
        flash("I'm sorry, the password you entered does not match with our records.  Please feel free to try again!")

# Views ------------------------------------------------------------------------

@app.route('/')
def home():
    current_user = determine_current_user(session)
    return render_template("home.html", users = mongo.db.Users.find(), username=current_user, page_title="Home")
    
@app.route('/sign_up')
def sign_up():
    return render_template("signup.html", users = mongo.db.Users.find(), username="guest", page_title="Sign Up")
    
@app.route('/add_new_user', methods=["POST"])
def add_new_user():
    
    users = mongo.db.Users.find()
    existing_user = 0
    for user in users:
        if request.form['email'] == user['email']:
            existing_user += 1
    
    if existing_user != 0 :
        flash("I'm sorry, this email address -  {}, has already been registered.\n  Please log in if you've signed up previously or try a different email address.".format(request.form['email']))
        return redirect(url_for('sign_up'))
    else:
        mongo.db.Users.insert_one(request.form.to_dict())
        user_has_logged_in(request.form['email'])
        flash("Hi {}, thanks for registering.\n  You may now add your own recipes and receive or write reviews!\n Good luck!".format(request.form['first_name']))
        return redirect(url_for('home'))

@app.route('/log_in.html', methods=["GET", "POST"])
def log_in():
    session.pop('user', None)
    
    if request.method == "POST":
        """
        Validate_password_on_log_in will check to see if a user is already signed up and then if the password
        given matches the users stored password
        """
        if validate_password_on_log_in(request.form["email"].lower(), request.form["password"]) == True:
            return redirect(url_for('home'))
        else:
            return render_template("log_in.html", page_title="Log In", username="guest")
    return render_template("log_in.html", page_title="Log In", username="guest")

@app.route('/logout.html')
def logout():
    session.pop('user', None)
    current_user = determine_current_user(session)
    return redirect(url_for('home'))
    
@app.route('/<username>/profile.html', methods=["GET", "POST"])
def profile(username):
    user = mongo.db.Users.find_one({"email": session["user"]})
    return render_template("profile.html", page_title="Profile", username=session["user"], user=user)

@app.route('/update_user/<username>', methods=["POST"])
def update_user(username):
    
    users = mongo.db.Users.find()
    email_belongs_to_another_user = False
    
    for user in users:
        if request.form['email'].lower() == user['email'].lower() and user['email'].lower() != session['user'].lower():
            email_belongs_to_another_user = True
    
    if email_belongs_to_another_user:        
        flash("I'm sorry, the email your trying to update to is already registered to another user, please try a different one or log in if this is already your account.")
        return redirect(url_for('profile', username=username))    
    else:        
        mongo.db.Users.update(
        {"email": username},
        {'first_name': request.form['first_name'],
        'surname': request.form['surname'],
        'email': request.form['email'],
        'password': request.form['password'],
        'country': request.form['country'],
        'user_photo': request.form['user_photo']})
        flash("Your details have been updated!")
        
        session.pop('user', None)
        user_has_logged_in(request.form['email'])
        
        return redirect(url_for('profile', username=session['user']))

@app.route('/ingredients.html')
def ingredients():
    ingredients = mongo.db.ingredients.find()
    return render_template("ingredients.html", ingredients_list = ingredients, page_title="Ingredients")

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
    port=int(os.environ.get('PORT')),
    debug=True)