from datetime import datetime
from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id         = Column(BigInteger, primary_key=True, index=True)
    token      = Column(String(64), unique=True, nullable=False, index=True)
    user_id    = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    user       = relationship("User", back_populates="refresh_tokens")
    issued_at  = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked    = Column(Boolean, default=False, nullable=False)