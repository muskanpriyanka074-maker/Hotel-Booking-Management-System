from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker



# Database URL for hotel_db (Update username/password if required)
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:chetna2920@localhost:5432/hotel_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Task 11: Dependency Injection get_db() with Depends()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()