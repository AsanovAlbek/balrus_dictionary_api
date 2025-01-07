from pydantic import BaseModel
from words import model

class Word(BaseModel):
    id: int
    name: str
    meaning: str
    audio_url: str
    audio_path: str

def from_db(db_model: model.Word):
    return Word(
        id=db_model.id,
        name=db_model.name,
        meaning=db_model.meaning,
        audio_url=db_model.audio_url,
        audio_path=db_model.audio_path
    )