from sqlalchemy import Column, Integer, String,DateTime
from database import Base
from datetime import datetime


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
class Filling(Base):

    __tablename__ = "fillings"

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

    uploaded_at = Column(
        DateTime,
        default=datetime.utcnow
    )
