from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func

from chatbot.db.database import Base


class User(Base):
    __tablename__ = "users" 
    
    id = Column(Integer, primary_key=True, index=True)
    
    email = Column(String(255), nullable=False, unique=True)
    
    name = Column(String(100), nullable=False)
    
    age = Column(Integer, nullable=True) 
    
    city = Column(String(100), nullable=True)
    
    factor1 = Column(String(255), nullable=True)
    factor2 = Column(String(255), nullable=True)
    factor3 = Column(String(255), nullable=True)
    
    voice_code = Column(String(4), nullable=True)
    
    active = Column(Boolean, nullable=False, default=False)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    
    context = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', active={self.active})>"