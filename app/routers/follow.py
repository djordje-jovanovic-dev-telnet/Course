from typing import Optional, List
from fastapi import Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from ..database import engine, get_db
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

router = APIRouter(prefix="/follow", tags=["Follow"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def follow(
    follow: schemas.Follow,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    user = (
        db.query(models.User).filter(models.User.id == follow.followed_user_id).first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist"
        )
    if current_user.id == follow.followed_user_id:
        if follow.dir == 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User can not follow himself",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User can not unfollow himself",
            )
    follow_query = db.query(models.Follow).filter(
        models.Follow.follow_user_id == follow.followed_user_id,
        models.Follow.user_id == current_user.id,
    )
    found_follow = follow_query.first()

    if follow.dir == 1:
        if found_follow:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User has been already followed",
            )
        new_follow = models.Follow(
            user_id=current_user.id, follow_user_id=follow.followed_user_id
        )
        db.add(new_follow)
        db.commit()
        return {"message": "Successfully followed user"}
    else:
        if not found_follow:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User is already unfollowed",
            )
        follow_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "Successfully unfollowed user"}
