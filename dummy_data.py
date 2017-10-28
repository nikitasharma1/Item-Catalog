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

# Add some users
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

print("Users added!")

# Add some categories
category1 = Category(name="category1",
                     user_id=1)
session.add(category1)
session.commit()

category2 = Category(name="category2",
                     user_id=1)
session.add(category2)
session.commit()

category3 = Category(name="category3",
                     user_id=1)
session.add(category3)
session.commit()

category4 = Category(name="category4",
                     user_id=1)
session.add(category4)
session.commit()

print("Categories added!")

# Add some items
item1 = Item(name="item1",
             description="description1",
             category_id=1,
             user_id=1)
session.add(item1)
session.commit()

item2 = Item(name="item2",
             description="description2",
             category_id=1,
             user_id=2)
session.add(item2)
session.commit()

item3 = Item(name="item3",
             description="description3",
             category_id=2,
             user_id=1)
session.add(item3)
session.commit()

item4 = Item(name="item4",
             description="description4",
             category_id=2,
             user_id=2)
session.add(item4)
session.commit()

item5 = Item(name="item5",
             description="description5",
             category_id=3,
             user_id=1)
session.add(item5)
session.commit()

item6 = Item(name="item6",
             description="description6",
             category_id=3,
             user_id=2)
session.add(item6)
session.commit()

item7 = Item(name="item7",
             description="description7",
             category_id=4,
             user_id=1)
session.add(item7)
session.commit()

item8 = Item(name="item8",
             description="description8",
             category_id=4,
             user_id=2)
session.add(item8)
session.commit()

print("Items added!")
