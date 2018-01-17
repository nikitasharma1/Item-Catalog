#!/usr/bin/env python3

# Imports from Flask
from flask import Flask
from flask import request, render_template, redirect, url_for
from flask import jsonify, flash
from flask import session as login_session
from flask import make_response

# Imports from "database_setup.py"
from database_setup import Base, Category, Item, User

# Imports from SQLAlchemy toolkit
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import from The Python Standard Library
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

# Import from "helper_functions.py"
from helper_functions import *

# Connect to database,
# Create session
#engine = create_engine("sqlite:///item_catelog.db")
engine = create_engine("postgresql://catalog:catalogpass@localhost/catalog")
# Bind schema constructs(mapper code) to engine
Base.metadata.bind = engine
# Create a configured Session class
DBSession = sessionmaker(bind=engine)
# Create a session
session = DBSession()


# Create Flask instance
app = Flask(__name__)

# Store client id in a variable
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catelog"


# Route to login page "http://localhost:5000/login/"
@app.route("/login")
def show_login():
    """Renders the login page to users
    not already logged in.
    Creates state token and stores it in the session"""

    # If login session contains the attribute "username",
    # i.e. if user is already logged in,
    if "username" in login_session:
        # Redirect to index page
        return redirect(url_for("index"))

    # Get categories
    categories = getCategoryAll(session)
    # Create anti forgery state token
    state = AFStateToken()
    # Store anti forgery state token in session
    login_session["state"] = state
    # Render template
    return render_template("login.html",
                           STATE=state,
                           categories=categories)


# Redirect URI post GOOGLE PLUS authorization
@app.route("/gconnect", methods=["POST"])
def gconnect():
    """Authentication and authorization:
    1. Validate state token
    2. Obtain authorization code
    3. Exchange authorization code with access credentials from provider
    4. Check if access token is valid.
    5. Check if access token is for correct user,
    and for correct client(app)
    6. Check if user is already connected,
    otherwise store the user and access credentials in login session
    7. Check if user already exists,
    otherwise create new user"""

    # Validate state token
    if request.args.get("state") != login_session["state"]:
        response = make_response(
            json.dumps("Invalid state parameter."), 401)
        response.headers["Content-Type"] = "application/json"
        return response

    # Obtain the authorization code
    auth_code = request.data

    try:
        # Upgrade authorization code into credentials object
        # 1. Create flow object
        # 2. Exchange authorization code with credentials object
        # The credentials object contains the access token
        oauth_flow = flow_from_clientsecrets("client_secrets.json", scope="")
        oauth_flow.redirect_uri = "postmessage"
        credentials = oauth_flow.step2_exchange(auth_code)
    except FlowExchangeError:
        response = make_response(
            json.dumps("Failed to upgrade the authorization code."), 401)
        response.headers["Content-Type"] = "application/json"
        return response

    # Check that access token is valid
    access_token = credentials.access_token
    url = ("https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s"
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1].decode())
    # If there was an error in access token info, abort
    if result.get("error") is not None:
        response = make_response(
            json.dumps(result.get("error")), 500)
        response.headers["Content-Type"] = "application/json"
        return response

    # Verify that the access token is for intended user
    gplus_id = credentials.id_token["sub"]
    if result["user_id"] != gplus_id:
        response = make_response(
            json.dumps(
                "Token's user id doesn't match the given user id."), 401)
        response.headers["Content-Type"] = "application/json"
        return response

    # Verify that the access token is valid for this app
    if result["issued_to"] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client id doesn't match the app's client id."))
        response.headers["Content-Type"] = "application/json"
        return response

    # Check if the user is already connected
    stored_access_token = login_session.get("access_token")
    stored_gplus_id = login_session.get("gplus_id")

    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps("Current user is already connected."), 200)
        response.headers["Content-Type"] = "application/json"
        return response

    # Store the access token and user id in session for later use
    login_session["access_token"] = credentials.access_token
    login_session["gplus_id"] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {"access_token": credentials.access_token, "alt": "json"}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    # Store user info in login session
    login_session["username"] = data["name"]
    login_session["picture"] = data["picture"]
    login_session["email"] = data["email"]

    # Check if user exists
    user_id = getUserId(login_session["email"], session)
    if not user_id:
        user_id = createUser(login_session, session)

    # Store user id to login session
    login_session["user_id"] = user_id

    output = ""
    output += "<h3> Welcome, " + login_session["username"]
    output += "!</h3>"
    output += "<img src='" + login_session["picture"] + "'"
    output += "style='width: 100px; height: 100px;border-radius: 150px;"
    output += "-webkit-border-radius: 150px;-moz-border-radius: 150px;'><br>"

    flash("You are now logged in as %s" % login_session["username"])
    print("Done!")
    return output


# Route to GOOGLE PLUS logout
@app.route("/gdisconnect")
def gdisconnect():
    """Revoke the current user's token and reset their login session"""

    access_token = login_session["access_token"]

    # Check if access token exists
    if access_token is None:
        print("Access token is None")
        response = make_response(
            json.dumps("Current user is not connected."), 401)
        response.headers["Content-Type"] = "application/json"
        return response

    # If access token exists, check that it is valid and can be revoked
    url = ("https://accounts.google.com/o/oauth2/revoke?token=%s"
           % login_session['access_token'])

    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    # If access token is valid and can be revoked,
    if result["status"] == "200":
        # Delete user info and access credentials from login session
        del login_session["access_token"]
        del login_session["gplus_id"]
        del login_session["username"]
        del login_session["email"]
        del login_session["picture"]
        del login_session["user_id"]

        response = make_response(
            json.dumps("Successfully Disconnected!"), 200)
        response.headers["Content-Type"] = "application/json"

        # Redirect to index page
        return redirect(url_for("index"))
    else:
        response = make_response(
            json.dumps("Failed to revoke token for given user."), 400)
        response.headers["Content-Type"] = "application/json"
        return response


@app.route("/logout")
def logout():
    """Performs redirect to corresponding logout routes"""

    # If user is logged in with GOOGLE PLUS,
    if "gplus_id" in login_session:
        # Redirect to revoke GOOGLE PLUS access credentials
        return redirect(url_for("gdisconnect"))


@app.route("/", methods=["GET"])
def index():
    """Displays the list of all categories and all items"""

    # Set login status
    logged_in = False
    if "username" in login_session:
        logged_in = True

    # Get all items and categories
    categories = getCategoryAll(session)
    items = getItemAll(session)

    # Render index page
    return render_template("index.html",
                           categories=categories,
                           items=items,
                           logged_in=logged_in)


@app.route("/category/create/", methods=["GET", "POST"])
def create_category():
    """Allows logged in users to create new category"""

    # If user is not logged in,
    if "username" not in login_session:
        # Redirect to login page
        return redirect(url_for("show_login"))

    # Get all categories
    categories = getCategoryAll(session)

    if request.method == "GET":
        # Render page to create new category
        return render_template("category/create_category.html",
                               categories=categories,
                               logged_in=True)
    else:
        # If method is "POST",

        # Get category name from form
        name = request.form["name"]
        # Create category
        CUCategory(session, login_session, name, "Create")
        # Flash message
        flash("Added category " + name)

        # Redirect to index page
        return redirect(url_for("index"))


@app.route("/category/<int:category_id>/update/", methods=["GET", "POST"])
def update_category(category_id):
    """Allows logged in users to update category created by them."""

    # If user is not logged in,
    if "username" not in login_session:
        # Redirect to login page
        return redirect(url_for("show_login"))

    # Get all categories
    categories = getCategoryAll(session)
    # Get category by id
    category = getCategoryOne(session, category_id)

    # Get creator id
    creator_id = category.user_id
    # If user is not the creator, update is unauthorized
    UnauthorizeUD(login_session, creator_id)

    if request.method == "GET":
        # Render page to update category
        return render_template("category/update_category.html",
                               category_id=category_id,
                               category_name=category.name,
                               categories=categories,
                               logged_in=True)
    else:
        # If method is "POST",

        # Save old category name to variable
        old_name = category.name
        # Get new category name from form
        name = request.form["name"]
        # Update category
        CUCategory(session, login_session, name, "Update", category_id)
        # Flash message
        flash("Updated category " + old_name + " to " + name)

        # Redirect to index page
        return redirect(url_for("index"))


@app.route("/category/<int:category_id>/delete/", methods=["GET", "POST"])
def delete_category(category_id):
    """Allows logged in users to delete category created by them."""

    # If user is not logged in,
    if "username" not in login_session:
        # Redirect to login page
        return redirect(url_for("show_login"))

    # Get all categories
    categories = getCategoryAll(session)
    # Get category by id
    category = getCategoryOne(session, category_id)

    # Get creator id
    creator_id = category.user_id
    # If user is not the creator, delete is unauthorized
    UnauthorizeUD(login_session, creator_id)

    if request.method == "GET":
        # Render page to delete category
        return render_template("category/delete_category.html",
                               category_id=category_id,
                               category_name=category.name,
                               categories=categories,
                               logged_in=True)
    else:
        # If method is "POST",

        # Delete category
        deleteObject(session, category)
        # Flash message
        flash("Deleted category " + category.name)

        # Redirect to index page
        return redirect(url_for("index"))


@app.route("/category/<int:category_id>/item/", methods=["GET"])
def read_item_by_category(category_id):
    """Display items for given category"""

    # Set login status
    logged_in = False
    if "username" in login_session:
        logged_in = True

    # Get all categories
    categories = getCategoryAll(session)
    # Get category by id
    category = getCategoryOne(session, category_id)
    # Get items by category
    items = getItemByCategory(session, category_id)
    # Check if user is creator
    user_is_creator = category.user_id == login_session.get("user_id")

    # Return page that displays items by category
    return render_template("item/read_item_by_category.html",
                           items=items,
                           categories=categories,
                           category_name=category.name,
                           category_id=category_id,
                           logged_in=logged_in,
                           user_is_creator=user_is_creator)


@app.route("/category/<int:category_id>/item/<int:item_id>/description/")
def read_item_description(category_id, item_id):
    """Display item description for given item"""

    # Set login status
    logged_in = False
    if "username" in login_session:
        logged_in = True

    # Get all categories from database
    categories = getCategoryAll(session)
    # Get category by id
    category = getCategoryOne(session, category_id)
    # Get item by id
    items = session.query(Item).filter_by(id=item_id)
    item = items.one()

    # Check if user is creator
    user_is_creator = item.user_id == login_session.get("user_id")

    # Return page that displays item description
    return render_template("item/read_item_description.html",
                           items=items,
                           item=item,
                           categories=categories,
                           category_name=category.name,
                           item_name=item.name,
                           category_id=category_id,
                           # item_id=item_id,
                           logged_in=logged_in,
                           user_is_creator=user_is_creator)


@app.route("/category/<int:category_id>/item/create/", methods=["GET", "POST"])
def create_item(category_id):
    """Allows logged in users to create items"""

    # If user is not logged in,
    if "username" not in login_session:
        # Redirect to login page
        return redirect(url_for("show_login"))

    # Get all categories
    categories = getCategoryAll(session)

    if request.method == "GET":
        # Render page to create item
        return render_template("item/create_item.html",
                               category_id=category_id,
                               categories=categories,
                               logged_in=True)
    else:
        # If method is "POST",

        # Get name and description from form
        name = request.form["name"]
        description = request.form["description"]
        # Create item
        CUItem(session, login_session,
               name, description, category_id, "Create")
        # Flash message
        flash("Created item " + name)

        # Redirect to page that displays items by category
        return redirect(url_for("read_item_by_category",
                                category_id=category_id))


@app.route("/category/<int:category_id>/item/<int:item_id>/update/",
           methods=["GET", "POST"])
def update_item(category_id, item_id):
    """Allows logged in users to update item created by them"""

    # If user is not logged in,
    if "username" not in login_session:
        # Redirect to login page
        return redirect(url_for("show_login"))

    # Get all categories
    categories = getCategoryAll(session)
    # Get item by id
    item = getItemOne(session, item_id)

    # Get creator id
    creator_id = item.user_id
    # If user is not creator, update is unauthorized
    UnauthorizeUD(login_session, creator_id)

    if request.method == "GET":
        # Render page to update item
        return render_template("item/update_item.html",
                               category_id=category_id,
                               item_id=item_id,
                               item=item,
                               categories=categories,
                               logged_in=True)
    else:
        # If method is "POST",

        # Store old name in variable
        old_name = item.name
        # Get name and description from form
        name = request.form["name"]
        description = request.form["description"]
        # Update item
        CUItem(session, login_session,
               name, description, category_id, "Update", item_id)
        # Flash message
        flash("Updated item " + old_name)

        # Redirect to page that reads item description
        return redirect(url_for("read_item_description",
                                category_id=category_id,
                                item_id=item_id))


@app.route("/category/<int:category_id>/item/<int:item_id>/delete/",
           methods=["GET", "POST"])
def delete_item(category_id, item_id):
    """Allows logged in users to delete item created by them"""

    # If user is not logged in,
    if "username" not in login_session:
        # Redirect to login page
        return redirect(url_for("show_login"))

    # Get all categories
    categories = getCategoryAll(session)
    # Get item by id
    item = getItemOne(session, item_id)

    # Get creator id
    creator_id = item.user_id
    # If user is not creator, delete is unauthorized
    UnauthorizeUD(login_session, creator_id)

    if request.method == "GET":
        # Render page to delete item
        return render_template("item/delete_item.html",
                               category_id=category_id,
                               item_id=item_id,
                               categories=categories,
                               logged_in=True)
    else:
        # If method is "POST",

        # Delete item
        deleteObject(session, item)
        # Flash message
        flash("Deleted item " + item.name)

        # Redirect page that displays items by category
        return redirect(url_for("read_item_by_category",
                                category_id=category_id))


@app.route("/category/JSON", methods=["GET"])
def categories_json():
    """Returns JSON object with all categories"""

    # Get all categories
    categories = getCategoryAll(session)
    # Return JSON object
    return jsonify(Categories=[c.serialize for c in categories])


@app.route("/category/<int:category_id>/JSON", methods=["GET"])
def category_json(category_id):
    """Returns JSON object of category with given id"""

    # Get category by id
    category = getCategoryOne(session, category_id)
    # Return JSON object
    return jsonify(Category=category.serialize)


@app.route("/item/JSON", methods=["GET"])
def items_JSON():
    """Returns JSON object with all items"""

    # Get all items
    items = getItemAll(session)
    # Return JSON object
    return jsonify(Items=[i.serialize for i in items])


@app.route("/item/<int:item_id>/JSON", methods=["GET"])
@app.route("/category/<int:category_id>/item/<int:item_id>/JSON",
           methods=["GET"])
def item_JSON(item_id, category_id=None):
    """Returns JSON object of item with given id"""

    # Get item by id
    item = getItemOne(session, item_id)
    # Return JSON object
    return jsonify(Item=item.serialize)


@app.route("/category/<int:category_id>/item/JSON", methods=["GET"])
def category_items_json(category_id):
    """Return JSON object of items with given category id"""

    # Get items by category id
    items = getItemByCategory(session, category_id)
    # Return JSON object
    return jsonify(Items=[i.serialize for i in items])


if __name__ == "__main__":
    # key to be changed later to something secure
    app.secret_key = "somekey"
    # To debug, Set to True, otherwise False
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
