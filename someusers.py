#!/usr/bin/env python3

# Imports from SQLAlchemy toolkit
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Imports from "database_setup.py"
from database_setup import Base, Category, Item, User

# Connect to database,
# Create session
engine = create_engine('sqlite:///item_catelog.db')
# Bind schema constructs(mapper code) to engine
Base.metadata.bind = engine
# Create a configured Session class
DBSession = sessionmaker(bind=engine)
# Create a session
session = DBSession()

user1 = User(name="User1",
			 email="example1@example1.com",
			 picture="http://via.placeholder.com/100x100")
session.add(user1)
session.commit()

user2 = User(name="User2",
			 email="example2@example2.com",
			 picture="http://via.placeholder.com/100x100")
session.add(user2)
session.commit()
