from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


URL = ''
engine = create_engine(URL)
Sessionlocal = sessionmaker(aurtocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
