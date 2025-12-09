"""
数据库初始化
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

Base = declarative_base()


def init_db_session(
    db_url: str,
    db_echo: bool = False,
    is_create_tables: bool = False,
) -> sessionmaker[Session]:
    """
    初始化同步数据库会话

    Args:
        db_url: 数据库连接URL
        db_echo: 是否打印SQL语句
        is_create_tables: 是否自动创建表

    Returns:
        Session工厂
    """
    engine = create_engine(db_url, echo=db_echo, pool_pre_ping=True)

    if is_create_tables:
        # 注意：调用方需要确保所有模型已被导入
        # 可以在 app/models/__init__.py 中导入所有模型
        Base.metadata.create_all(bind=engine)

    session_factory: sessionmaker[Session] = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
    )
    return session_factory


def init_db_async_session(
    db_url: str,
    db_echo: bool = False,
    is_create_tables: bool = False,
) -> async_sessionmaker[AsyncSession]:
    """
    初始化异步数据库会话

    Args:
        db_url: 异步数据库连接URL
        db_echo: 是否打印SQL语句
        is_create_tables: 是否自动创建表（注意：异步引擎需要同步方式创建表）

    Returns:
        AsyncSession工厂
    """
    engine = create_async_engine(db_url, echo=db_echo, pool_pre_ping=True)

    if is_create_tables:
        # 异步引擎需要使用同步方式创建表
        # 注意：调用方需要确保所有模型已被导入
        sync_url = (
            db_url.replace("+aiosqlite", "")
            .replace("+asyncpg", "")
            .replace("+aiomysql", "+pymysql")
        )
        sync_engine = create_engine(sync_url, echo=db_echo)
        Base.metadata.create_all(bind=sync_engine)
        sync_engine.dispose()

    async_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    return async_session_factory
