from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://eq_test_m5sz_user:KPrC6DS9MNo9aEgsz8EoUxGx6CgkKeNk@dpg-d1pp7nqdbo4c73bprhb0-a.oregon-postgres.render.com:5432/eq_test_m5sz?sslmode=require")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
