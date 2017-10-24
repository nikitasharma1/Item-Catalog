#!/usr/bin/env python3

# Imports from SQLAlchemy toolkit
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Imports from "database_setup.py"
from database_setup import Base, Category, Item

# Connect to database,
# Create session
engine = create_engine("sqlite:///item_catelog.db")
# Bind schema constructs(mapper code) to engine
Base.metadata.bind = engine
# Create a configured Session class
DBSession = sessionmaker(bind=engine)
# Create a session
session = DBSession()

item1 = Item(name="item1",
			 description="description1",
			 category_id=1 )
session.add(item1)
session.commit()

item2 = Item(name="item2",
			 description="description2",
			 category_id=1 )
session.add(item2)
session.commit()

item3 = Item(name="item3",
			 description="description3",
			 category_id=2 )
session.add(item3)
session.commit()

item4 = Item(name="item4",
			 description="description4",
			 category_id=2 )
session.add(item4)
session.commit()

item5 = Item(name="item5",
			 description="description5",
			 category_id=3 )
session.add(item5)
session.commit()

item6 = Item(name="item6",
			 description="description6",
			 category_id=3 )
session.add(item6)
session.commit()

item7 = Item(name="item7",
			 description="description7",
			 category_id=4 )
session.add(item7)
session.commit()

item8 = Item(name="item8",
			 description="description8",
			 category_id=4 )
session.add(item8)
session.commit()

print("Items added!")