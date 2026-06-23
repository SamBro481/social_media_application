from pydantic import BaseModel
from typing import Literal

class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True
        
class UserLogin(BaseModel):
    email: str
    password: str
    
class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    user_id: int | None = None
    
    
class UserOut(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


class PostCreate(BaseModel):
    title: str
    content: str
    published: bool = True
    

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    published: bool 
    owner: UserOut
    
    class Config:
        from_attributes = True

class Vote(BaseModel):
    post_id: int
    dir: Literal[0, 1]
    

class PostVote(BaseModel):
    Post: PostResponse
    votes: int
    
    class Config:
        from_attributes = True
        
        

