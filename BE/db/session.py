from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from settings.settings import settings

db_url = settings.database_url.strip()
connect_args = {'check_same_thread': False} if db_url.startswith('sqlite') else {}
engine = create_engine(db_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
