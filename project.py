#!/usr/bin/env python3

# Imports from Flask
from flask import Flask
from flask import request, render_template, redirect, url_for

# Imports from "database_setup.py"
from database_setup import Base, Category, Item

# Imports from SQLAlchemy toolkit
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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

@app.route("/login")
def show_login():
	return render_template("login.html")


@app.route("/", methods=["GET"])
def index():
	categories = session.query(Category).all()
	items = session.query(Item).all()
	return render_template("index.html",
						   categories=categories,
						   items=items)


@app.route("/category/create/", methods=["GET", "POST"])
def create_category():
	if request.method == "GET":
		return render_template("category/create_category.html")
	else:
		return "Post request to create category"


@app.route("/category/<int:category_id>/update/", methods=["GET", "POST"])
def update_category(category_id):
	if request.method == "GET":
		return render_template("category/update_category.html", category_id=category_id)
	else:
		return "Post request to update category"


@app.route("/category/<int:category_id>/delete/", methods=["GET", "POST"])
def delete_category(category_id):
	if request.method == "GET":
		return render_template("category/delete_category.html", category_id=category_id)
	else:
		return "Post request to delete category"


@app.route("/category/<int:category_id>/item/", methods=["GET"])
def read_item_by_category(category_id):
	categories = session.query(Category)
	category = categories.filter_by(id=category_id).one()
	items = session.query(Item).filter_by(category_id=category_id)
	return render_template("item/read_item_by_category.html",
						   items=items,
						   categories=categories,
						   category_name=category.name)


@app.route("/category/<int:category_id>/item/<int:item_id>/description/")
def read_item_description(category_id, item_id):
	categories = session.query(Category)
	category = categories.filter_by(id=category_id).one()
	items = session.query(Item).filter_by(id=item_id)
	item = items.one()
	return render_template("item/read_item_description.html",
						   items = items,
						   item = item,
						   categories=categories,
						   category_name=category.name)

@app.route("/category/<int:category_id>/item/create/", methods=["GET", "POST"])
def create_item(category_id):
	if request.method == "GET":
		return render_template("item/create_item.html")
	else:
		return "Post request to create item"


@app.route("/category/<int:category_id>/item/<int:item_id>/update/", methods=["GET", "POST"])
def update_item(category_id, item_id):
	if request.method == "GET":
		return render_template("item/update_item.html", category_id=category_id, item_id=item_id)
	else:
		return "Post request to update item"


@app.route("/category/<int:category_id>/item/<int:item_id>/delete/", methods=["GET", "POST"])
def delete_item(category_id, item_id):
	if request.method == "GET":
		return render_template("item/delete_item.html", category_id=category_id, item_id=item_id)
	else:
		return "Post request to update item"


@app.route("/category/JSON")
def categories_json():
	return "categories json"


@app.route("/category/<int:category_id>/JSON")
def category_json(category_id):
	return "category json"


@app.route("/item/JSON")
def items_JSON():
	return "items json"


@app.route("/item/<int:item_id>/JSON")
def item_JSON(item_id):
	return "item json"


@app.route("/category/<int:category_id>/item/JSON")
def category_items_json(category_id):
	return "category items json"


@app.route("/category/<int:category_id>/item/<int:item_id>/JSON")
def category_item_json(category_id, item_id):
	return "category item json"


if __name__ == "__main__":
    # To debug, Set to True, otherwise False
    app.debug = True
    app.run(host="0.0.0.0", port=5000)