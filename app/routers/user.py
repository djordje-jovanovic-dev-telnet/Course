from typing import List
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy import func, text, or_
from .. import models, schemas, utils
from ..database import get_db
from sqlalchemy.orm import Session
import sys


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/{id}", response_model=schemas.UserFollow)
def get_user_details(id: int, db: Session = Depends(get_db)):
    user = (
        db.query(models.User.id, models.User.email).filter(models.User.id == id).first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    following_data = (
        db.query(models.User)
        .join(models.Follow, models.Follow.follow_user_id == models.User.id)
        .filter(models.Follow.follow_user_id != id, models.Follow.user_id == id)
        .all()
    )

    followers_data = (
        db.query(models.User)
        .join(models.Follow, models.Follow.user_id == models.User.id)
        .filter(models.Follow.user_id != id, models.Follow.follow_user_id == id)
        .all()
    )

    following_count_data = (
        db.query(func.count())
        .filter(
            models.Follow.user_id == id,
            models.Follow.follow_user_id != id,
        )
        .scalar()
    )

    followers_count_data = (
        db.query(func.count())
        .filter(
            models.Follow.user_id != id,
            models.Follow.follow_user_id == id,
        )
        .scalar()
    )

    user_data = schemas.UserFollow(
        id=user.id,
        email=user.email,
        following_count=following_count_data,
        followers_count=followers_count_data,
        following=following_data,
        followers=followers_data,
    )
    return user_data


@router.get("/", response_model=List[schemas.UserOut])
def get_all_users(db: Session = Depends(get_db)):
    users = (
        db.query(
            models.User.id,
            models.User.email,
            func.count()
            .filter(
                models.Follow.user_id != models.User.id,
                models.Follow.follow_user_id == models.User.id,
            )
            .label("followers"),
            func.count()
            .filter(
                models.Follow.user_id == models.User.id,
                models.Follow.follow_user_id != models.User.id,
            )
            .label("following"),
        )
        .join(
            models.Follow,
            or_(
                models.Follow.user_id == models.User.id,
                models.Follow.follow_user_id == models.User.id,
            ),
            isouter=True,
        )
        .group_by(models.User.id, models.User.email)
        .all()
    )

    return users
