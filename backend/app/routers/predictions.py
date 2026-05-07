from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Match, Prediction, User
from app.auth import get_current_user
from app.schemas import PredictionCreate, PredictionOut, FriendPrediction
from app.time_utils import get_reference_time, compute_match_status

router = APIRouter()


@router.post("", response_model=PredictionOut)
def upsert_prediction(
    body: PredictionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Prediction:
    match = db.query(Match).filter(Match.id == body.match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    ref_time = get_reference_time(body.simulated_time)
    computed = compute_match_status(
        match.status, match.start_time, match.home_team, match.away_team,
        match.home_team_placeholder, match.away_team_placeholder, ref_time,
    )
    if computed != "Open":
        raise HTTPException(status_code=403, detail="Match is locked. Predictions closed.")

    pred = (
        db.query(Prediction)
        .filter(Prediction.match_id == body.match_id, Prediction.user_id == current_user.id)
        .first()
    )
    if pred:
        pred.home_score_guess = body.home_score_guess
        pred.away_score_guess = body.away_score_guess
        pred.updated_at = datetime.utcnow()
    else:
        pred = Prediction(
            user_id=current_user.id,
            match_id=body.match_id,
            home_score_guess=body.home_score_guess,
            away_score_guess=body.away_score_guess,
        )
        db.add(pred)
    db.commit()
    db.refresh(pred)
    return pred


@router.get("/match/{match_id}", response_model=list[FriendPrediction])
def get_match_predictions(
    match_id: int,
    simulated_time: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    ref_time = get_reference_time(simulated_time)
    computed = compute_match_status(
        match.status, match.start_time, match.home_team, match.away_team,
        match.home_team_placeholder, match.away_team_placeholder, ref_time,
    )
    if computed not in ("Locked", "Finished"):
        raise HTTPException(
            status_code=403,
            detail="Predictions are only visible after the match is locked.",
        )

    preds = (
        db.query(Prediction)
        .join(User, Prediction.user_id == User.id)
        .filter(Prediction.match_id == match_id)
        .all()
    )
    return [
        {
            "username": p.user.username,
            "home_score_guess": p.home_score_guess,
            "away_score_guess": p.away_score_guess,
            "points_earned": p.points_earned,
        }
        for p in preds
    ]
