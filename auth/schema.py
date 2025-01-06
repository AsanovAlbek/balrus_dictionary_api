from pydantic import BaseModel

class UserBase(BaseModel):
    name: str
    email: str
    imei: str
    is_active: bool = False
    is_admin: bool = False

class CreateUser(UserBase):
    password: str

class User(UserBase):
    id: int