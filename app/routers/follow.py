from fastapi import APIRouter

from fastapi import Depends, HTTPException, status

from sqlalchemy.orm import Session

from app import schemas, models, database, oauth2

router = APIRouter(
    prefix="/follow",
    tags=["Follow"]
)

@router.post("/")
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