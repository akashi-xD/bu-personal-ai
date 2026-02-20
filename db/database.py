from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os

DATABASE_URL = (
    f"postgresql+asyncpg://{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:"
    f"{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

engine = create_async_engine(DATABASE_URL)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass