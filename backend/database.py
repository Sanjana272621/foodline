from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Default DB URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./food_donation.db"

# Create engine and session factory dynamically
def get_engine_and_session(db_url=SQLALCHEMY_DATABASE_URL):
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal

# Production engine/session
engine, SessionLocal = get_engine_and_session()

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
