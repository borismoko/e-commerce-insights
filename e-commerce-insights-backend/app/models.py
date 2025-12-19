from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Numeric, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(100), default='analyst')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to uploaded files
    uploaded_files = relationship("FileMetadata", back_populates="user")


class FileMetadata(Base):
    __tablename__ = "file_metadata"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    upload_time = Column(DateTime(timezone=True), server_default=func.now())
    processed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationship to user
    user = relationship("User", back_populates="uploaded_files")
    # Relationship to sales data
    sales_data = relationship("SalesData", back_populates="file_metadata")


class SalesData(Base):
    __tablename__ = "sales_data"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(100), nullable=True, index=True)
    user_name = Column(String(255), nullable=True, index=True)
    age = Column(Integer, nullable=True)
    country = Column(String(100), nullable=True, index=True)
    product_category = Column(String(100), nullable=True, index=True)
    purchase_amount = Column(Numeric(10, 2), nullable=True)
    payment_method = Column(String(50), nullable=True, index=True)
    transaction_date = Column(DateTime, nullable=True, index=True)
    file_id = Column(Integer, ForeignKey("file_metadata.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to file metadata
    file_metadata = relationship("FileMetadata", back_populates="sales_data")
