from pydantic import BaseModel
from suggestion import model


class CreateSuggestWord(BaseModel):
    word: str
    meaning: str


class SuggestWord(CreateSuggestWord):
    id: int
    user_id: int


def from_db(db_model: model.SuggestWord):
    return SuggestWord(
        id=db_model.id, 
        word=db_model.word, 
        meaning=db_model.meaning, 
        user_id=db_model.user_id
    )
