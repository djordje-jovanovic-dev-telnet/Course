from typing import Optional, List
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from random import randrange
from sqlalchemy import desc
from app import oauth2
from ..import models, schemas, utils
from ..database import engine, get_db
from sqlalchemy.orm import Session, Query
from sqlalchemy import or_, func

router = APIRouter(
    prefix = "/posts",
    tags = ['Posts']
)

@router.get("/", response_model=List[schemas.Post])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    posts = db.query(models.Post).all()
    return posts

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

#updated with subquery  
@router.get("/get_last_post")
def get_last_post(db: Session = Depends(get_db)):
    subquery = db.query(func.max(models.Post.id)).scalar_subquery()
    last_post = db.query(models.Post).filter(models.Post.id == subquery).first()
    return last_post

@router.get("/condition/{id}")
def get_with_condition(id: int, db: Session = Depends(get_db)):
    
    post = db.query(func.concat(models.Post.content," ",models.Post.id).label("Novo")).filter(models.Post.id > id).limit(2).all()    
    return post

@router.get("/{id}", response_model=schemas.Post)
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    print(post)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} is not found",
        )     
    return post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), user_id: int = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with {id} does not exist",
        )
    post.delete(synchronize_session = False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, post: schemas.PostBase, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    updated_post = post_query.first()
    if updated_post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with {id} does not exist",
        )
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    return post_query.first()

@router.patch("/{id}", response_model=schemas.Post)
def update_post_title(id: int, post: schemas.PostPatch, db: Session = Depends(get_db)):
    patch_query = db.query(models.Post).filter(models.Post.id == id)
    updated_post = patch_query.first()
    if updated_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} does not exist",
        )
    patch_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    return patch_query.first()