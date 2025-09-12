"""
API Key model for authentication and access control
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.core.database import Base


class APIKey(Base):
    """API Key model for authentication"""
    
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key_id = Column(String(100), unique=True, index=True, nullable=False)  # Public key identifier
    key_hash = Column(String(255), nullable=False)  # Hashed secret key
    name = Column(String(255), nullable=False)  # Human-readable name
    description = Column(Text, nullable=True)
    
    # User relationship
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="api_keys")
    
    # Status and permissions
    is_active = Column(Boolean, default=True, nullable=False)
    scopes = Column(JSON, default=list, nullable=False)  # List of allowed scopes
    
    # Rate limiting (overrides user defaults if set)
    requests_per_hour = Column(Integer, nullable=True)
    requests_per_day = Column(Integer, nullable=True)
    
    # Usage tracking
    total_requests = Column(Integer, default=0, nullable=False)
    total_cost_usd = Column(Integer, default=0, nullable=False)  # In cents
    last_used = Column(DateTime(timezone=True), nullable=True)
    
    # Expiration
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # IP restrictions
    allowed_ips = Column(JSON, default=list, nullable=False)  # List of allowed IP addresses/ranges
    
    # Relationships
    usage_records = relationship("Usage", back_populates="api_key", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<APIKey(id={self.id}, key_id='{self.key_id}', name='{self.name}')>"
    
    @property
    def is_expired(self) -> bool:
        """Check if the API key has expired"""
        if self.expires_at is None:
            return False
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        """Check if the API key is valid for use"""
        return self.is_active and not self.is_expired
    
    def has_scope(self, scope: str) -> bool:
        """Check if the API key has a specific scope"""
        return scope in self.scopes or "*" in self.scopes

