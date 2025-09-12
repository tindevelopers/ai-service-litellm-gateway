"""
User model for authentication and account management
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.core.database import Base


class User(Base):
    """User model for account management"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Billing and limits
    plan_type = Column(String(50), default="free", nullable=False)  # free, pro, enterprise
    monthly_budget_usd = Column(Float, default=0.0, nullable=False)
    current_usage_usd = Column(Float, default=0.0, nullable=False)
    
    # Rate limiting
    requests_per_hour = Column(Integer, default=100, nullable=False)
    requests_per_day = Column(Integer, default=1000, nullable=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Additional info
    company = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    usage_records = relationship("Usage", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"
    
    @property
    def is_budget_exceeded(self) -> bool:
        """Check if user has exceeded their monthly budget"""
        if self.monthly_budget_usd <= 0:
            return False
        return self.current_usage_usd >= self.monthly_budget_usd
    
    @property
    def remaining_budget(self) -> float:
        """Get remaining budget for the month"""
        if self.monthly_budget_usd <= 0:
            return float('inf')
        return max(0, self.monthly_budget_usd - self.current_usage_usd)

