from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Reservation(Base):
    __tablename__ = "rezerwacje"
    
    id = Column(Integer, primary_key=True, index=True)
    firstName = Column(String(100))
    lastName = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    createdAt = Column(TIMESTAMP(timezone=True)) 
    reservationDate = Column(TIMESTAMP(timezone=True))     
    service = Column(String(50))
    people = Column(Integer)
    duration = Column(Integer)
    whoCreated = Column(String(20))
    cancelled = Column(Boolean)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

class AppConfig(Base):
    __tablename__ = "ustawienia"

    id = Column(Integer, primary_key=True, index=True)
    stations = Column(Integer)
    seats = Column(Integer)