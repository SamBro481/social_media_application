from fastapi import APIRouter
from fastapi import Depends, status, HTTPException
from fastapi import Response, Query


from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app import schemas, models, database, oauth2


router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

@router.post("/",
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


@router.get("/", response_model=List[schemas.PostVote])
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


@router.get("/{id}", response_model=schemas.PostVote)
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



@router.delete("/{id}")
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
    


@router.put("/{id}", response_model=schemas.PostResponse)
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

