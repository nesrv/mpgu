from sqlalchemy import Column, Integer
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

import os


DATABASE_URL = "postgresql+asyncpg://student:password@db:5432/student_db"

engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class Counter(Base):
    __tablename__ = "counter"
    id = Column(Integer, primary_key=True, default=1)
    value = Column(Integer, default=0)