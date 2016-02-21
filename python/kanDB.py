from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# global
engine = create_engine('sqlite:///db.sqlite')
Base = declarative_base(engine)
Session = sessionmaker(bind=engine)
session = Session()

class Task(Base):
    __tablename__ = 'tasks'
    __table_args__ = {'autoload':True}

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'autoload':True}

class Subtask(Base):
    __tablename__ = 'subtasks'
    __table_args__ = {'autoload':True}

class Project(Base):
    __tablename__ = 'projects'
    __table_args__ = {'autoload':True}

class Column(Base):
    __tablename__ = 'columns'
    __table_args__ = {'autoload':True}