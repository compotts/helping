import os

import ormar
import databases
import sqlalchemy

from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

metadata = sqlalchemy.MetaData()
database = databases.Database(DATABASE_URL)
engine = sqlalchemy.create_engine(DATABASE_URL)

base_ormar_config = ormar.OrmarConfig(
    metadata=metadata,
    database=database,
    engine=engine
)
