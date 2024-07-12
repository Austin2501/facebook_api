from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from utils.config.db import get_db
from models.user import FacebookUser as UserModel, Friend as FriendModel, Chat as ChatModel, Status as StatusModel, Image as ImageModel
from schemas.user import FacebookUserCreateRequest, FacebookUser as UserSchema, Friend as FriendSchema, Chat as ChatSchema, Status as StatusSchema, Image as ImageSchema

import logger

user = APIRouter()

# User CRUD operations
@user.get("/")
async def read_users(db: Session = Depends(get_db)):
    logger.logger.info("Fetching all users")
    users = db.query(UserModel).all()
    return users

@user.get("/{id}")
async def read_user(id: int, db: Session = Depends(get_db)):
    logger.logger.info(f"Fetching user with id: {id}")
    user = db.query(UserModel).filter(UserModel.id == id).first()
    if user is None:
        logger.logger.error(f"User with id {id} not found")
        raise HTTPException(status_code=404, detail="User not found")
    return user

@user.post("/")
async def create_user(user: FacebookUserCreateRequest, db: Session = Depends(get_db)):
    logger.logger.info(f"Creating user with name: {user.name}")
    db_user = UserModel(name=user.name, friend_number=user.friend_number)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@user.put("/{id}")
async def update_user(id: int, user: FacebookUserCreateRequest, db: Session = Depends(get_db)):
    logger.logger.info(f"Updating user with id: {id}")
    db_user = db.query(UserModel).filter(UserModel.id == id).first()
    if db_user is None:
        logger.logger.error(f"User with id {id} not found")
        raise HTTPException(status_code=404, detail="User not found")
    db_user.name = user.name
    db_user.friend_number = user.friend_number
    db.commit()
    db.refresh(db_user)
    return db_user

@user.delete("/{id}")
async def delete_user(id: int, db: Session = Depends(get_db)):
    logger.logger.info(f"Deleting user with id: {id}")
    db_user = db.query(UserModel).filter(UserModel.id == id).first()
    if db_user is None:
        logger.logger.error(f"User with id {id} not found")
        raise HTTPException(status_code=404, detail="User not found")
    
    # Delete associated friends
    db.query(FriendModel).filter(FriendModel.user_id == id).delete()
    # Delete associated chats
    db.query(ChatModel).filter(ChatModel.user_id == id).delete()
    # Delete associated statuses
    db.query(StatusModel).filter(StatusModel.user_id == id).delete()
    
    # Delete the user
    db.delete(db_user)
    db.commit()
    return {"detail": "User and associated records deleted"}

# Friends CRUD operations
@user.get("/{user_id}/friends")
async def read_friends(user_id: int, db: Session = Depends(get_db)):
    logger.logger.info(f"Fetching friends for user with id: {user_id}")
    friends = db.query(FriendModel).filter(FriendModel.user_id == user_id).all()
    return friends

@user.post("/{user_id}/friends")
async def create_friend(user_id: int, friend: FriendSchema, db: Session = Depends(get_db)):
    logger.logger.info(f"Creating friend for user with id: {user_id}")
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if db_user:
        db_friend = FriendModel(name=friend.name, friend_number=friend.friend_number, user_id=user_id)
        db.add(db_friend)
        db.commit()
        db.refresh(db_friend)
        return db_friend
    else:
        raise HTTPException(status_code=404, detail="User not found")

@user.put("/{user_id}/friends/{friend_id}")
async def update_friend(user_id: int, friend_id: int, friend: FriendSchema, db: Session = Depends(get_db)):
    logger.logger.info(f"Updating friend with id: {friend_id} for user with id: {user_id}")
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if db_user:
        db_friend = db.query(FriendModel).filter(FriendModel.id == friend_id, FriendModel.user_id == user_id).first()
        if db_friend is None:
            logger.logger.error(f"Friend with id {friend_id} not found")
            raise HTTPException(status_code=404, detail="Friend not found")
        db_friend.name = friend.name
        db_friend.friend_number = friend.friend_number
        db.commit()
        db.refresh(db_friend)
        return db_friend
    else:
        raise HTTPException(status_code=404, detail="User not found")

@user.delete("/{user_id}/friends/{friend_id}")
async def delete_friend(user_id: int, friend_id: int, db: Session = Depends(get_db)):
    logger.logger.info(f"Deleting friend with id: {friend_id} for user with id: {user_id}")
    db_friend = db.query(FriendModel).filter(FriendModel.id == friend_id, FriendModel.user_id == user_id).first()
    if db_friend is None:
        logger.logger.error(f"Friend with id {friend_id} not found")
        raise HTTPException(status_code=404, detail="Friend not found")
    db.delete(db_friend)
    db.commit()
    return {"detail": "Friend deleted"}

# Chat CRUD operations
@user.get("/{user_id}/chats")
async def read_chats(user_id: int, db: Session = Depends(get_db)):
    logger.logger.info(f"Fetching chats for user with id: {user_id}")
    chats = db.query(ChatModel).filter(ChatModel.user_id == user_id).all()
    
    # Fetch images for each chat
    for chat in chats:
        chat.images = db.query(ImageModel).filter(ImageModel.chat_id == chat.id).all()
    
    return chats
    
@user.post("/{user_id}/chats")
async def create_chat(user_id: int, chat: ChatSchema, db: Session = Depends(get_db)):
    logger.logger.info(f"Creating chat for user with id: {user_id}")
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if db_user:
        db_chat = ChatModel(message=chat.message, user_id=user_id)
        db.add(db_chat)
        db.commit()
        db.refresh(db_chat)
        
        # Add images if any
        db_image = None
        if chat.images:
            for image in chat.images:
                db_image = ImageModel(url=image.url, name=image.name, chat_id=db_chat.id)
                db.add(db_image)
            db.commit()
            db.refresh(db_image)
        
        return db_image
    
    else:
        raise HTTPException(status_code=404, detail="User not found")

@user.put("/{user_id}/chats/{chat_id}")
async def update_chat(user_id: int, chat_id: int, chat: ChatSchema, db: Session = Depends(get_db)):
    logger.logger.info(f"Updating chat with id: {chat_id} for user with id: {user_id}")
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if db_user:
        db_chat = db.query(ChatModel).filter(ChatModel.id == chat_id, ChatModel.user_id == user_id).first()
        if db_chat is None:
            logger.logger.error(f"Chat with id {chat_id} not found")
            raise HTTPException(status_code=404, detail="Chat not found")
        db_chat.message = chat.message
        db.commit()
        db.refresh(db_chat)
        
        # Update images if any
        db_image = None
        if chat.images:
            db.query(ImageModel).filter(ImageModel.chat_id == chat_id).delete()
            for image in chat.images:
                db_image = ImageModel(url=image.url, name=image.name, chat_id=chat_id)
                db.add(db_image)
            db.commit()
            db.refresh(db_image)
        
        return db_image
    
    else:
        raise HTTPException(status_code=404, detail="User not found")

@user.delete("/{user_id}/chats/{chat_id}")
async def delete_chat(user_id: int, chat_id: int, db: Session = Depends(get_db)):
    logger.logger.info(f"Deleting chat with id: {chat_id} for user with id: {user_id}")
    db_chat = db.query(ChatModel).filter(ChatModel.id == chat_id, ChatModel.user_id == user_id).first()
    if db_chat is None:
        logger.logger.error(f"Chat with id {chat_id} not found")
        raise HTTPException(status_code=404, detail="Chat not found")
    db.delete(db_chat)
    db.commit()
    return {"detail": "Chat deleted"}

# Status CRUD operations
@user.get("/{user_id}/status")
async def read_status(user_id: int, db: Session = Depends(get_db)):
    logger.logger.info(f"Fetching status for user with id: {user_id}")
    status = db.query(StatusModel).filter(StatusModel.user_id == user_id).all()
    if not status:
        logger.logger.error(f"Status for user with id {user_id} not found")
        raise HTTPException(status_code=404, detail="Status not found")
    return status

@user.post("/{user_id}/status")
async def create_status(user_id: int, status: StatusSchema, db: Session = Depends(get_db)):
    logger.logger.info(f"Creating status for user with id: {user_id}")
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if db_user:
        db_status = StatusModel(content=status.content, user_id=user_id)
        db.add(db_status)
        db.commit()
        db.refresh(db_status)
        return db_status
    else:
        raise HTTPException(status_code=404, detail="User not found")

@user.put("/{user_id}/status/{status_id}")
async def update_status(user_id: int, status_id: int, status: StatusSchema, db: Session = Depends(get_db)):
    logger.logger.info(f"Updating status with id: {status_id} for user with id: {user_id}")
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if db_user:
        db_status = db.query(StatusModel).filter(StatusModel.id == status_id, StatusModel.user_id == user_id).first()
        if db_status is None:
            logger.logger.error(f"Status with id {status_id} not found")
            raise HTTPException(status_code=404, detail="Status not found")
        db_status.content = status.content
        db.commit()
        db.refresh(db_status)
        return db_status
    else:
        raise HTTPException(status_code=404, detail="User not found")

@user.delete("/{user_id}/status/{status_id}")
async def delete_status(user_id: int, status_id: int, db: Session = Depends(get_db)):
    logger.logger.info(f"Deleting status with id: {status_id} for user with id: {user_id}")
    db_status = db.query(StatusModel).filter(StatusModel.id == status_id, StatusModel.user_id == user_id).first()
    if db_status is None:
        logger.logger.error(f"Status with id {status_id} not found")
        raise HTTPException(status_code=404, detail="Status not found")
    db.delete(db_status)
    db.commit()
    return {"detail": "Status deleted"}

# New endpoint for fetching status from friend ID
@user.get("/friends/{friend_id}/status")
async def read_status_from_friend(friend_id: int, db: Session = Depends(get_db)):
    logger.logger.info(f"Fetching status for user associated with friend id: {friend_id}")
    friend = db.query(FriendModel).filter(FriendModel.id == friend_id).first()
    if friend is None:
        logger.logger.error(f"Friend with id {friend_id} not found")
        raise HTTPException(status_code=404, detail="Friend not found")
    
    user_status = db.query(StatusModel).filter(StatusModel.user_id == friend.user_id).all()
    if not user_status:
        logger.logger.error(f"No status found for user with id {friend.user_id}")
        raise HTTPException(status_code=404, detail="Status not found for the user")
    
    return user_status

# Include the router
api_router = APIRouter()
api_router.include_router(user, prefix="/users", tags=["users"])