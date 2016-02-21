import config

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('mysql://{}:{}@{}:{}/{}'.format(
    config.DB_USER,
    config.DB_PASS,
    config.DB_HOST,
    config.DB_PORT,
    config.DB_NAME))
Base = declarative_base(engine)
Session = sessionmaker(bind=engine)
session = Session()

class Project(Base):
    __tablename__ = 'project'
    __table_args__ = {'autoload':True}

class ManiphestTask(Base):
    __tablename__ = 'maniphest_task'
    __table_args__ = {'autoload':True}
