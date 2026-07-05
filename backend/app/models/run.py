import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Run(Base):
    __tablename__ = "runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    repo_path = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    analysis = Column(JSON, nullable=True)
    report = Column(Text, nullable=True)
    transcript = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
