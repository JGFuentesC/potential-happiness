from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.auth import get_current_user
from app.schemas import UserMe, RankingEntry

router = APIRouter()


def _compute_rank(db: Session, user_id: int) -> int:
    users = (
        db.query(User)
        .filter(User.status == "Active")
        .order_by(User.total_points.desc(), User.exact_scores.desc(), User.username.asc())
        .all()
    )
    for i, u in enumerate(users, start=1):
        if u.id == user_id:
            return i
    return -1


@router.get("/me", response_model=UserMe)
def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    rank = _compute_rank(db, current_user.id)
    return {
        "id": current_user.id,
        "username": current_user.username,
        "is_admin": bool(current_user.is_admin),
        "status": current_user.status,
        "total_points": current_user.total_points,
        "exact_scores": current_user.exact_scores,
        "rank": rank,
    }


@router.get("/ranking", response_model=list[RankingEntry])
def ranking(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[dict]:
    users = (
        db.query(User)
        .filter(User.status == "Active")
        .order_by(User.total_points.desc(), User.exact_scores.desc(), User.username.asc())
        .all()
    )
    return [
        {
            "rank": i,
            "user_id": u.id,
            "username": u.username,
            "total_points": u.total_points,
            "exact_scores": u.exact_scores,
        }
        for i, u in enumerate(users, start=1)
    ]
