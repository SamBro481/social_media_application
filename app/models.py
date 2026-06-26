from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP, text
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        nullable=False
    )

    username = Column(
        String,
        nullable=False
    )

    email = Column(
        String,
        nullable=False
    )
    
    password = Column(
        String,
        nullable=False
    )
    
class Post(Base):
    __tablename__ = "posts"
    
    id = Column(
        Integer,
        primary_key=True,
        nullable=False
    )
    
    title = Column(
        String,
        nullable=False
    )
    
    content = Column(
        String,
        nullable=False
    )
    
    published = Column(
        Boolean,
        default=True
    )
    
    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )
    owner = relationship("User")
    

class Vote(Base):
    __tablename__ = "votes"
    
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    
    post_id = Column(
        Integer,
        ForeignKey("posts.id", ondelete="CASCADE"),
        primary_key=True
    )
    

class Follow(Base):
    __tablename__ = "follows"
    
    follower_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    
    following_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()")
    )


    
