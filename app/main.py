from fastapi import FastAPI

from . import database
from . import models

from app.routers import users
from app.routers import auth
from app.routers import posts
from app.routers import vote
from app.routers import follow
from app.routers import feed
from app.routers import root

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()
app.include_router(root.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(vote.router)
app.include_router(follow.router)
app.include_router(feed.router)


