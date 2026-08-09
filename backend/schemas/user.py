"""
Pydantic v2 schemas for auth requests/responses.

UserCreate/UserLogin validate incoming data (e.g. EmailStr catches malformed
emails before we ever touch the DB). UserOut never includes the password
hash - it's the safe shape we're allowed to return to clients.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
