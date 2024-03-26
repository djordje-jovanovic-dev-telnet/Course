from typing import Annotated, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr
from pydantic.types import conint
from datetime import datetime


class UserData(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True


class UserOut(BaseModel):
    id: int
    email: EmailStr
    followers: int
    following: int


class PostPatch(BaseModel):
    title: str


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = False


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut

    class Config:
        from_attributes = True


class PostOut(BaseModel):
    Post: Post
    votes: int

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    followers: int = 0
    following: int = 0


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)
    id: Optional[str] = None


class Vote(BaseModel):
    post_id: int
    dir: Annotated[int, conint(le=1)]


class Follow(BaseModel):
    followed_user_id: int
    dir: Annotated[int, conint(le=1)]


class UserFollow(BaseModel):
    id: int
    email: EmailStr
    following_count: int
    followers_count: int
    following: list[UserData] = []
    followers: list[UserData] = []
