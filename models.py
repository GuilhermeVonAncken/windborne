import os
from sqlalchemy import create_engine, Column, Integer, String, Text, Date, Numeric, TIMESTAMP, UniqueConstraint, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/finance_db")
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), unique=True, index=True, nullable=False)
    name = Column(Text)
    exchange = Column(String(20))

class FinancialStatement(Base):
    __tablename__ = "financial_statements"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"))
    statement_type = Column(String(20), nullable=False)
    fiscal_date = Column(Date, nullable=False)
    period_type = Column(String(10), nullable=False)
    key = Column(Text, nullable=False)
    value = Column(Numeric)
    raw_value_text = Column(Text)
    retrieved_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    __table_args__ = (UniqueConstraint('company_id', 'statement_type', 'fiscal_date', 'period_type', 'key', name='uq_finstmt'),)

class FinancialMetric(Base):
    __tablename__ = "financial_metrics"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"))
    fiscal_date = Column(Date, nullable=False)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Numeric)
    computed_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    __table_args__ = (UniqueConstraint('company_id', 'fiscal_date', 'metric_name', name='uq_metrics'),)

def create_schema():
    Base.metadata.create_all(engine)
