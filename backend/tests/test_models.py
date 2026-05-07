from datetime import datetime
from sqlalchemy.exc import IntegrityError
import pytest

from app.models import User, Match, Prediction, BonusPrediction
from app.auth import hash_password


def test_create_user(db):
    user = User(username="gus", password_hash=hash_password("secret"), status="Active")
    db.add(user)
    db.commit()
    db.refresh(user)
    assert user.id is not None
    assert user.total_points == 0
    assert user.exact_scores == 0
    assert user.is_admin == 0


def test_username_unique_constraint(db):
    db.add(User(username="gus", password_hash="x", status="Active"))
    db.commit()
    db.add(User(username="gus", password_hash="y", status="Active"))
    with pytest.raises(IntegrityError):
        db.commit()


def test_create_match(db):
    match = Match(
        home_team="USA",
        away_team="Mexico",
        home_team_code="us",
        away_team_code="mx",
        start_time=datetime(2026, 6, 11, 20, 0),
        phase="Groups",
        group_name="A",
        matchday=1,
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    assert match.id is not None
    assert match.status == "Scheduled"
    assert match.home_score_final is None


def test_match_nullable_teams_for_knockout(db):
    match = Match(
        home_team=None,
        away_team=None,
        home_team_placeholder="1° Grupo A",
        away_team_placeholder="2° Grupo B",
        start_time=datetime(2026, 7, 2, 20, 0),
        phase="R32",
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    assert match.home_team is None
    assert match.home_team_placeholder == "1° Grupo A"


def test_prediction_unique_constraint(db):
    user = User(username="gus", password_hash="x", status="Active")
    match = Match(
        home_team="USA", away_team="MEX",
        start_time=datetime(2026, 6, 11, 20, 0), phase="Groups",
    )
    db.add_all([user, match])
    db.commit()

    db.add(Prediction(user_id=user.id, match_id=match.id, home_score_guess=1, away_score_guess=0))
    db.commit()
    db.add(Prediction(user_id=user.id, match_id=match.id, home_score_guess=2, away_score_guess=1))
    with pytest.raises(IntegrityError):
        db.commit()


def test_bonus_prediction_unique_constraint(db):
    user = User(username="gus", password_hash="x", status="Active")
    db.add(user)
    db.commit()
    db.add(BonusPrediction(user_id=user.id, question_type="Champion", prediction_text="Argentina"))
    db.commit()
    db.add(BonusPrediction(user_id=user.id, question_type="Champion", prediction_text="France"))
    with pytest.raises(IntegrityError):
        db.commit()
