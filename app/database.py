from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()
user = os.getenv('DB_USER','')
password = os.getenv('DB_PASSWORD','') 
host = os.getenv('DB_HOST','')
port = os.getenv('DB_PORT','0')
database = os.getenv('DB_NAME','')

SQLALCHEMY_DATABASE_URL = "postgresql://"+user+":"+password+"@"+host+":"+port+"/"+database
engine = create_engine(SQLALCHEMY_DATABASE_URL,pool_size=50, max_overflow=10)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db        
    finally:
        db.close()
