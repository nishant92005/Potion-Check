import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


def uuid_str() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=uuid_str)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    profile = relationship("UserProfile", back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profiles"
    __table_args__ = (UniqueConstraint("user_id"),)
    id = Column(String, primary_key=True, default=uuid_str)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"))
    allergies = Column(JSON, default=list)
    health_conditions = Column(JSON, default=list)
    diet_type = Column(String, default="None")
    updated_at = Column(DateTime, onupdate=func.now())
    user = relationship("User", back_populates="profile")


class ScanHistory(Base):
    __tablename__ = "scan_history"
    id = Column(String, primary_key=True, default=uuid_str)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    barcode = Column(String, index=True)
    product_name = Column(String)
    product_image_url = Column(String, nullable=True)
    safety_score = Column(Integer)
    verdict = Column(String)
    flagged_count = Column(Integer, default=0)
    raw_product_data = Column(JSON, default=dict)
    created_at = Column(DateTime, server_default=func.now())
    analysis = relationship("Analysis", back_populates="scan", cascade="all, delete-orphan")


class Analysis(Base):
    __tablename__ = "analyses"
    id = Column(String, primary_key=True, default=uuid_str)
    scan_id = Column(ForeignKey("scan_history.id", ondelete="CASCADE"))
    safety_score = Column(Integer)
    verdict = Column(String)
    flagged_ingredients = Column(JSON, default=list)
    all_ingredients = Column(JSON, default=list)
    nutriments = Column(JSON, default=dict)
    ai_summary = Column(Text)
    ai_recommendation = Column(Text)
    personalized_warnings = Column(JSON, default=list)
    created_at = Column(DateTime, server_default=func.now())
    scan = relationship("ScanHistory", back_populates="analysis")
