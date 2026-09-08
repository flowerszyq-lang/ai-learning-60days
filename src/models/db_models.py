from sqlalchemy import Column, String, Float, DateTime, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from ..database import Base
from sqlalchemy import Column, String, Text
from pgvector.sqlalchemy import Vector  # 需要安装 pgvector 的 Python 包

class Customer(Base):
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False)
    id_card = Column(String(18), unique=True, nullable=False)
    phone = Column(String(11), nullable=False)
    risk_level = Column(String(10), default="LOW")
    created_at = Column(DateTime, default=datetime.utcnow)

class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), nullable=False)
    account_type = Column(String(20), nullable=False)
    balance = Column(Float, default=0.0)
    status = Column(String(10), default="ACTIVE")
    created_at = Column(DateTime, default=datetime.utcnow)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(String(10), nullable=False)  # INCOME or EXPENSE
    note = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)

# class Document(Base):
#     __tablename__ = "documents"
#
# id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
# content = Column(Text, nullable=False)
# metadata = Column(String(200))  # 可存来源、标题等
# embedding = Column(Vector(384))  # 384 是 Sentence-BERT 的维度