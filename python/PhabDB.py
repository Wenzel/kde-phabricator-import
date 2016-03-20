import config

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('mysql+cymysql://{}:{}@{}/{}'.format(
    config.DB_USER,
    config.DB_PASS,
    config.DB_HOST,
    config.DB_NAME))
Base = declarative_base(engine)
Session = sessionmaker(bind=engine)
session = Session()

class ManiphestTransactionComment(Base):
    __tablename__ = 'maniphest_transaction_comment'
    __table_args__ = {'autoload':True}
