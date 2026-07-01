from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException

from sqlalchemy.orm import Session

from app import schemas, models, database
from app.utils import verify_password
from app.oauth2 import create_access_token


router = APIRouter(
    tags=["Authentication"]
)

@router.post("/login", response_model=schemas.Token)
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


