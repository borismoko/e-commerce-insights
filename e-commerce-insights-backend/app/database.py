from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from decouple import config

# Load database URL from environment variables (from .env file)
DATABASE_URL = config(
    "DATABASE_URL",
    default="postgresql+psycopg2://postgres:postgres@localhost:5432/ecommerce"
)

engine = create_engine(DATABASE_URL,
                       connect_args={'check_same_thread': False} if DATABASE_URL.startswith('postgres://') else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
