import time
from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import desc
from app import models, schemas
from app.database import engine, get_db
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

while True:
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="TestDatabase",
            user="postgres",
            password="1234",
            cursor_factory=RealDictCursor,
        )
        cursor = conn.cursor()
        print("Database connection was successfull")
        break
    except Exception as error:
        print("Connecting to database failed")
        print(f"Error: {error}")
        time.sleep(2)

@app.get("/")
def root():
    return {"message": "Hey"}

@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    print(posts)
    return {"data": posts}

@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data": posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data": new_post}

@app.get("/posts/orm_last_post")
def get_last_post_orm(db: Session = Depends(get_db)):
    last_post = db.query(models.Post).order_by(desc(models.Post.id)).first()
    return {"data": last_post}
    

@app.get("/posts/last_post")
def get_last_posts():
    cursor.execute("""select * from posts where created_at = (select max(created_at) from posts) limit 1""")
    post = cursor.fetchall()
    return {"data": post}

@app.get("/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    print(post)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} is not found",
        )
        
    return {"post_detail": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with {id} does not exist",
        )
    post.delete(synchronize_session = False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    updated_post = post_query.first()
    if updated_post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with {id} does not exist",
        )
    post_query.update(post.dict(), synchronize_session=False)
    db.commit()
    return {"data": post_query.first()}

@app.patch("/posts/{id}")
def update_post_title(id: int, post: schemas.PostBase):
    cursor.execute(
        """UPDATE posts SET title = %s WHERE id = %s RETURNING *""",
        (
            post.title,
            str(id),
        ),
    )
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} does not exist",
        )
    return {"data": updated_post}

