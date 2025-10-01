# backend/utils/db.py
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()  # make sure .env exists in backend/

DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "password032005")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3307")
DB_NAME = os.getenv("DB_NAME", "classicmodels")

DB_PASS_QUOTED = quote_plus(DB_PASS)
DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS_QUOTED}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Ensure database exists (connect to server, create DB if absent)
tmp_engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASS_QUOTED}@{DB_HOST}:{DB_PORT}/")
with tmp_engine.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"))
tmp_engine.dispose()

# main engine
engine = create_engine(DB_URL, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
