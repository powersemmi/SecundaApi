from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from api.settings import settings

engine = create_async_engine(
    settings.PG_URL.unicode_string(),
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)
