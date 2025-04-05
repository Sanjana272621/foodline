from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    user_type = Column(String, nullable=False)  # "donor" or "recipient"
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Relationships
    gatherings = relationship("Gathering", back_populates="user")
    claims = relationship("Claim", back_populates="recipient", foreign_keys="Claim.recipient_id")

class Gathering(Base):
    __tablename__ = 'gatherings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    food_details = Column(String, nullable=False)
    available_from = Column(DateTime, nullable=False)
    available_to = Column(DateTime, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    is_taken = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="gatherings")
    claims = relationship("Claim", back_populates="gathering")

class Claim(Base):
    __tablename__ = 'claims'
    
    id = Column(Integer, primary_key=True)
    recipient_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    gathering_id = Column(Integer, ForeignKey('gatherings.id'), nullable=False)
    claim_time = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)  # "claimed", "collected", "cancelled"
    
    # Relationships
    recipient = relationship("User", back_populates="claims", foreign_keys=[recipient_id])
    gathering = relationship("Gathering", back_populates="claims")