from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import settings
from app.db.base import Base

settings.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

# TODO: should be configured by .env instead
DATABASE_URL = "sqlite+aiosqlite:///data/psygraph.db"

# not really sure how any of this after works or why but it does so im not touching it
engine = create_async_engine(DATABASE_URL, connect_args={"check_same_thread": False})


AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    import app.models  # makes sure all the models are loaded before create_all # pyright: ignore[]

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
