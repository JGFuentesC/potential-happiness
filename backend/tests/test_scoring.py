import pytest
from app.scoring import calculate_prediction_points, recalculate_match_predictions, recalculate_user_totals
from app.models import User, Match, Prediction
from app.auth import hash_password
from datetime import datetime


# ── calculate_prediction_points (pure function, no DB) ───────────────────────

@pytest.mark.parametrize("hg,ag,hf,af,expected", [
    # Tendencia correcta: local gana → +3
    (2, 0, 1, 0, 3),
    # Tendencia correcta: visitante gana → +3
    (0, 1, 0, 2, 3),
    # Tendencia correcta: empate → +3
    (1, 1, 2, 2, 3),
    # Marcador exacto: local gana → +5
    (2, 1, 2, 1, 5),
    # Marcador exacto: visitante gana → +5
    (0, 3, 0, 3, 5),
    # Marcador exacto: empate → +5
    (1, 1, 1, 1, 5),
    # Tendencia incorrecta: predijo local, empató → 0
    (2, 0, 1, 1, 0),
    # Tendencia incorrecta: predijo empate, ganó local → 0
    (1, 1, 2, 0, 0),
    # Tendencia incorrecta: predijo visitante, ganó local → 0
    (0, 2, 3, 1, 0),
    # Goleada: acierto tendencia pero no exacto → +3
    (3, 0, 4, 0, 3),
])
def test_calculate_points(hg, ag, hf, af, expected):
    assert calculate_prediction_points(hg, ag, hf, af) == expected


# ── recalculate_match_predictions ─────────────────────────────────────────────

def _make_user(db, username: str) -> User:
    u = User(username=username, password_hash=hash_password("x"), status="Active")
    db.add(u)
    db.flush()
    return u


def _make_match(db) -> Match:
    m = Match(
        home_team="USA", away_team="MEX",
        start_time=datetime(2026, 6, 11, 20, 0),
        phase="Groups",
    )
    db.add(m)
    db.flush()
    return m


def test_recalculate_match_updates_points(db):
    u1 = _make_user(db, "u1")
    u2 = _make_user(db, "u2")
    match = _make_match(db)

    db.add(Prediction(user_id=u1.id, match_id=match.id, home_score_guess=2, away_score_guess=1))
    db.add(Prediction(user_id=u2.id, match_id=match.id, home_score_guess=0, away_score_guess=1))
    db.commit()

    count = recalculate_match_predictions(db, match.id, 2, 1)
    db.commit()

    assert count == 2
    db.refresh(u1)
    db.refresh(u2)
    assert u1.total_points == 5   # exact score
    assert u2.total_points == 0   # wrong tendency


def test_recalculate_updates_exact_scores_count(db):
    u = _make_user(db, "u1")
    m1 = _make_match(db)
    m2 = Match(
        home_team="ARG", away_team="BRA",
        start_time=datetime(2026, 6, 12, 20, 0), phase="Groups",
    )
    db.add(m2)
    db.flush()

    db.add(Prediction(user_id=u.id, match_id=m1.id, home_score_guess=1, away_score_guess=0))
    db.add(Prediction(user_id=u.id, match_id=m2.id, home_score_guess=2, away_score_guess=2))
    db.commit()

    recalculate_match_predictions(db, m1.id, 1, 0)   # exact: +5
    recalculate_match_predictions(db, m2.id, 2, 2)   # exact: +5
    db.commit()
    db.refresh(u)

    assert u.total_points == 10
    assert u.exact_scores == 2


def test_recalculate_after_correction(db):
    u = _make_user(db, "u1")
    match = _make_match(db)
    db.add(Prediction(user_id=u.id, match_id=match.id, home_score_guess=2, away_score_guess=1))
    db.commit()

    # First result: wrong tendency → 0 pts
    recalculate_match_predictions(db, match.id, 0, 1)
    db.commit()
    db.refresh(u)
    assert u.total_points == 0

    # Admin corrects result → exact score → 5 pts
    recalculate_match_predictions(db, match.id, 2, 1)
    db.commit()
    db.refresh(u)
    assert u.total_points == 5
    assert u.exact_scores == 1
