from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, Text, String, Enum, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.enums import ContractType

class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(Enum(ContractType), nullable=False)  # Assuming you use an Enum for contract types
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    chats = relationship("Chat", back_populates="contract", cascade="all, delete-orphan")