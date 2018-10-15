import os
import json
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from bson.json_util import loads, dumps
from test_suite import *

app = Flask(__name__)
app.secret_key = 'we-will-succeed-123'

app.config["MONGO_DBNAME"] = "onlinecookbook"
app.config["MONGO_URI"] = "mongodb://admin:Sameday123@ds161112.mlab.com:61112/onlinecookbook"

mongo = PyMongo(app)

# Global Variables -------------------------------------------------------------

cusine_list = ['American', 'British', 'Caribbean', 'Chinese', 'French', 'Greek', 'Indian', 'Italian', 'Japanese', 'Mediterranean', 'Mexican', 'Moroccan', 'Spanish', 'Thai', 'Turkish', 'Vietnamese', 'Other']

# User functions ---------------------------------------------------------------

def user_has_logged_in(email):
    session['user'] = email
    this_user = mongo.db.Users.find_one({"email":session["user"]})
    this_user_id_bson = this_user["_id"]
    this_user_id_str = dumps(this_user_id_bson)
    extract_id_1 = this_user_id_str.replace('{"$oid": "', "")
    extract_id_2 = extract_id_1.replace('"}', "")
    session['user_id'] = extract_id_2
    print(session)
    
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

def does_record_already_exist(search_criteria, database_records):
    existing_record = 0
    for item in database_records:
        if request.form[search_criteria].lower() == item[search_criteria].lower():
            existing_record += 1
    
    if existing_record != 0:
        return True

# Search database functions ----------------------------------------------------

def recipe_already_exists(new_recipe_name):
    
    current_user = determine_current_user(session)
    if current_user == "guest":
        print("Not logged in")
    else:
        this_user = mongo.db.Users.find_one({"email":current_user})
        recipes = mongo.db.recipes.find()
        
        for recipe in recipes:
            if ObjectId(recipe["author"]) == this_user["_id"] and recipe["recipe_name"] == new_recipe_name:
                return True

# This function is now superceaded by the javascript code so that the ingredients can load without having to refresh the page but this function is equally as valid if the page was to be refreshed...

# def createThisRecipeIngredientsList(recipe_id):
#     new_recipe_ingredients_list = []
#     the_recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    
#     try:
#         for ingredient in the_recipe["recipe_ingredients"]:
#             for key, value in ingredient.iteritems():
#                 decoded_key = key.encode('utf-8')
#                 fully_decoded_key = decoded_key.replace(" ", "")
#                 this_ingredient = mongo.db.ingredients.find_one({"_id": ObjectId(fully_decoded_key)})
#                 new_recipe_ingredients_list.append({ this_ingredient["ingredient_name"] : value })
#     except:
#         new_recipe_ingredients_list = []
    
#     return new_recipe_ingredients_list
                
# Views ------------------------------------------------------------------------

@app.before_request
def before_request():
    protected_route = ['profile']
    if request.endpoint in protected_route and 'user' not in session:
        return redirect(url_for('log_in'))

@app.route('/')
def home():
    current_user = determine_current_user(session)
    return render_template("home.html", users = mongo.db.Users.find(), username=current_user, page_title="Home")

# User related views -----------------------------------------------------------

@app.route('/sign_up')
def sign_up():
    return render_template("signup.html", users = mongo.db.Users.find(), username="guest", page_title="Sign Up")
    
@app.route('/add_new_user', methods=["POST"])
def add_new_user():
    
    users = mongo.db.Users.find()
    
    if does_record_already_exist('email', users):
        flash("I'm sorry, this email address -  {}, has already been registered.\n  Please log in if you've signed up previously or try a different email address.".format(request.form['email']))
        return redirect(url_for('sign_up'))
    else:
        mongo.db.Users.insert_one(request.form.to_dict())
        user_has_logged_in(request.form['email'])
        flash("Hi {}, thanks for registering.\n  You may now add your own recipes and receive or write reviews!\n Good luck!".format(request.form['first_name']))
        return redirect(url_for('home'))

@app.route('/log_in', methods=["GET", "POST"])
def log_in():
    session.pop('user', None)
    
    if request.method == "POST":
        """
        Validate_password_on_log_in will check to see if a user is already signed up and then if the password
        given matches the users stored password
        """
        if validate_password_on_log_in(request.form["email"].lower(), request.form["password"]) == True:
            flash("Welcome back {}".format(session['user']))
            return redirect(url_for('recipes'))
        else:
            return render_template("log_in.html", page_title="Log In", username="guest")
    return render_template("log_in.html", page_title="Log In", username="guest")

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('user_id', None)
    current_user = determine_current_user(session)
    flash("You have logged out. Come back now you hear!")
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

# Ingredients related views ----------------------------------------------------

@app.route('/ingredients')
def ingredients():
    current_user = determine_current_user(session)
    ingredients = mongo.db.ingredients.find().sort([("ingredient_name", 1)])
    return render_template("ingredients.html", ingredients_list = ingredients, page_title="Ingredients", username=current_user)

@app.route('/add_ingredient/<recipe_id>')
def add_ingredient(recipe_id):
    current_user = determine_current_user(session)
    return render_template("add_ingredient.html", page_title="Add an Ingredient", username=current_user, recipe_id=recipe_id)

@app.route('/insert_ingredient/<recipe_id>', methods=["POST"])
def insert_ingredient(recipe_id):
    
    ingredients = mongo.db.ingredients.find()
    
    if does_record_already_exist('ingredient_name', ingredients):
        flash("I'm sorry, this ingredient -  {}, is already in the list.\n  Please check again and simply select it!".format(request.form['ingredient_name']))
        return redirect(url_for('ingredients'))
    else:
        mongo.db.ingredients.insert_one(request.form.to_dict())
        flash("{} has been added to the ingredients list.\n  Thanks for your input!".format(request.form['ingredient_name']))
        if recipe_id == "none":
            return redirect(url_for('ingredients'))
        else:
            return redirect(url_for('edit_recipe', recipe_id=recipe_id))
        
@app.route('/edit_ingredient/<ingredient_id>')
def edit_ingredient(ingredient_id):
    current_user = determine_current_user(session)
    the_ingredient = mongo.db.ingredients.find_one({"_id": ObjectId(ingredient_id)})
    return render_template('edit_ingredient.html', ingredient=the_ingredient, username=current_user)

@app.route('/<ingredient_id>/update_ingredient', methods=["POST"])
def update_ingredient(ingredient_id):
    try:
        mongo.db.ingredients.update(
        {"_id": ObjectId(ingredient_id)},
        {'ingredient_name': request.form['ingredient_name'],
        'ingredient_image_url': request.form['ingredient_image_url'],
        'allergens': request.form['allergens']
        })
    except:
        mongo.db.ingredients.update(
        {"_id": ObjectId(ingredient_id)},
        {'ingredient_name': request.form['ingredient_name'],
        'ingredient_image_url': request.form['ingredient_image_url']})
    flash("Ingredient updated!")
    return redirect(url_for('ingredients'))

# Recipe related views ---------------------------------------------------------

@app.route('/recipes')
def recipes():
    current_user = determine_current_user(session)
    try:
        user = mongo.db.Users.find_one({"email": session["user"]})
        user_id = session["user_id"]
    except:
        user = "guest"
        user_id = "guest"
        
    recipes = mongo.db.recipes.find().sort([("recipe_name", 1)])
    return render_template("recipes.html", recipes_list = recipes, page_title="Recipes", username=current_user, user=user, user_id = user_id)

@app.route('/add_recipe')
def add_recipe():
    current_user = determine_current_user(session)
    
    if current_user == "guest":
        flash("I'm sorry but you need to be logged in to add a recipe.  Log in or sign up and begin!")
        return redirect(url_for('recipes'))
    else:
        user = mongo.db.Users.find_one({"email": session["user"]})
        ingredients_list = mongo.db.ingredients.find()
        return render_template("add_recipe.html", page_title="Add a Recipe", username=current_user, cusines=cusine_list, user=user, ingredients=ingredients_list)

@app.route('/insert_recipe', methods=["POST"])
def insert_recipe():
    
    if recipe_already_exists(request.form['recipe_name']):
        flash("Oops, you already have a recipe called {}!  Please try again with a different name or edit the existing recipe.".format(request.form['recipe_name']))
        return redirect(url_for('recipes', current_user=session['user']))
    else:
        mongo.db.recipes.insert_one(request.form.to_dict())
        this_recipe = mongo.db.recipes.find_one({"recipe_name": request.form['recipe_name']})
        flash("{} has been to the recipes list.\n  Time to add some ingredients and instructions!".format(request.form['recipe_name']))
        return redirect(url_for('edit_recipe', recipe_id=this_recipe['_id']))

@app.route('/edit_recipe/<recipe_id>', methods=["GET", "POST"])
def edit_recipe(recipe_id):
    current_user = determine_current_user(session)
    user = mongo.db.Users.find_one({"email": session["user"]})
    the_recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    ingredients = mongo.db.ingredients.find().sort([("ingredient_name", 1)])
    
    return render_template("edit_recipe.html", page_title="Edit Recipe", username=current_user, user=user, cusines=cusine_list, this_recipe=the_recipe, ingredients=ingredients)

@app.route('/update_recipe/<recipe_id>', methods=["POST"])
def update_recipe(recipe_id):
    
    this_recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    
    # This code will update the recipe details if it already has ingredients contained within the recipe on the database...
    
    try:
        mongo.db.recipes.update(
            {"_id": ObjectId(recipe_id)},
            {'recipe_name': request.form['recipe_name'],
            'recipe_image_url': request.form['recipe_image_url'],
            'cusine': request.form['cusine'],
            'instructions': request.form['instructions'],
            'author': request.form['author'],
            'author_COO': request.form['author_COO'],
            'recipe_ingredients': this_recipe["recipe_ingredients"]
        })
        print("Had ingredients")
        
    # If it has no ingredients in the recipe then this will run instead (ignoring the request to update with the existing ingredients in the recipe)...
        
    except:
        mongo.db.recipes.update(
            {"_id": ObjectId(recipe_id)},
            {'recipe_name': request.form['recipe_name'],
            'recipe_image_url': request.form['recipe_image_url'],
            'cusine': request.form['cusine'],
            'instructions': request.form['instructions'],
            'author': request.form['author'],
            'author_COO': request.form['author_COO']
        })
    
    # If an ingredient has been added to the form for inclusion, this code will append it to the list...
    
    record_exists = False
    
    if request.form["ingredient_name"] != "":
        try:
            for ingredient in this_recipe["recipe_ingredients"]:
                for key, value in ingredient.iteritems():
                    if request.form["ingredient_name"] == key:
                        record_exists = True
                        break
            if record_exists == False:
                mongo.db.recipes.update(
                    {"_id": ObjectId(recipe_id)},
                    { "$push" : { "recipe_ingredients": {request.form["ingredient_name"] : request.form["ingredient_quantity"]}}}
                )
                print("Added")
            else:
                print("exists")
        except:
            mongo.db.recipes.update(
                {"_id": ObjectId(recipe_id)},
                { "$push" : { "recipe_ingredients": {request.form["ingredient_name"] : request.form["ingredient_quantity"]}}}
            )
            print("Added")
            
    return json.dumps({'status':'OK'});

@app.route('/delete_recipe/<recipe_id>', methods=["POST"])
def delete_recipe(recipe_id):
    mongo.db.recipes.remove({"_id": ObjectId(recipe_id)})
    return redirect(url_for('recipes'))


@app.route('/delete_ingredient_from_recipe/<recipe_id>/<ingredient_id>', methods=["POST"])
def delete_ingredient_from_recipe(recipe_id, ingredient_id):
    print(recipe_id)
    print(ingredient_id)
    
    this_recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    
    for ingredient in this_recipe["recipe_ingredients"]:
        ingredientKey = ingredient.keys()
        stringIngKey = ingredientKey[0].replace(" ", "")
        if stringIngKey == ingredient_id:
            print(ingredient)
            mongo.db.recipes.update(
            {'_id': ObjectId(recipe_id)}, 
            { "$pull": { "recipe_ingredients" : ingredient }},
            False, True);
            return json.dumps({'status':'OK'});
            break
        else:
            print("Couldn't match {} to {}".format(stringIngKey, ingredient_id))
    
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
    port=int(os.environ.get('PORT')),
    debug=True)