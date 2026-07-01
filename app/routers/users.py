from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session
from typing import List

from app import schemas, database, models
from app import oauth2
from app.utils import hash_password



router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    hashed_password = hash_password(user.password)
    new_user = models.User(
        username = user.username,
        email = user.email,
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.get("/me", response_model=schemas.UserResponse)
def get_me(
    current_user: models.User = Depends(oauth2.get_current_user)
):
    return current_user


@router.get("/{id}", response_model=schemas.UserResponse)
def get_user(id: int, db: Session = Depends(database.get_db)):
    
    user = db.query(models.User).filter(models.User.id == id).first()
    
    if user is None:
        raise HTTPException(status_code=404, detail="User Not Found")
    
    return user


@router.get("/", response_model=List[schemas.UserResponse])
def get_users(db: Session = Depends(database.get_db)):
    users = db.query(models.User).all()
    
    return users


@router.get("/{id}/followers", response_model=List[schemas.UserResponse])
def get_followers(
    id: int,
    db: Session = Depends(database.get_db)
):
    followers = (
        db.query(models.User)
        .join(
            models.Follow,
            models.Follow.follower_id == models.User.id
        )
        .filter(models.Follow.following_id == id)
        .all()
    )
    
    return followers


@router.get("/{id}/following", response_model=List[schemas.UserResponse])
def get_following(
    id: int,
    db: Session = Depends(database.get_db)
):
    following = (
        db.query(models.User)
        .join(
            models.Follow,
            models.Follow.following_id == models.User.id
        )
        .filter(models.Follow.follower_id == id)
        .all()
    )
    
    return following