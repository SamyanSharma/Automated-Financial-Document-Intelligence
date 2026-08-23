from sqlalchemy import Column, Integer, String, DateTime,Float, Text,JSON
from database import Base
from datetime import datetime
from sqlalchemy import ForeignKey

class Company(Base):

    __tablename__ = "companies"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    ticker = Column(
        String,
        unique=True
    )

    sector = Column(
        String
    )
class Filing(Base):

    __tablename__ = "filings"

    id = Column(
    Integer,
    primary_key=True,
    index=True
    )

    company_name = Column(
        String
    )

    filename = Column(
        String
    )

    file_path = Column(
        String
    )
    extracted_text = Column(
        String
    )
    uploaded_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class DocumentChunk(Base):

    __tablename__ = "document_chunks"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    filing_id = Column(
        Integer,
        nullable=False
    )

    chunk_index = Column(
        Integer,
        nullable=False
    )

    text = Column(
        Text,
        nullable=False
    )

    page_number = Column(
        Integer,
        nullable=True
    )
    embedding = Column(JSON, nullable=True)

class FinancialMetric(Base):

    __tablename__ = "financial_metrics"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    document_id = Column(
        Integer,
        nullable=False
    )


    company_name = Column(
        String,
        nullable=True
    )


    financial_year = Column(
        String,
        nullable=True
    )


    revenue = Column(
        Float,
        nullable=True
    )


    total_assets = Column(
        Float,
        nullable=True
    )


    total_liabilities = Column(
        Float,
        nullable=True
    )


    debt = Column(
        Float,
        nullable=True
    )


    cash_flow = Column(
        Float,
        nullable=True
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )