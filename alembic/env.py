import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import pool
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

load_dotenv()

config = context.config
fileConfig(config.config_file_name)

db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"


config.set_main_option("sqlalchemy.url", DATABASE_URL)

from task_api.infrastructure.db.models import Base

target_metadata = Base.metadata


def run_migrations_offline():
    """Запуск в offline режиме."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"}
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Запуск в online режиме с async движком."""
    connectable = create_async_engine(DATABASE_URL, poolclass=pool.NullPool)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())