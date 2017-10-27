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
import random, string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

# Connect to database,
# Create session
engine = create_engine("sqlite:///item_catelog.db")
# Bind schema constructs(mapper code) to engine
Base.metadata.bind = engine
# Create a configured Session class
DBSession = sessionmaker(bind=engine)
# Create a session
session = DBSession()


# Create Flask instance
app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catelog"


def getUserId(email):
	try:
		user = session.query(User).filter_by(email=email).one()
		return user_id
	except Exception:
		return None

def createUser(login_session):
	user = User(name=login_session["username"],
				email=login_session["email"],
				picture=login_session["picture"])
	session.add(user)
	session.commit()
	return user.id

@app.route("/login")
def show_login():
	if "username" in login_session:
		return redirect(url_for("index"))
	categories = session.query(Category)
	state = ''.join(random.choice(string.ascii_uppercase + string.digits)
			for x in range(32))
	login_session['state'] = state
	# return "The current session state is %s" % login_session['state']
	return render_template("login.html",
						   STATE=state,
						   categories=categories)


@app.route("/gconnect", methods=["POST"])
def gconnect():
	# Validate state token
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state parameter.'), 401)
		response.headers['Content-Type'] = "application/json"
		return response

	# Obtain the authorization code
	auth_code = request.data

	try:
		# Upgrade authorization code into credentials object
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
	url = ("https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s"  % access_token)
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
			json.dumps("Token's user id doesn't match the given user id."), 401)
		response.headers["Content-Type"] = "application/json"
		return response

	# Verify that the access token is valid for this app
	if result["issued_to"] != CLIENT_ID:
		response = make_response(
			json.dumps("Token's client id doesn't match the app's client id."))
		response.headers["Content-Type"] = "application/json"
		return response

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

	login_session["username"] = data["name"]
	login_session["picture"] = data["picture"]
	login_session["email"] = data["email"]

	# Check if user exists
	user_id = getUserId(login_session["email"])
	if not user_id:
		user_id = createUser(login_session)

	login_session["user_id"] = user_id

	output = ""
	output += "<h3> Welcome, " + login_session["username"]
	output += "!</h3>"
	output += "<img src='" + login_session["picture"] + "'"
	output += "style='width: 100px; height: 100px;border-radius: 150px;"
	output += "-webkit-border-radius: 150px;-moz-border-radius: 150px;'"

	flash("You are now logged in as %s" % login_session["username"])
	print("Done!")
	return output

# Disconnect: Revoke the current user's token and reset their login session
@app.route("/gdisconnect")
def gdisconnect():
	access_token = login_session["access_token"]
	if access_token is None:
		print("Access token is None")
		response = make_response(
			json.dumps("Current user is not connected."), 401)
		response.headers["Content-Type"] = "application/json"
		return response

	url = ("https://accounts.google.com/o/oauth2/revoke?token=%s" % login_session['access_token'])

	h = httplib2.Http()
	result = h.request(url, 'GET')[0]

	if result["status"] == "200":
		del login_session["access_token"]
		del login_session["gplus_id"]
		del login_session["username"]
		del login_session["email"]
		del login_session["picture"]
		del login_session["user_id"]

		response =  make_response(
			json.dumps("Successfully Disconnected!"), 200)
		response.headers["Content-Type"] = "application/json"
		return redirect(url_for("index"))
	else:
		response = make_response(
			json.dumps("Failed to revoke token for given user."), 400)
		response.headers["Content-Type"] = "application/json"
		return response


@app.route("/logout")
def logout():
	if "gplus_id" in login_session:
		return redirect(url_for("gdisconnect"))


@app.route("/", methods=["GET"])
def index():
	logged_in = False
	if "username" in login_session:
		logged_in = True

	categories = session.query(Category)
	items = session.query(Item)
	return render_template("index.html",
						   categories=categories,
						   items=items,
						   logged_in=logged_in)


@app.route("/category/create/", methods=["GET", "POST"])
def create_category():
	if "username" not in login_session:
		return redirect(url_for("show_login"))

	categories = session.query(Category)
	if request.method == "GET":
		return render_template("category/create_category.html",
							   categories=categories,
							   logged_in=True)
	else:
		category = Category(name=request.form["name"],
							user_id=login_session["user_id"])
		session.add(category)
		session.commit()
		flash("Added category "+ category.name)
		return redirect(url_for("index"))


@app.route("/category/<int:category_id>/update/", methods=["GET", "POST"])
def update_category(category_id):
	if "username" not in login_session:
		return redirect(url_for("show_login"))

	categories = session.query(Category)
	category = session.query(Category).filter_by(id=category_id).one()

	if category.user_id != login_session["user_id"]:
		response = make_response(
			json.dumps("Unauthorized"), 401)
		response.headers["Content-Type"] = "application/json"
		return response

	if request.method == "GET":
		return render_template("category/update_category.html",
							   category_id=category_id,
							   category_name=category.name,
							   categories=categories,
							   logged_in=True)
	else:
		old_name = category.name
		category.name = request.form["name"]
		session.add(category)
		session.commit()
		flash("Updated category " + old_name + " to " + category.name)
		return redirect(url_for("index"))


@app.route("/category/<int:category_id>/delete/", methods=["GET", "POST"])
def delete_category(category_id):
	if "username" not in login_session:
		return redirect(url_for("show_login"))

	categories = session.query(Category)
	category = session.query(Category).filter_by(id=category_id).one()

	if category.user_id != login_session["user_id"]:
		response = make_response(
			json.dumps("Unauthorized"), 401)
		response.headers["Content-Type"] = "application/json"
		return response

	if request.method == "GET":
		return render_template("category/delete_category.html",
							   category_id=category_id,
							   category_name=category.name,
							   categories=categories,
							   logged_in=True)
	else:
		session.delete(category)
		session.commit()
		flash("Deleted category " + category.name)
		return redirect(url_for("index"))


@app.route("/category/<int:category_id>/item/", methods=["GET"])
def read_item_by_category(category_id):
	logged_in = False
	if "username" in login_session:
		logged_in = True
	categories = session.query(Category)
	category = categories.filter_by(id=category_id).one()
	items = session.query(Item).filter_by(category_id=category_id)

	user_is_creator = category.user_id == login_session["user_id"]

	return render_template("item/read_item_by_category.html",
						   items=items,
						   categories=categories,
						   category_name=category.name,
						   category_id=category_id,
						   logged_in=logged_in,
						   user_is_creator=user_is_creator)


@app.route("/category/<int:category_id>/item/<int:item_id>/description/")
def read_item_description(category_id, item_id):
	logged_in = False
	if "username" in login_session:
		logged_in = True
	categories = session.query(Category)
	category = categories.filter_by(id=category_id).one()
	items = session.query(Item).filter_by(id=item_id)
	item = items.one()

	user_is_creator = item.user_id == login_session["user_id"]

	return render_template("item/read_item_description.html",
						   items = items,
						   item = item,
						   categories=categories,
						   category_name=category.name,
						   item_name=item.name,
						   category_id=category_id,
						   item_id=item_id,
						   logged_in=logged_in,
						   user_is_creator=user_is_creator)

@app.route("/category/<int:category_id>/item/create/", methods=["GET", "POST"])
def create_item(category_id):
	if "username" not in login_session:
		return redirect(url_for("show_login"))

	categories = session.query(Category)
	if request.method == "GET":
		return render_template("item/create_item.html",
							   category_id=category_id,
							   categories=categories,
							   logged_in=True)
	else:
		item = Item(name=request.form["name"],
					description=request.form["description"],
					category_id=category_id,
					user_id=login_session["user_id"])
		session.add(item)
		session.commit()
		flash("Created item " + item.name)
		return redirect(url_for("read_item_by_category",
								category_id=category_id))


@app.route("/category/<int:category_id>/item/<int:item_id>/update/", methods=["GET", "POST"])
def update_item(category_id, item_id):
	if "username" not in login_session:
		return redirect(url_for("show_login"))

	categories = session.query(Category)
	item = session.query(Item).filter_by(id=item_id).one()

	if item.user_id != login_session["user_id"]:
		response = make_response(
			json.dumps("Unauthorized"), 401)
		response.headers["Content-Type"] = "application/json"
		return response

	if request.method == "GET":
		return render_template("item/update_item.html",
							   category_id=category_id,
							   item_id=item_id,
							   item=item,
							   categories=categories,
							   logged_in=True)
	else:
		old_name = item.name
		item.name = request.form["name"]
		item.description = request.form["description"]
		session.add(item)
		session.commit()
		flash("Updated item " + old_name)
		return redirect(url_for("read_item_description",
								category_id=category_id,
								item_id=item_id))


@app.route("/category/<int:category_id>/item/<int:item_id>/delete/", methods=["GET", "POST"])
def delete_item(category_id, item_id):
	if "username" not in login_session:
		return redirect(url_for("show_login"))

	categories = session.query(Category)
	item = session.query(Item).filter_by(id=item_id).one()

	if item.user_id != login_session["user_id"]:
		response = make_response(
			json.dumps("Unauthorized"), 401)
		response.headers["Content-Type"] = "application/json"
		return response

	if request.method == "GET":
		return render_template("item/delete_item.html",
							   category_id=category_id,
							   item_id=item_id,
							   categories=categories,
							   logged_in=True)
	else:
		session.delete(item)
		session.commit()
		flash("Deleted item " + item.name)
		return redirect(url_for("read_item_by_category",
								category_id=category_id))


@app.route("/category/JSON", methods=["GET"])
def categories_json():
	categories = session.query(Category).all()
	return jsonify(Categories=[c.serialize for c in categories])


@app.route("/category/<int:category_id>/JSON", methods=["GET"])
def category_json(category_id):
	category = session.query(Category).filter_by(id=category_id).one()
	return jsonify(Category=category.serialize)


@app.route("/item/JSON", methods=["GET"])
def items_JSON():
	items = session.query(Item).all()
	return jsonify(Items=[i.serialize for i in items])


@app.route("/item/<int:item_id>/JSON", methods=["GET"])
@app.route("/category/<int:category_id>/item/<int:item_id>/JSON", methods=["GET"])
def item_JSON(item_id, category_id=None):
	item = session.query(Item).filter_by(id=item_id).one()
	return jsonify(Item=item.serialize)


@app.route("/category/<int:category_id>/item/JSON", methods=["GET"])
def category_items_json(category_id):
	items = session.query(Item).filter_by(category_id=category_id).all()
	return jsonify(Items=[i.serialize for i in items])


if __name__ == "__main__":
	# key to be changed later to something secure
	app.secret_key = "somekey"
	# To debug, Set to True, otherwise False
	app.debug = True
	app.run(host="0.0.0.0", port=5000)