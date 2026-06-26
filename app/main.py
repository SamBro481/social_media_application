from fastapi import FastAPI
from fastapi import Depends
from fastapi import HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Query
from sqlalchemy import func

from . import database
from . import models
from . import schemas
from . import oauth2
from .utils import hash_password
from .utils import verify_password
from .oauth2 import create_access_token

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

@app.post("/users", response_model=schemas.UserResponse)
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

@app.get("/users/me", response_model=schemas.UserResponse)
def get_me(
    current_user: models.User = Depends(oauth2.get_current_user)
):
    return current_user
   

@app.get("/users/{id}", response_model=schemas.UserResponse)
def get_user(id: int, db: Session = Depends(database.get_db)):
    
    user = db.query(models.User).filter(models.User.id == id).first()
    
    if user is None:
        raise HTTPException(status_code=404, detail="User Not Found")
    
    return user

@app.get("/users", response_model=List[schemas.UserResponse])
def get_users(db: Session = Depends(database.get_db)):
    users = db.query(models.User).all()
    
    return users


@app.post("/login", response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), 
          db: Session = Depends(database.get_db)):
    
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    
    if not verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    
    access_token = create_access_token(
    data={"user_id": user.id}
)
    return {
    "access_token": access_token,
    "token_type": "bearer"
}

@app.post("/posts",
          response_model=schemas.PostResponse,
          status_code=status.HTTP_201_CREATED
          )
def create_post(post: schemas.PostCreate,
                db : Session = Depends(database.get_db),
                current_user: models.User = Depends(oauth2.get_current_user)
):
    
    new_post = models.Post(
        owner_id = current_user.id,
        **post.model_dump()
    )
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    return new_post
    
@app.get("/posts", response_model=List[schemas.PostVote])
def get_posts(db: Session = Depends(database.get_db),
              limit: int = Query(default=10, le=100),
              skip: int = Query(default=0, ge=0),
              search: str = ""):
    
    posts = ( 
             db.query(models.Post,
                      func.count(models.Vote.post_id).label("votes"))
            .join(
                models.Vote,
                models.Vote.post_id == models.Post.id,
                isouter=True
            )
            .filter(models.Post.title.contains(search))
            .group_by(models.Post.id)
            .limit(limit)
            .offset(skip)
            .all()
    )
            
    
    return posts

@app.get("/posts/{id}", response_model=schemas.PostVote)
def get_post(id: int, db: Session = Depends(database.get_db)):
    
    post = ( db.query(models.Post,
                      func.count(models.Vote.post_id).label("votes"))
            .join(
                models.Vote,
                models.Vote.post_id == models.Post.id,
                isouter=True
            )
            .filter(models.Post.id == id)
            .group_by(models.Post.id)
            .first()
    )

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post Not Found")
    return post

@app.delete("/posts/{id}")
def delete_post(id: int,
                db: Session = Depends(database.get_db),
                current_user: models.User = Depends(oauth2.get_current_user)):
    
    post = (
        db.query(models.Post).filter(models.Post.id == id).first()
    )
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post Not Foudn!")
    
    if(current_user.id != post.owner_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized")
    
    db.delete(post)
    db.commit()
    
    return Response(
        status_code = status.HTTP_204_NO_CONTENT
    )

@app.put("/posts/{id}", response_model=schemas.PostResponse)
def update_post(id: int,
                post: schemas.PostCreate,
                db: Session = Depends(database.get_db),
                current_user: models.User = Depends(oauth2.get_current_user)):
    
    post_query = db.query(models.Post).filter(models.Post.id == id)
    existing_post = post_query.first()
    
    if not existing_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post Not Found")
        
    if current_user.id != existing_post.owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorised Action")
    
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    
    return post_query.first()


@app.post("/vote")
def vote(vote: schemas.Vote,
         db: Session = Depends(database.get_db),
         current_user: models.User = Depends(oauth2.get_current_user)):
    
    post = (
        db.query(models.Post)
        .filter(models.Post.id == vote.post_id)
        .first()
    )
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Post Not Found")
    
    vote_query = ( db.query(models.Vote)
                  .filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)    
                 )       
    
    found_vote = vote_query.first()
    
    if vote.dir == 1:
        
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                                detail="Already voted on this post")
    
        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
    
        return {
            "message": "Successfully Added Vote"
        }
    
    if vote.dir == 0:
        
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Vote Not Found")
        
        vote_query.delete(
            synchronize_session=False
        )
        db.commit()
        return {
            "message": "Successfully Deleted Vote"
        }

@app.post("/follow")
def follow_user(
    follow: schemas.FollowRequest,
    current_user: models.User = Depends(oauth2.get_current_user),
    db: Session = Depends(database.get_db)
):
    
    user = (
        db.query(models.User)
        .filter(models.User.id == follow.user_id)
        .first()
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_404_BAD_REQUEST, detail="User Not Found")
    
    if follow.user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot Follow Yourself")
    
    follow_query = (
        db.query(models.Follow)
        .filter(models.Follow.follower_id == current_user.id, models.Follow.following_id == follow.user_id)
    )
    found_follow = follow_query.first()
    
    if follow.dir == 1:
        
        if found_follow:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already Following this user")
        
        new_follow = models.Follow(
            follower_id = current_user.id,
            following_id = follow.user_id
        )
        db.add(new_follow)
        db.commit()
        
        return {"message": "User Followed Successfully"}
    
    else:
        
        if not found_follow:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Following this User")
        
        follow_query.delete(synchronize_session=False)
        db.commit()
        
        return {"message": "User unfollowed Successfully"}


@app.get("users/{id}/followers", response_model=List[schemas.UserResponse])
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


@app.get("users/{id}/following", response_model=List[schemas.UserResponse])
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

