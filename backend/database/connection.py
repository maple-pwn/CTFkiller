from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session as DBSession
from backend.database.models import Base
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/agent_workspace"
)

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db() -> DBSession:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
