from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, Text
from database.database import Base

class Word(Base):
    __tablename__ = "balk"

    id = Column(Integer, name="id", primary_key=True, index=True, autoincrement=True)
    name = Column(Text, name='Name', index=True)
    meaning = Column(Text, name='TOLK', index=True)
    audio_url = Column(Text, name='audio_url', index=True)