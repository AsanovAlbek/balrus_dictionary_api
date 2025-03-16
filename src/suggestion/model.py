from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, Text
from database.database import Base

class SuggestWord(Base):
    __tablename__ = "suggest"

    id = Column(Integer, name="id", primary_key=True, index=True, autoincrement=True)
    word = Column(Text, name='word', index=True)
    meaning = Column(Text, name='meaning', index=True)
    user_id = Column(Integer, name='user_id', index=True)