#!/usr/bin/env python3

# Imports from Flask
from flask import Flask
from flask import request, render_template, redirect, url_for
from flask import jsonify, flash

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
	categories = session.query(Category)
	items = session.query(Item)
	return render_template("index.html",
						   categories=categories,
						   items=items)


@app.route("/category/create/", methods=["GET", "POST"])
def create_category():
	categories = session.query(Category)
	if request.method == "GET":
		return render_template("category/create_category.html",
							   categories=categories)
	else:
		category = Category(name=request.form["name"])
		session.add(category)
		session.commit()
		flash("Added category "+ category.name)
		return redirect(url_for("index"))


@app.route("/category/<int:category_id>/update/", methods=["GET", "POST"])
def update_category(category_id):
	categories = session.query(Category)
	category = session.query(Category).filter_by(id=category_id).one()
	if request.method == "GET":
		return render_template("category/update_category.html",
							   category_id=category_id,
							   category_name=category.name,
							   categories=categories)
	else:
		old_name = category.name
		category.name = request.form["name"]
		session.add(category)
		session.commit()
		flash("Updated category " + old_name + " to " + category.name)
		return redirect(url_for("index"))


@app.route("/category/<int:category_id>/delete/", methods=["GET", "POST"])
def delete_category(category_id):
	categories = session.query(Category)
	category = session.query(Category).filter_by(id=category_id).one()
	if request.method == "GET":
		return render_template("category/delete_category.html",
							   category_id=category_id,
							   category_name=category.name,
							   categories=categories)
	else:
		session.delete(category)
		session.commit()
		flash("Deleted category " + category.name)
		return redirect(url_for("index"))


@app.route("/category/<int:category_id>/item/", methods=["GET"])
def read_item_by_category(category_id):
	categories = session.query(Category)
	category = categories.filter_by(id=category_id).one()
	items = session.query(Item).filter_by(category_id=category_id)
	return render_template("item/read_item_by_category.html",
						   items=items,
						   categories=categories,
						   category_name=category.name,
						   category_id=category_id)


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
						   category_name=category.name,
						   item_name=item.name,
						   category_id=category_id,
						   item_id=item_id)

@app.route("/category/<int:category_id>/item/create/", methods=["GET", "POST"])
def create_item(category_id):
	categories = session.query(Category)
	if request.method == "GET":
		return render_template("item/create_item.html",
							   category_id=category_id,
							   categories=categories)
	else:
		item = Item(name=request.form["name"],
					description=request.form["description"],
					category_id=category_id)
		session.add(item)
		session.commit()
		flash("Created item " + item.name)
		return redirect(url_for("read_item_by_category",
								category_id=category_id))


@app.route("/category/<int:category_id>/item/<int:item_id>/update/", methods=["GET", "POST"])
def update_item(category_id, item_id):
	categories = session.query(Category)
	item = session.query(Item).filter_by(id=item_id).one()
	if request.method == "GET":
		return render_template("item/update_item.html",
							   category_id=category_id,
							   item_id=item_id,
							   item=item,
							   categories=categories)
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
	categories = session.query(Category)
	item = session.query(Item).filter_by(id=item_id).one()
	if request.method == "GET":
		return render_template("item/delete_item.html",
							   category_id=category_id,
							   item_id=item_id,
							   categories=categories)
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