"""
Usage tracking model for monitoring API usage and costs
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.core.database import Base


class Usage(Base):
    """Usage tracking model for API calls and costs"""
    
    __tablename__ = "usage"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    api_key_id = Column(Integer, ForeignKey("api_keys.id"), nullable=False)
    
    user = relationship("User", back_populates="usage_records")
    api_key = relationship("APIKey", back_populates="usage_records")
    
    # Request details
    request_id = Column(String(100), unique=True, index=True, nullable=False)
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    
    # Model and provider information
    model = Column(String(100), nullable=False)
    provider = Column(String(50), nullable=False)  # openai, anthropic, google, etc.
    
    # Token usage
    prompt_tokens = Column(Integer, default=0, nullable=False)
    completion_tokens = Column(Integer, default=0, nullable=False)
    total_tokens = Column(Integer, default=0, nullable=False)
    
    # Cost tracking (in USD cents for precision)
    prompt_cost_cents = Column(Integer, default=0, nullable=False)
    completion_cost_cents = Column(Integer, default=0, nullable=False)
    total_cost_cents = Column(Integer, default=0, nullable=False)
    
    # Request metadata
    request_duration_ms = Column(Integer, nullable=True)  # Request duration in milliseconds
    cache_hit = Column(String(20), default="miss", nullable=False)  # hit, miss, partial
    
    # Status and error tracking
    status_code = Column(Integer, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Additional metadata
    request_metadata = Column(JSON, default=dict, nullable=False)  # Additional request metadata
    
    # Client information
    client_ip = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Usage(id={self.id}, request_id='{self.request_id}', model='{self.model}', cost={self.total_cost_usd:.4f})>"
    
    @property
    def total_cost_usd(self) -> float:
        """Get total cost in USD"""
        return self.total_cost_cents / 100.0
    
    @property
    def prompt_cost_usd(self) -> float:
        """Get prompt cost in USD"""
        return self.prompt_cost_cents / 100.0
    
    @property
    def completion_cost_usd(self) -> float:
        """Get completion cost in USD"""
        return self.completion_cost_cents / 100.0
    
    @property
    def was_successful(self) -> bool:
        """Check if the request was successful"""
        return 200 <= self.status_code < 300
    
    @property
    def cache_savings_usd(self) -> float:
        """Calculate cost savings from cache hit"""
        if self.cache_hit == "hit":
            return self.total_cost_usd
        elif self.cache_hit == "partial":
            return self.total_cost_usd * 0.5  # Assume 50% savings for partial hits
        return 0.0

