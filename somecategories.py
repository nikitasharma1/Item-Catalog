#!/usr/bin/env python3

# Imports from SQLAlchemy toolkit
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Imports from "database_setup.py"
from database_setup import Base, Category, Item

# Connect to database,
# Create session
engine = create_engine('sqlite:///item_catelog.db')
# Bind schema constructs(mapper code) to engine
Base.metadata.bind = engine
# Create a configured Session class
DBSession = sessionmaker(bind=engine)
# Create a session
session = DBSession()

category1 = Category(name="category1")
session.add(category1)
session.commit()

category2 = Category(name="category2")
session.add(category2)
session.commit()

category3 = Category(name="category3")
session.add(category3)
session.commit()

category4 = Category(name="category4")
session.add(category4)
session.commit()

print("Categories added!")