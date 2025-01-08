from pydantic import BaseModel
from auth import model

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

def from_db(db_user: model.User):
    return User(
        id=db_user.id,
        name=db_user.name,
        email=db_user.email,
        imei=db_user.imei,
        is_active=db_user.is_active,
        is_admin=db_user.is_admin
    )