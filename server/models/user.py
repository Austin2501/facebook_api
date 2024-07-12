from utils.config.db import Base
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.mysql import INTEGER as Integer
from sqlalchemy.orm import relationship

class FacebookUser(Base):
    __tablename__ = "facebook_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, index=True, nullable=False)
    friend_number = Column(String, unique=True, nullable=False)
    friends = relationship("Friend", back_populates="user", cascade="all, delete-orphan")
    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")
    statuses = relationship("Status", back_populates="user", cascade="all, delete-orphan")

class Friend(Base):
    __tablename__ = "friends"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True, nullable=False)
    friend_name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("facebook_users.id", ondelete="CASCADE"), nullable=False)

    user = relationship("FacebookUser", back_populates="friends")

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message = Column(String, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("facebook_users.id", ondelete="CASCADE"), nullable=False)

    user = relationship("FacebookUser", back_populates="chats")
    images = relationship("Image", back_populates="chat", cascade="all, delete-orphan")

class Status(Base):
    __tablename__ = "statuses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("facebook_users.id", ondelete="CASCADE"), nullable=False)

    user = relationship("FacebookUser", back_populates="statuses")

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False)
    name = Column(String, nullable=False)
    chat_id = Column(Integer, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False)

    chat = relationship("Chat", back_populates="images")