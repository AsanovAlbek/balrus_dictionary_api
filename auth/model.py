from sqlalchemy import Column, String, Integer, Boolean, DateTime, func
from database.database import Base
import datetime

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer(), primary_key=True)
    name = Column(String(), nullable=False)
    email = Column(String(), unique=True, nullable=False)
    password = Column(String(), nullable=False)
    imei = Column(String(), nullable=False)
    is_active = Column(Boolean(), default=False, nullable=False)
    is_superuser = Column(Boolean(), default=False, nullable=False)
    created_date = Column(DateTime, nullable=False, default=datetime.timezone.utc, server_default=func.now())

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
    date_of_creation = Column(DateTime, nullable=False, default=datetime.timezone.utc, server_default=func.now())
    expiration_date = Column(DateTime, nullable=False)