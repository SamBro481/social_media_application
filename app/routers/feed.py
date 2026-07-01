from fastapi import APIRouter
from fastapi import Depends, Query

from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List

from app import schemas, models, database, oauth2

router = APIRouter(
    prefix="/feed",
    tags=["Feed"]
)

@router.get("/", response_model=List[schemas.PostVote])
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