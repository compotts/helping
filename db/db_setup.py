import os

import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

async def db_setup(
        metadata: sqlalchemy.MetaData
) -> AsyncEngine:
    engine = create_async_engine(DATABASE_URL)
    if not engine:
        raise RuntimeError("Database engine was not created properly")

    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    return engine
