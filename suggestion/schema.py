from pydantic import BaseModel

class SuggestWord(BaseModel):
    id: int
    word: str
    meaning: str
    user_id: int