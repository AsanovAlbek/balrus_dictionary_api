from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, Text
from database.database import Base

class Word(Base):
    __tablename__ = "balk"

    id = Column(Integer, name="id", primary_key=True, index=True, autoincrement=True)
    name = Column(Text, name='Name', index=True, nullable=False)
    meaning = Column(Text, name='TOLK', index=True, nullable=False)
    audio_url = Column(Text, name='audio_url', index=True, nullable=False)
    audio_path = Column(Text, name='audio_path', index=True, nullable=False)