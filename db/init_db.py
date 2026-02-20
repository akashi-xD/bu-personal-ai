# db/init_db.py
from db.database import engine, Base
from db import models  # noqa: F401


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)