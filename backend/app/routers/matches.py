from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Match, Prediction, User
from app.auth import get_current_user
from app.schemas import MatchOut, PredictionInMatch
from app.time_utils import get_reference_time, compute_match_status

router = APIRouter()


def _build_match_out(match: Match, ref_time, my_pred: Optional[Prediction]) -> dict:
    computed_status = compute_match_status(
        match.status,
        match.start_time,
        match.home_team,
        match.away_team,
        match.home_team_placeholder,
        match.away_team_placeholder,
        ref_time,
    )
    my_prediction = None
    if my_pred:
        my_prediction = PredictionInMatch(
            home_score_guess=my_pred.home_score_guess,
            away_score_guess=my_pred.away_score_guess,
            points_earned=my_pred.points_earned,
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
        "status": computed_status,
        "home_score_final": match.home_score_final,
        "away_score_final": match.away_score_final,
        "my_prediction": my_prediction,
    }


@router.get("", response_model=list[MatchOut])
def list_matches(
    phase: Optional[str] = Query(None),
    group_name: Optional[str] = Query(None),
    simulated_time: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    ref_time = get_reference_time(simulated_time)
    query = db.query(Match)
    if phase:
        query = query.filter(Match.phase == phase)
    if group_name:
        query = query.filter(Match.group_name == group_name)
    matches = query.order_by(Match.start_time.asc()).all()

    result = []
    for m in matches:
        pred = (
            db.query(Prediction)
            .filter(Prediction.match_id == m.id, Prediction.user_id == current_user.id)
            .first()
        )
        result.append(_build_match_out(m, ref_time, pred))
    return result


@router.get("/{match_id}", response_model=MatchOut)
def get_match(
    match_id: int,
    simulated_time: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    from fastapi import HTTPException
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    ref_time = get_reference_time(simulated_time)
    pred = (
        db.query(Prediction)
        .filter(Prediction.match_id == match_id, Prediction.user_id == current_user.id)
        .first()
    )
    return _build_match_out(match, ref_time, pred)
