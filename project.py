#!/usr/bin/env python

# Imports from Flask
from flask import Flask
from flask import request, render_template, redirect, url_for

# Create Flask instance
app = Flask(__name__)

@app.route("/login")
def showLogin():
	return render_template("login.html")


@app.route("/", methods=["GET"])
def index():
	return render_template("index.html")


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