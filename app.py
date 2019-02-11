import os
import json
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from bson.json_util import loads, dumps
from byotests import *

try:
    import env
    development = True
except:
    development = False

app = Flask(__name__)
app.secret_key = 'we-will-succeed-123'

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")

mongo = PyMongo(app)

# Global Variables -------------------------------------------------------------

cusine_list = ['American', 'British', 'Caribbean', 'Chinese', 'French', 'Greek', 'Indian', 'Italian', 'Japanese', 'Mediterranean', 'Mexican', 'Moroccan', 'Spanish', 'Thai', 'Turkish', 'Vietnamese', 'Other']


# User functions ---------------------------------------------------------------

def user_has_logged_in(email):
    
    """ 
    Upon valid log in, adds users email address to the session dict and also 
    extracts the users unique bson id to keep in the session too
    """
    
    session['user'] = email
    this_user = mongo.db.Users.find_one({"email":session["user"]})
    this_user_id_bson = this_user["_id"]
    this_user_id_str = dumps(this_user_id_bson)
    extract_id_1 = this_user_id_str.replace('{"$oid": "', "")
    extract_id_2 = extract_id_1.replace('"}', "")
    session['user_id'] = extract_id_2
    
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
        if email_given.lower() == user["email"].lower() and password_given == user["password"]:
            user_has_logged_in(email_given)
            log_on_validation_status.append("username & password match")
            break
        elif email_given.lower() == user["email"].lower() and password_given != user["password"]:
            log_on_validation_status.append("username found, password incorrect")
            break
        
    if log_on_validation_status == []:
        flash("I'm sorry, email address {} does not appear to have been registered.  Please sign up now or try again!".format(email_given))
    elif log_on_validation_status[0] == "username & password match":
        return True
    elif log_on_validation_status[0] == "username found, password incorrect":
        flash("I'm sorry, the password you entered does not match with our records.  Please feel free to try again!")

def does_record_already_exist(search_criteria, database_records):
    
    """
    Checks to see if a record already exists in a database {e.g. users / ingredients
    and returns True if so
    """
    
    existing_record = 0
    for item in database_records:
        if request.form[search_criteria].lower() == item[search_criteria].lower():
            existing_record += 1
    
    if existing_record != 0:
        return True


#  Database helper functions ---------------------------------------------------

# Search database functions ----------------------------------------------------

def recipe_already_exists(new_recipe_name):
    
    """
    Checks to see if a recipe already exists taking into account object id
    and returns True if so
    """
    
    current_user = determine_current_user(session)
    if current_user == "guest":
        print("Not logged in")
    else:
        this_user = mongo.db.Users.find_one({"email":current_user})
        recipes = mongo.db.recipes.find()
        
        for recipe in recipes:
            if ObjectId(recipe["author"]) == this_user["_id"] and recipe["recipe_name"] == new_recipe_name:
                return True


# Recipe Review Functions ------------------------------------------------------

def review_is_present(review_db, user):
    
    """
    Checks if the current user has already reviewed the recipe being looked at
    """
    
    try:
        for review in review_db:
            if review["reviewing_user"] == user:
                return "Yes"
        return "No"
    except:
        return "No"

def website_recipe_data(recipesDB):
    
    """
    Should review the recipes in the database and pull together stats to show
    how many are on the site, which cusines they relate to and how many
    authors there are compared to recipes
    """
    
    recipe_data = []
    authors_data = []
    recipe_count = 0
    
    for recipe in recipesDB:
        recipe_count += 1
        for key, value in recipe.items():
            
            if key == "cusine":
                key_type = value
                
                if recipe_data == []:
                        recipe_data.append({ key_type : 1 })
                else:
                    for entry in recipe_data:
                        if next(iter(entry)) == key_type:
                            existing = "Yes"
                            break
                        else:
                            existing = "No"
                            
                    if existing == "No":
                        recipe_data.append({ key_type : 1 })
                    else:
                        entry[key_type] += 1
                        
            elif key == "author_email":
                key_type = value
                
                if authors_data == []:
                    authors_data.append(recipe["author_email"])
                else:
                    for entry in authors_data:
                        if entry == key_type:
                            existing = "Yes"
                            break
                        else:
                            existing = "No"
                            
                    if existing == "No":
                        authors_data.append(recipe["author_email"])
    
    recipe_data.append({ "Total Recipes" : recipe_count })
    recipe_data.append({"Number of Authors" : len(authors_data) })
    
    return recipe_data

# FUNCTION TESTS ------------------------------------------------------------------------------

"""
The following test will check to ensure the correct data is being pulled for the
via the website_recdipe_data_function
"""

test_recipe_data = [
            {"cusine" : "American", "author_email" : "first_author", "random_field" : "random_data"},
            {"cusine" : "Japanese", "author_email" : "first_author", "random_field" : "random_data"},
            {"cusine" : "American", "author_email" : "second_author", "random_field" : "random_data"},
            {"cusine" : "American", "author_email" : "third_author", "random_field" : "random_data"},
            {"cusine" : "Italian", "author_email" : "first_author", "random_field" : "random_data"},
            ]

test_are_equal(website_recipe_data(test_recipe_data), [{"American" : 3}, {"Japanese" : 1}, {"Italian" : 1}, {"Total Recipes" : 5}, {"Number of Authors": 3}])

print("All tests have passed")
    
# Views ------------------------------------------------------------------------

@app.before_request
def before_request():
    protected_route = ['profile']
    if request.endpoint in protected_route and 'user' not in session:
        return redirect(url_for('log_in'))

@app.route('/')
def index():
    current_user = determine_current_user(session)
    recipes = mongo.db.recipes.find()
    
    site_stats = website_recipe_data(recipes)
    
    return render_template("index.html", users = mongo.db.Users.find(), username=current_user, page_title="Home", stats=site_stats)

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
        if request.form["password"] == request.form["password2"]:
            mongo.db.Users.insert_one(request.form.to_dict())
            user_has_logged_in(request.form['email'])
            flash("Hi {}, thanks for registering.\n  You may now add your own recipes and receive or write reviews!\n Good luck!".format(request.form['email']))
            return redirect(url_for('index'))
        else:
            flash("I'm sorry, yoyr passwords did not match, please try again")
            return redirect(url_for('sign_up'))

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
    session.pop('sort_param', None)
    session.pop('filter_value', None)
    session.pop('filter_field', None)
    session.pop('limit', None)
    current_user = determine_current_user(session)
    flash("You have logged out. Come back now you hear!")
    return redirect(url_for('index'))
    
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
    return render_template('edit_ingredient.html', ingredient=the_ingredient, username=current_user, page_title="Edit Ingredient")

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
    
    recipe_db = mongo.db.recipes
    
    try:
        user = mongo.db.Users.find_one({"email": session["user"]})
        user_id = session["user_id"]
    except:
        user = "guest"
        user_id = "guest"
    
    """
    This code should apply any sort parameters, filters and pagination to the
    recipes on recpes.html.  It takes the sort parameter, a filter field, a 
    filter id and a limit value to determine what the user wants to see on the page.It
    
    The filter field and value will determine which recipes are applied to be
    part of the users custom search and can be filtered my their own recipes, all
    recipes, or based on the cusine type.All
    
    The sort parameter will determine whether that data is then sorted by latest, 
    Highest rated or alphabetically.Highest
    
    Finally, the limit value will determine how many recipes are displayed on the
    page at once (3, 6 or 9) and the offset value will determnie where the user is 
    in the list of recipes within that limit as the user flicks through the pages.
    
    """
    
    starting_sort_param = '_id'
    starting_filter_field = "_id"
    starting_filter_value = "All"
    starting_limit = 9
    
    try:    
        new_filter_field = str(request.args["filter_field"])
        new_filter_value = str(request.args["filter_value"])
    except:
        new_filter_field = "None"
    
    try:
        existing_filter_field = session['filter_field']
        existing_filter_value = session['filter_value']
    except:
        existing_filter_field = "None"

    if new_filter_field != "None":
        session['filter_field'] = new_filter_field
        session['filter_value'] = new_filter_value
        filter_field = session['filter_field']
        filter_value = session['filter_value']
    elif existing_filter_field != "None":
        filter_field = existing_filter_field
        filter_value = existing_filter_value
    else:
        filter_field = starting_filter_field
        filter_value = starting_filter_value
    
    try:    
        new_limit = int(request.args["limit"])
    except:
        new_limit = "None"
    
    try:
        existing_limit = session['limit']
    except:
        existing_limit = "None"

    if new_limit != "None":
        session['limit'] = new_limit
        limit = session['limit']
    elif existing_limit != "None":
        limit = existing_limit
    else:
        limit = starting_limit
    
    try:
        new_offset = int(request.args["offset"])
    except:
        new_offset = 0
    
    if new_offset < 0:
        offset = 0
    elif new_offset >= recipe_db.find().count():
        if recipe_db.find().count() - limit < 0:
            offset = 0
        else:
            offset = recipe_db.find().count() - limit;
    else:
        offset = new_offset
    
    try:    
        new_sort = str(request.args["sort_param"])
    except:
        new_sort = "None"
    
    try:
        existing_sort = session['sort_param']
    except:
        existing_sort = "None"

    if new_sort != "None":
        session['sort_param'] = new_sort
        sort_param = session['sort_param']
    elif existing_sort != "None":
        sort_param = existing_sort
    else:
        sort_param = starting_sort_param
        
    if sort_param == "_id":
        sort_order = -1
    elif sort_param == "user_score":
        sort_order = 1
        sort_param = "user_score"
    else:
        sort_order = 1

    # Execute if no filters applied....

    if filter_field == "_id":
        
        # Sort by latest ................
        
        if sort_param == "_id":
            first_id_in_db = recipe_db.find().sort([(sort_param, sort_order)])
            id_to_start_from = first_id_in_db[offset]['_id']
    
            recipes = mongo.db.recipes.find({'_id' :{'$lte' : id_to_start_from}}).limit(limit).sort([(sort_param, sort_order)])
        
        # Sort by user score ................
        
        elif sort_param == "user_score":
            aggrDB = recipe_db.aggregate([ { '$project' : { "_id" : 1 , 
                "user_score" : 1, "cusine" : 1, "recipe_image_url" : 1, "author" : 1,
                "recipe_name" : 1, "average_score" : { '$avg' : { '$ifNull' : ["$user_score", 0 ]} }}}, 
                { '$sort' : { "average_score" : -1 }}, { '$skip' : offset },
                { '$limit': limit }])
    
            recipes = aggrDB
        
            
        # Sort by recipe_name ..............
        
        else:
            first_id_in_db = recipe_db.find().sort([(sort_param, sort_order)])
            id_to_start_from = first_id_in_db[offset][sort_param]
    
            recipes = mongo.db.recipes.find({sort_param :{'$gte' : id_to_start_from}}).limit(limit).sort([(sort_param, sort_order)])
     
    
    # If filters applied...        
            
    else:
        
        try:
            # Sort by latest ................
        
            if sort_param == "_id":
                first_id_in_db = recipe_db.find({filter_field : filter_value}).sort([(sort_param, sort_order)])
                id_to_start_from = first_id_in_db[offset]['_id']
    
                recipes = mongo.db.recipes.find({filter_field : filter_value, '_id' :{'$lte' : id_to_start_from}}).limit(limit).sort([(sort_param, sort_order)])
            
            # Sort by user score ................
            
            elif sort_param == "user_score":
                aggrDB = recipe_db.aggregate([ { '$project' : { "_id" : 1 , 
                    "user_score" : 1, "cusine" : 1, "recipe_image_url" : 1, "author" : 1,
                    "recipe_name" : 1, "average_score" : { '$avg' : { '$ifNull' : ["$user_score", 0 ]} }}}, 
                    { '$sort' : { "average_score" : -1 }}, { '$match' : { filter_field : filter_value }}, { '$skip' : offset },
                    { '$limit': limit }])
        
                recipes = aggrDB
            
            # Sort by recipe_name ..............
        
            else:
                first_id_in_db = recipe_db.find({filter_field : filter_value}).sort([(sort_param, sort_order)])
                id_to_start_from = first_id_in_db[offset][sort_param]
    
                recipes = mongo.db.recipes.find({filter_field : filter_value, sort_param :{'$gte' : id_to_start_from}}).limit(limit).sort([(sort_param, sort_order)])
        except:
            recipes = []
    
    return render_template("recipes.html", recipes_list = recipes, page_title="Recipes", username=current_user, user=user, 
        user_id = user_id, limit = limit, offset = offset, cusines = cusine_list, filter_field = filter_field, 
        filter_value = filter_value, sort_param = sort_param)

@app.route('/add_recipe')
def add_recipe():
    current_user = determine_current_user(session)
    
    if current_user == "guest":
        flash("I'm sorry but you need to be logged in to add a recipe.  Log in or sign up and begin!")
        return redirect(url_for('recipes'))
    else:
        user = mongo.db.Users.find_one({"email": session["user"]})
        return render_template("add_recipe.html", page_title="Add a Recipe", username=current_user, cusines=cusine_list, user=user)

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

@app.route('/view_recipe/<recipe_id>', methods=["GET", "POST"])
def view_recipe(recipe_id):
    current_user = determine_current_user(session)
    the_recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    author = mongo.db.Users.find_one({"_id": ObjectId(the_recipe["author"])})
    
    """
    Filters the recipe_comments database to create a database of comments that
    relates only to the viewed recipe and then determines if the existing users 
    has already posted a review...
    """
    
    if mongo.db.recipe_comments.find({"reviewed_recipe_id": recipe_id}).count() == 0:
        the_reviews = "None"
    else:
        the_reviews = mongo.db.recipe_comments.find({"reviewed_recipe_id": recipe_id}).sort([("_id", -1)])

    already_reviewed = review_is_present(the_reviews, current_user)
    
    return render_template("view_recipe.html", page_title="View Recipe", 
        cusines=cusine_list, this_recipe=the_recipe, username=current_user, 
        author=author, already_reviewed = already_reviewed)

@app.route('/update_recipe/<section>/<recipe_id>', methods=["POST"])
def update_recipe(section, recipe_id):
    
    this_recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    
    # This code will update the recipe details if it already has ingredients contained within the recipe on the database...
    if section == "1":
        mongo.db.recipes.update(
            {"_id": ObjectId(recipe_id)},
            { "$set":
                {
                    'recipe_name': request.form['recipe_name'],
                    'recipe_image_url': request.form['recipe_image_url'],
                    'cusine': request.form['cusine']
                }
            }
        )
    
    # If an ingredient has been added to the form for inclusion, this code will append it to the list...
    
    elif section == "2":        
        instruction_exists = False
        
        if request.form["instruction"] != "" and request.form["step"] != "":
            try:
                for instruction in this_recipe["recipe_instructions"]:
                    if request.form["step"] == instruction["step"]:
                        instruction_exists = True
                        break
                if instruction_exists == True:
                    print("Not added")
                else:
                    mongo.db.recipes.update(
                        {"_id": ObjectId(recipe_id)},
                        { "$push" : { "recipe_instructions": {"step" : request.form["step"], "instruction" : request.form["instruction"]}}}
                    )
            except:
                mongo.db.recipes.update(
                        {"_id": ObjectId(recipe_id)},
                        { "$push" : { "recipe_instructions": {"step" : request.form["step"], "instruction" : request.form["instruction"]}}}
                    )
    
    # If an ingredient has been added to the form for inclusion, this code will append it to the list...
    elif section == "3":
        ingredient_exists = False
    
        if request.form["ingredient_name"] != "":
            try:
                for ingredient in this_recipe["recipe_ingredients"]:
                    for key, value in ingredient.iteritems():
                        if request.form["ingredient_name"] == key:
                            ingredient_exists = True
                            break
                if ingredient_exists == False:
                    mongo.db.recipes.update(
                        {"_id": ObjectId(recipe_id)},
                        { "$push" : { "recipe_ingredients": {request.form["ingredient_name"] : request.form["ingredient_quantity"]}}}
                    )

            except:
                mongo.db.recipes.update(
                    {"_id": ObjectId(recipe_id)},
                    { "$push" : { "recipe_ingredients": {request.form["ingredient_name"] : request.form["ingredient_quantity"]}}}
                )
        
    return json.dumps({'status':'OK'});

@app.route('/delete_recipe/<recipe_id>', methods=["POST"])
def delete_recipe(recipe_id):
    mongo.db.recipes.remove({"_id": ObjectId(recipe_id)})
    return redirect(url_for('recipes'))

@app.route('/delete_ingredient_from_recipe/<recipe_id>/<ingredient_id>', methods=["POST"])
def delete_ingredient_from_recipe(recipe_id, ingredient_id):
    
    this_recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    
    for ingredient in this_recipe["recipe_ingredients"]:
        ingredientKey = ingredient.keys()
        for key in ingredientKey:
            stringIngKey = key.replace(" ", "")
            if stringIngKey == ingredient_id:
                mongo.db.recipes.update(
                {'_id': ObjectId(recipe_id)}, 
                { "$pull": { "recipe_ingredients" : ingredient }},
                False, True);
                return json.dumps({'status':'OK'});
    
@app.route('/delete_instruction_from_recipe/<recipe_id>/<step>', methods=["POST"])
def delete_instruction_from_recipe(recipe_id, step):
    
    this_recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    
    for instruction in this_recipe["recipe_instructions"]:
        if step == instruction["step"]:
            mongo.db.recipes.update(
            {'_id': ObjectId(recipe_id)}, 
            { "$pull": {"recipe_instructions" : instruction}},
            False, True);
            return json.dumps({'status':'OK'});

@app.route('/add_review_to_recipe/<recipe_id>/<reviewing_user>', methods=["POST"])
def add_review(recipe_id, reviewing_user):
    
    mongo.db.recipe_comments.insert_one({
        "reviewed_recipe_id": recipe_id,
        "reviewing_user": reviewing_user,
        "review_comments" : request.form["review-comments"],
        "review_score" : request.form["review-score"]
        })
    
    mongo.db.recipes.update(
        {"_id": ObjectId(recipe_id)},
            { "$push" : { "user_score": int(request.form["review-score"])}
        })
    
    return redirect(url_for('view_recipe', recipe_id=recipe_id))

@app.route('/head_chefs')
def head_chefs():
    current_user = determine_current_user(session)
    recipe_db = mongo.db.recipes
    
    """
    Creates a database of the top ten users based on the average review score of
    all of the recipes that each user have added to the site.
    """
    
    aggrDB = recipe_db.aggregate([ {
        '$unwind' : '$author_email'
        },
        { '$lookup' : {
        'from' : "Users",
        'localField' : "author_email",
        'foreignField': "email",
        'as' : "author_details"}},
        { '$project' : { "_id" : 1 ,
        "user_score" : 1, "author" : 1,  
        "recipe_name" : 1, "email" : "$author_email", "average_score" : { '$avg' : "$user_score" }}},
        { '$group' : { "_id" : "$author" , "author" : { '$first' : "$author"}, 
        "score" : { '$avg' : '$average_score' }, "email" : { '$first' : { "$split" : ["$email", "@"] }}, "recipes_count" : { '$sum' : 1 }}},
        { '$sort' : { "score" : -1 }},
        { '$limit': 10 }
        ])
    
    return render_template("head_chefs.html", page_title="Head Chefs", username=current_user, table = aggrDB)

@app.route('/js_tests')
def js_tests():
    return render_template("jasmine.html", page_title="JS Testing")
    
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
    port=int(os.environ.get('PORT')),
    debug=development)