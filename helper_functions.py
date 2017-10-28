#!/usr/bin/env python3

# Imports from The Python Standard Library
import random
import string

# Imports from "database_setup.py"
from database_setup import Base, Category, Item, User


# Create anti forgery state token
def AFStateToken():
    """Returns anti forgery state token"""
    state = ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for x in range(32))
    return state


def UnauthorizeUD(login_session, creator_id):
    """Forbids the user from performing an action on an object
    not created by that user and returns corresponding response"""

    if creator_id != login_session["user_id"]:
        response = make_response(
            json.dumps("Unauthorized"), 401)
        response.headers["Content-Type"] = "application/json"
        return response


def deleteObject(session, object):
    """Deletes an object"""

    # Delete object
    session.delete(object)
    # Save changes to database
    session.commit()
    # Return message
    return "Deleted"


# User helper functions
def getUserId(email, session):
    """Returns user id corresponding to the given email"""

    try:
        # For given email, get user object
        user = session.query(User).filter_by(email=email).one()
        # Return user id
        return user_id
    except Exception as e:
        # If user not found,
        return None


def createUser(login_session, session):
    """Perform Insert on user table"""

    # Create user object,
    # with attribute values from login_session
    user = User(name=login_session["username"],
                email=login_session["email"],
                picture=login_session["picture"])
    # Add user object to session
    session.add(user)
    # Save object to database
    session.commit()
    # Return user id
    return user.id


# Category helper functions
def getCategoryAll(session):
    """Returns list of all category objects from database"""

    try:
        # Get all categories from database
        categories = session.query(Category).all()
        # Return categories object
        return categories
    except Exception as e:
        # If no category found,
        return None


def getCategoryOne(session, category_id):
    """Returns the category object for given id"""

    try:
        # Get category for given category id
        category = session.query(Category).filter_by(id=category_id).one()
        # Return category object
        return category
    except Exception as e:
        # If no category found,
        return None


def CUCategory(session, login_session, name, CU, id=None):
    """Performs Insert or Update on category table
    depending upon the value of CU"""

    if CU == "Create":
        # Create category
        category = Category(name=name,
                            user_id=login_session["user_id"])
    elif CU == "Update":
        # Update category
        category = getCategoryOne(session, id)
        category.name = name

    # Add category object to session
    session.add(category)
    # Save object to database
    session.commit()
    # return category id
    return category.id


# Item helper functions
def getItemAll(session):
    """Returns all item objects from database"""

    try:
        # Get all items from database
        items = session.query(Item).all()
        # Return items object
        return items
    except Exception as e:
        # If no item found,
        return None


def getItemOne(session, item_id):
    """Returns item object for given id"""

    try:
        # Get item for given category id
        item = session.query(Item).filter_by(id=item_id).one()
        # Return item object
        return item
    except Exception as e:
        # If no item found,
        return None


def getItemByCategory(session, category_id):
    """Returns all item objects for given category id"""

    try:
        # Get items by category id
        items = session.query(Item).filter_by(category_id=category_id).all()
        # Return items object
        return items
    except Exception as e:
        # If no item found,
        return None


def CUItem(session, login_session,
           name, description, category_id, CU, id=None):
    """Performs Insert or Update on item table
    depending upon the value of CU"""

    if CU == "Create":
        # Create item
        item = Item(name=name,
                    description=description,
                    category_id=category_id,
                    user_id=login_session["user_id"])
    elif CU == "Update":
        # Update item
        item = getItemOne(session, id)
        item.name = name
        item.description = description

    # Add item object to session
    session.add(item)
    # Save object to database
    session.commit()
    # Return item id
    return item.id
