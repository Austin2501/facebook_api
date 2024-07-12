from pydantic import BaseModel
from typing import List, Optional

class Image(BaseModel):
    url: str
    name: str
    
    class Config:
        from_attributes = True

class Chat(BaseModel):
    message: str
    user_id: int
    images: Optional[List[Image]] = []

    class Config:
        from_attributes = True

class Status(BaseModel):
    content: str
    user_id: int

    class Config:
        from_attributes = True

class Friend(BaseModel):
    name: str
    friend_name: str 
    user_id: int

    class Config:
        from_attributes = True

class FacebookUserCreateRequest(BaseModel):
    name: str
    friend_name: str

class FacebookUser(BaseModel):
    name: str
    friend_name: str
    friends: Optional[List[Friend]] = []
    chats: Optional[List[Chat]] = []
    statuses: Optional[List[Status]] = []

    class Config:
        from_attributes = True