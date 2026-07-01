from fastapi import FastAPI
from fastapi import Depends
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from fastapi import Query
from sqlalchemy import func

from . import database
from . import models
from . import schemas
from . import oauth2

from app.routers import users
from app.routers import auth
from app.routers import posts

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(posts.router)



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

@app.get("/feed", response_model=List[schemas.PostVote])
def get_feed(
    current_user: models.User = Depends(oauth2.get_current_user),
    db: Session = Depends(database.get_db),
    limit: int = Query(default=10, le=100),
    offset: int = Query(default=0, ge=0)
):
    following = (
        db.query(models.Follow.following_id)
        .filter(models.Follow.follower_id == current_user.id)
    )
    
    feed = (
        db.query(
            models.Post,
            func.count(models.Vote.post_id).label("votes")
        )
        .join(
            models.Vote,
            models.Vote.post_id == models.Post.id,
            isouter=True
        )
        .filter(models.Post.owner_id.in_(following))
        .group_by(models.Post.id)
        .order_by(models.Post.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )
    return feed

