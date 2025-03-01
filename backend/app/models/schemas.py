from pydantic import BaseModel, EmailStr
from typing import Optional

# Request 
class UserCreate(BaseModel):
    full_name: str
    username: str
    email: EmailStr
    password: str

# Response
class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str

# Validating 
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenOut(BaseModel):
    id: Optional[str] = None