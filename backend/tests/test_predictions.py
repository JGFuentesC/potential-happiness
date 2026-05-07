from datetime import datetime, timedelta

from app.models import Match, Prediction


FUTURE = datetime.utcnow() + timedelta(days=30)
PAST = datetime.utcnow() - timedelta(days=1)
LOCKED_SOON = datetime.utcnow() + timedelta(minutes=5)  # within 15-min lock window


def _match(db, start_time=FUTURE, status="Scheduled", home="USA", away="MEX") -> Match:
    m = Match(home_team=home, away_team=away, start_time=start_time,
              phase="Groups", group_name="A", matchday=1, status=status)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


# ── POST /predictions ─────────────────────────────────────────────────────────

def test_create_prediction_open_match(client, db, auth_headers):
    m = _match(db)
    resp = client.post("/predictions", json={"match_id": m.id, "home_score_guess": 2, "away_score_guess": 1},
                       headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["home_score_guess"] == 2
    assert data["away_score_guess"] == 1
    assert data["points_earned"] is None


def test_prediction_upsert_updates_existing(client, db, auth_headers):
    m = _match(db)
    client.post("/predictions", json={"match_id": m.id, "home_score_guess": 1, "away_score_guess": 0},
                headers=auth_headers)
    # Update same match
    resp = client.post("/predictions", json={"match_id": m.id, "home_score_guess": 3, "away_score_guess": 2},
                       headers=auth_headers)
    assert resp.status_code == 200
    # Only one prediction in DB
    count = db.query(Prediction).filter(Prediction.match_id == m.id).count()
    assert count == 1
    assert resp.json()["home_score_guess"] == 3


def test_prediction_blocked_when_locked(client, db, auth_headers):
    m = _match(db, start_time=LOCKED_SOON)
    resp = client.post("/predictions", json={"match_id": m.id, "home_score_guess": 1, "away_score_guess": 0},
                       headers=auth_headers)
    assert resp.status_code == 403
    assert "locked" in resp.json()["detail"].lower()


def test_prediction_blocked_when_finished(client, db, auth_headers):
    m = _match(db, start_time=PAST, status="Finished")
    resp = client.post("/predictions", json={"match_id": m.id, "home_score_guess": 1, "away_score_guess": 0},
                       headers=auth_headers)
    assert resp.status_code == 403


def test_prediction_blocked_when_pending_teams(client, db, auth_headers):
    m = Match(home_team=None, away_team=None, home_team_placeholder="1° A",
              away_team_placeholder="2° B", start_time=FUTURE, phase="R32")
    db.add(m)
    db.commit()
    resp = client.post("/predictions", json={"match_id": m.id, "home_score_guess": 1, "away_score_guess": 0},
                       headers=auth_headers)
    assert resp.status_code == 403


def test_prediction_404_for_unknown_match(client, db, auth_headers):
    resp = client.post("/predictions", json={"match_id": 9999, "home_score_guess": 1, "away_score_guess": 0},
                       headers=auth_headers)
    assert resp.status_code == 404


def test_time_travel_allows_prediction_before_lock(client, db, auth_headers, monkeypatch):
    monkeypatch.setenv("ENABLE_TIME_TRAVEL", "True")
    start = datetime(2026, 6, 11, 20, 0)
    m = _match(db, start_time=start)
    # 30 min before start → Open
    sim = (start - timedelta(minutes=30)).isoformat()
    resp = client.post("/predictions",
                       json={"match_id": m.id, "home_score_guess": 1, "away_score_guess": 0,
                             "simulated_time": sim},
                       headers=auth_headers)
    assert resp.status_code == 200


def test_time_travel_blocks_prediction_after_lock(client, db, auth_headers, monkeypatch):
    monkeypatch.setenv("ENABLE_TIME_TRAVEL", "True")
    start = datetime(2026, 6, 11, 20, 0)
    m = _match(db, start_time=start)
    # 5 min before start → Locked
    sim = (start - timedelta(minutes=5)).isoformat()
    resp = client.post("/predictions",
                       json={"match_id": m.id, "home_score_guess": 1, "away_score_guess": 0,
                             "simulated_time": sim},
                       headers=auth_headers)
    assert resp.status_code == 403


# ── GET /predictions/match/{id} ───────────────────────────────────────────────

def test_get_predictions_blocked_when_open(client, db, auth_headers):
    m = _match(db, start_time=FUTURE)
    resp = client.get(f"/predictions/match/{m.id}", headers=auth_headers)
    assert resp.status_code == 403
    assert "locked" in resp.json()["detail"].lower()


def test_get_predictions_visible_when_locked(client, db, auth_headers, active_user):
    m = _match(db, start_time=LOCKED_SOON)
    db.add(Prediction(user_id=active_user.id, match_id=m.id,
                      home_score_guess=2, away_score_guess=1))
    db.commit()
    resp = client.get(f"/predictions/match/{m.id}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["username"] == "testuser"
    assert data[0]["home_score_guess"] == 2


def test_get_predictions_visible_when_finished(client, db, auth_headers, active_user):
    m = _match(db, start_time=PAST, status="Finished")
    db.add(Prediction(user_id=active_user.id, match_id=m.id,
                      home_score_guess=1, away_score_guess=0, points_earned=3))
    db.commit()
    resp = client.get(f"/predictions/match/{m.id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()[0]["points_earned"] == 3


def test_get_predictions_returns_empty_list_when_no_predictions(client, db, auth_headers):
    m = _match(db, start_time=LOCKED_SOON)
    resp = client.get(f"/predictions/match/{m.id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []
