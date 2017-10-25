#!/usr/bin/env python3

# Imports from The Python Standard Library
import os
import sys

# Imports from SQLAlchemy toolkit
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine

# Create instance of declarative base class.
# Subclasses of the base class correspond to tables
# and their objects correspond to columns in database
Base = declarative_base()


class Category(Base):
    """Modal of Category:
    1. Set table name,
    2. Initialise columns: id, name"""

    __tablename__ = "category"
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }


class Item(Base):
    """Modal of Item:
    1. Set table name,
    2. Initialise columns: id, name, description, category_id
    3. Define relationship"""

    __tablename__ = "item"
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(1000))
    category_id = Column(Integer, ForeignKey("category.id"))
    category = relationship("Category", backref=backref("item", cascade="all, delete-orphan"))

    @property
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.name
        }

# Create instance of Engine class,
# which provides interface to database
engine = create_engine("sqlite:///item_catelog.db")

# Create tables using classes and corresponding mapper code
Base.metadata.create_all(engine)
