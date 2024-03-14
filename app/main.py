from fastapi import FastAPI, Depends
from app import models
from app.database import engine, get_db
from sqlalchemy.orm import Session
from .routers import post, user, auth, vote
from .config import settings


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)


@app.get("/")
def root():
    return {"message": "Hey"}


@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    print(posts)
    return {posts}
