from datetime import datetime, timedelta

from app.models import Match, BonusPrediction


def _add_match(db, start_time: datetime) -> Match:
    m = Match(home_team="USA", away_team="MEX", start_time=start_time, phase="Groups")
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


# ── GET /bonus-questions ──────────────────────────────────────────────────────

def test_list_bonus_questions(client, auth_headers):
    resp = client.get("/bonus-questions", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    types = {q["question_type"] for q in data}
    assert "Champion" in types
    assert "TopScorer" in types


def test_bonus_not_locked_before_kickoff(client, db, auth_headers):
    _add_match(db, start_time=datetime.utcnow() + timedelta(hours=2))
    resp = client.get("/bonus-questions", headers=auth_headers)
    assert all(q["is_locked"] is False for q in resp.json())


def test_bonus_locked_after_kickoff(client, db, auth_headers, monkeypatch):
    monkeypatch.setenv("ENABLE_TIME_TRAVEL", "True")
    kickoff = datetime(2026, 6, 11, 20, 0)
    _add_match(db, start_time=kickoff)
    # Fetch with simulated_time after kickoff — bonus questions endpoint doesn't
    # accept simulated_time, so we fake "now" by setting env var trick.
    # Instead, use a past kickoff to trigger real lock.
    pass  # covered by test below


def test_bonus_locked_when_first_match_in_past(client, db, auth_headers):
    _add_match(db, start_time=datetime.utcnow() - timedelta(minutes=1))
    resp = client.get("/bonus-questions", headers=auth_headers)
    assert all(q["is_locked"] is True for q in resp.json())


def test_my_prediction_shown_in_bonus_questions(client, db, auth_headers, active_user):
    _add_match(db, start_time=datetime.utcnow() + timedelta(days=10))
    db.add(BonusPrediction(user_id=active_user.id, question_type="Champion",
                           prediction_text="Argentina"))
    db.commit()
    resp = client.get("/bonus-questions", headers=auth_headers)
    champion = next(q for q in resp.json() if q["question_type"] == "Champion")
    assert champion["my_prediction"] == "Argentina"


# ── POST /bonus-predictions ───────────────────────────────────────────────────

def test_save_bonus_prediction(client, db, auth_headers):
    _add_match(db, start_time=datetime.utcnow() + timedelta(days=10))
    resp = client.post("/bonus-predictions",
                       json={"question_type": "Champion", "prediction_text": "France"},
                       headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["prediction_text"] == "France"


def test_bonus_prediction_upsert(client, db, auth_headers):
    _add_match(db, start_time=datetime.utcnow() + timedelta(days=10))
    client.post("/bonus-predictions",
                json={"question_type": "Champion", "prediction_text": "France"},
                headers=auth_headers)
    resp = client.post("/bonus-predictions",
                       json={"question_type": "Champion", "prediction_text": "Brazil"},
                       headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["prediction_text"] == "Brazil"


def test_bonus_blocked_after_kickoff(client, db, auth_headers):
    _add_match(db, start_time=datetime.utcnow() - timedelta(minutes=1))
    resp = client.post("/bonus-predictions",
                       json={"question_type": "Champion", "prediction_text": "Germany"},
                       headers=auth_headers)
    assert resp.status_code == 403
    assert "locked" in resp.json()["detail"].lower()


def test_bonus_invalid_question_type(client, db, auth_headers):
    _add_match(db, start_time=datetime.utcnow() + timedelta(days=10))
    resp = client.post("/bonus-predictions",
                       json={"question_type": "InvalidType", "prediction_text": "X"},
                       headers=auth_headers)
    assert resp.status_code == 400
