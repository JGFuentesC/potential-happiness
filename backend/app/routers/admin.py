from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Match, User, BonusPrediction
from app.auth import requires_admin
from app.schemas import (
    AdminUserOut, MatchCreate, MatchOut, MatchResult, MatchUpdate,
    ResultResponse, BonusValidate, BonusPredictionOut,
)
from app.scoring import recalculate_match_predictions
from app.time_utils import compute_match_status, get_reference_time

router = APIRouter()


# ── Users ─────────────────────────────────────────────────────────────────────

@router.get("/users", response_model=list[AdminUserOut])
def list_users(
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(requires_admin),
) -> list[User]:
    q = db.query(User)
    if status:
        q = q.filter(User.status == status)
    return q.order_by(User.created_at.desc()).all()


@router.post("/users/{user_id}/approve", response_model=AdminUserOut)
def approve_user(user_id: int, db: Session = Depends(get_db), _: User = Depends(requires_admin)) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.status = "Active"
    db.commit()
    db.refresh(user)
    return user


@router.post("/users/{user_id}/reject", response_model=AdminUserOut)
def reject_user(user_id: int, db: Session = Depends(get_db), _: User = Depends(requires_admin)) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.status = "Rejected"
    db.commit()
    db.refresh(user)
    return user


# ── Matches ───────────────────────────────────────────────────────────────────

@router.post("/matches", response_model=MatchOut, status_code=status.HTTP_201_CREATED)
def create_match(
    body: MatchCreate,
    db: Session = Depends(get_db),
    _: User = Depends(requires_admin),
) -> dict:
    match = Match(**body.model_dump())
    db.add(match)
    db.commit()
    db.refresh(match)
    return _match_to_out(match, get_reference_time())


@router.put("/matches/{match_id}", response_model=MatchOut)
def update_match(
    match_id: int,
    body: MatchUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(requires_admin),
) -> dict:
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(match, field, value)
    db.commit()
    db.refresh(match)
    return _match_to_out(match, get_reference_time())


@router.post("/matches/{match_id}/result", response_model=ResultResponse)
def set_result(
    match_id: int,
    body: MatchResult,
    db: Session = Depends(get_db),
    _: User = Depends(requires_admin),
) -> dict:
    return _apply_result(match_id, body, db)


@router.put("/matches/{match_id}/result", response_model=ResultResponse)
def correct_result(
    match_id: int,
    body: MatchResult,
    db: Session = Depends(get_db),
    _: User = Depends(requires_admin),
) -> dict:
    return _apply_result(match_id, body, db)


def _apply_result(match_id: int, body: MatchResult, db: Session) -> dict:
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    match.home_score_final = body.home_score_final
    match.away_score_final = body.away_score_final
    match.status = "Finished"
    db.flush()
    count = recalculate_match_predictions(db, match_id, body.home_score_final, body.away_score_final)
    db.commit()
    return {
        "match_id": match_id,
        "home_score_final": body.home_score_final,
        "away_score_final": body.away_score_final,
        "predictions_updated": count,
    }


# ── Bonus ─────────────────────────────────────────────────────────────────────

@router.post("/bonus-predictions/{user_id}/{question_type}/validate", response_model=BonusPredictionOut)
def validate_bonus(
    user_id: int,
    question_type: str,
    body: BonusValidate,
    db: Session = Depends(get_db),
    _: User = Depends(requires_admin),
) -> BonusPrediction:
    bp = (
        db.query(BonusPrediction)
        .filter(BonusPrediction.user_id == user_id, BonusPrediction.question_type == question_type)
        .first()
    )
    if not bp:
        raise HTTPException(status_code=404, detail="Bonus prediction not found")
    bp.points_earned = body.points_earned
    db.commit()
    db.refresh(bp)
    return bp


# ── Helpers ───────────────────────────────────────────────────────────────────

def _match_to_out(match: Match, ref_time) -> dict:
    computed = compute_match_status(
        match.status, match.start_time, match.home_team, match.away_team,
        match.home_team_placeholder, match.away_team_placeholder, ref_time,
    )
    return {
        "id": match.id,
        "home_team": match.home_team,
        "away_team": match.away_team,
        "home_team_code": match.home_team_code,
        "away_team_code": match.away_team_code,
        "home_team_placeholder": match.home_team_placeholder,
        "away_team_placeholder": match.away_team_placeholder,
        "start_time": match.start_time,
        "phase": match.phase,
        "group_name": match.group_name,
        "matchday": match.matchday,
        "venue": match.venue,
        "status": computed,
        "home_score_final": match.home_score_final,
        "away_score_final": match.away_score_final,
        "my_prediction": None,
    }
