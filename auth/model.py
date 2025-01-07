from sqlalchemy import Column, String, Integer, Boolean, DateTime, func
from database.database import Base
import datetime

class User(Base):
    __tablename__ = 'Users'

    id = Column(Integer(), primary_key=True)
    name = Column(String(), nullable=False)
    email = Column(String(), unique=True, nullable=False)
    password = Column(String(), nullable=False)
    imei = Column(String(), nullable=False)
    is_active = Column(Boolean(), default=False, nullable=False)
    is_admin = Column(Boolean(), default=False, nullable=False)
    created_date = Column(DateTime, nullable=False, default=datetime.datetime.now())

class Activation(Base):
    __tablename__ = 'activations'

    id = Column(Integer(), primary_key=True)
    user_email = Column(String(), unique=True, nullable=False)
    code = Column(String(), nullable=False)
    expiration_date = Column(DateTime, nullable=False)

class Reset(Base):
    __tablename__ = 'resets'

    id = Column(Integer(), primary_key=True)
    user_email = Column(String(), unique=True, nullable=False)
    code = Column(String(), nullable=False)
    created_date = Column(DateTime, nullable=False, default=datetime.datetime.now())
    expiration_date = Column(DateTime, nullable=False)