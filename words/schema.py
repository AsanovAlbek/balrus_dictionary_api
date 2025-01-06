from pydantic import BaseModel

class Word(BaseModel):
    id: int
    name: str
    meaning: str
    audio_url: str