from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP, text
from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy.sql import func

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
    
    posts = relationship(
    "Post",
    back_populates="owner",
    cascade="all, delete"
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
    
    created_at = Column(
    TIMESTAMP(timezone=True),
    nullable=False,
    server_default=func.now()
)
    
    owner = relationship(
    "User",
    back_populates="posts"
    )
    
    votes = relationship(
    "Vote",
    back_populates="post",
    cascade="all, delete"
    )
    
    
    

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
    
    post = relationship(
    "Post",
    back_populates="votes"
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


    
