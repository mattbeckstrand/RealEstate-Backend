from sqlalchemy import Column, Integer, String, JSON, DateTime # type: ignore   
from sqlalchemy.sql import func # type: ignore
from ..database import Base # type: ignore

class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    source_type = Column(String)  # e.g., "zillow", "mls", "tax_records"
    raw_data = Column(JSON)  # Store raw data as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 