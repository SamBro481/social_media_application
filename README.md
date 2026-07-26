# Social Media Backend API

A REST API built with FastAPI that supports user authentication, posts, voting, following users, and a personalized feed. The project uses PostgreSQL for persistent storage, Redis for caching, JWT for authentication, and Docker for containerized deployment.

## Tech Stack

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Redis
- JWT Authentication
- Docker

## Live API

Swagger Documentation:
https://social-media-application-snc3.onrender.com/docs

Health Check:
https://social-media-application-snc3.onrender.com/health

## Features

- User registration and login
- JWT authentication
- CRUD operations for posts
- Vote on posts
- Follow and unfollow users
- Personalized feed
- Pagination
- Redis caching
- Database migrations with Alembic
- Dockerized deployment

## Running Locally

Clone the repository:

```bash
git clone https://github.com/SamBro481/social_media_application.git
cd social_media_application
```

Create a `.env` file with the required environment variables.

Run with Docker:

```bash
docker compose up --build
```

API will be available at:

```
http://localhost:8000/docs
```

## Environment Variables

```
DATABASE_URL=
SECRET_KEY=
ALGORITHM=
ACCESS_TOKEN_EXPIRE_MINUTES=
REDIS_URL=
```

## Project Structure

```
app/
├── routers/
├── models.py
├── schemas.py
├── oauth2.py
├── database.py
├── redis_client.py
├── utils.py
└── main.py

alembic/
Dockerfile
docker-compose.yml
requirements.txt
```

## API Endpoints

Authentication

- POST /login

Users

- POST /users

Posts

- GET /posts
- GET /posts/{id}
- POST /posts
- PUT /posts/{id}
- DELETE /posts/{id}

Votes

- POST /vote

Follow

- POST /follow
- DELETE /follow/{user_id}

Feed

- GET /feed

## Deployment

- Hosted on Render
- PostgreSQL hosted on Neon
- Redis hosted on Upstash

## License

This project is for learning and portfolio purposes.
