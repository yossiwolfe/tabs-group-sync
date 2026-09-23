from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

DATABASE_URL = "sqlite:///./tabgroups.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} # this is only needed for sqlite so that FastAPI can use multiple threads
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine) # creates the actual .db file and the SQL tables