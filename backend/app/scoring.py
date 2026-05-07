from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Prediction, User


def calculate_prediction_points(
    home_guess: int,
    away_guess: int,
    home_final: int,
    away_final: int,
) -> int:
    def tendency(h: int, a: int) -> str:
        if h > a:
            return "home"
        if h < a:
            return "away"
        return "draw"

    if tendency(home_guess, away_guess) != tendency(home_final, away_final):
        return 0

    points = 3
    if home_guess == home_final and away_guess == away_final:
        points += 2
    return points


def recalculate_match_predictions(db: Session, match_id: int, home_final: int, away_final: int) -> int:
    predictions = db.query(Prediction).filter(Prediction.match_id == match_id).all()
    affected_users: set[int] = set()

    for pred in predictions:
        pred.points_earned = calculate_prediction_points(
            pred.home_score_guess, pred.away_score_guess, home_final, away_final
        )
        affected_users.add(pred.user_id)

    db.flush()

    for user_id in affected_users:
        recalculate_user_totals(db, user_id)

    return len(predictions)


def recalculate_user_totals(db: Session, user_id: int) -> None:
    result = (
        db.query(
            func.coalesce(func.sum(Prediction.points_earned), 0),
            func.count(Prediction.id).filter(Prediction.points_earned == 5),
        )
        .filter(Prediction.user_id == user_id, Prediction.points_earned.isnot(None))
        .one()
    )
    total_points, exact_scores = result
    db.query(User).filter(User.id == user_id).update(
        {"total_points": total_points, "exact_scores": exact_scores}
    )
