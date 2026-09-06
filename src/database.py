from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from .config import settings

# 异步引擎，echo=True 会打印 SQL 日志（便于调试）
engine = create_async_engine(settings.database_url, echo=True)
# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
# ORM 基类
Base = declarative_base()