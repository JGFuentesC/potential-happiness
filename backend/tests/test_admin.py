from datetime import datetime, timedelta

from app.models import Match, Prediction, User, BonusPrediction
from app.auth import hash_password

FUTURE = datetime.utcnow() + timedelta(days=30)
PAST = datetime.utcnow() - timedelta(days=1)


def _make_match(db, **kwargs) -> Match:
    defaults = dict(home_team="USA", away_team="MEX", start_time=FUTURE, phase="Groups")
    defaults.update(kwargs)
    m = Match(**defaults)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


# ── Auth guard ────────────────────────────────────────────────────────────────

def test_admin_routes_blocked_for_non_admin(client, auth_headers):
    resp = client.get("/admin/users", headers=auth_headers)
    assert resp.status_code == 403


def test_admin_routes_blocked_without_token(client):
    resp = client.get("/admin/users")
    assert resp.status_code == 401


# ── User management ───────────────────────────────────────────────────────────

def test_list_users_all(client, db, admin_headers, active_user, pending_user):
    resp = client.get("/admin/users", headers=admin_headers)
    assert resp.status_code == 200
    usernames = {u["username"] for u in resp.json()}
    assert "testuser" in usernames
    assert "pendinguser" in usernames


def test_filter_users_by_status(client, db, admin_headers, pending_user):
    resp = client.get("/admin/users?status=Pending", headers=admin_headers)
    assert resp.status_code == 200
    statuses = {u["status"] for u in resp.json()}
    assert statuses == {"Pending"}


def test_approve_user(client, db, admin_headers, pending_user):
    resp = client.post(f"/admin/users/{pending_user.id}/approve", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "Active"
    db.refresh(pending_user)
    assert pending_user.status == "Active"


def test_reject_user(client, db, admin_headers, pending_user):
    resp = client.post(f"/admin/users/{pending_user.id}/reject", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "Rejected"


def test_approve_nonexistent_user(client, admin_headers):
    resp = client.post("/admin/users/9999/approve", headers=admin_headers)
    assert resp.status_code == 404


# ── Match management ──────────────────────────────────────────────────────────

def test_create_match(client, admin_headers):
    payload = {
        "home_team": "Spain", "away_team": "Germany",
        "home_team_code": "es", "away_team_code": "de",
        "start_time": "2026-06-15T18:00:00",
        "phase": "Groups", "group_name": "C", "matchday": 1,
    }
    resp = client.post("/admin/matches", json=payload, headers=admin_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["home_team"] == "Spain"
    assert data["status"] == "Open"


def test_update_match_assigns_teams(client, db, admin_headers):
    m = Match(home_team=None, away_team=None, home_team_placeholder="1° A",
              away_team_placeholder="2° B", start_time=FUTURE, phase="R32")
    db.add(m)
    db.commit()
    resp = client.put(f"/admin/matches/{m.id}",
                      json={"home_team": "Brazil", "away_team": "France",
                            "home_team_code": "br", "away_team_code": "fr"},
                      headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["home_team"] == "Brazil"
    assert resp.json()["status"] == "Open"  # teams assigned → Open


# ── Results & recalculation ───────────────────────────────────────────────────

def test_set_result_triggers_recalculation(client, db, admin_headers, active_user):
    m = _make_match(db)
    db.add(Prediction(user_id=active_user.id, match_id=m.id,
                      home_score_guess=2, away_score_guess=1))
    db.commit()

    resp = client.post(f"/admin/matches/{m.id}/result",
                       json={"home_score_final": 2, "away_score_final": 1},
                       headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["predictions_updated"] == 1
    assert data["home_score_final"] == 2

    db.refresh(active_user)
    assert active_user.total_points == 5  # exact score
    assert active_user.exact_scores == 1


def test_correct_result_recalculates(client, db, admin_headers, active_user):
    m = _make_match(db)
    db.add(Prediction(user_id=active_user.id, match_id=m.id,
                      home_score_guess=2, away_score_guess=1))
    db.commit()

    # First result: wrong tendency
    client.post(f"/admin/matches/{m.id}/result",
                json={"home_score_final": 0, "away_score_final": 1},
                headers=admin_headers)
    db.refresh(active_user)
    assert active_user.total_points == 0

    # Correct it
    resp = client.put(f"/admin/matches/{m.id}/result",
                      json={"home_score_final": 2, "away_score_final": 1},
                      headers=admin_headers)
    assert resp.status_code == 200
    db.refresh(active_user)
    assert active_user.total_points == 5


def test_set_result_marks_match_finished(client, db, admin_headers):
    m = _make_match(db)
    client.post(f"/admin/matches/{m.id}/result",
                json={"home_score_final": 1, "away_score_final": 0},
                headers=admin_headers)
    db.refresh(m)
    assert m.status == "Finished"


def test_result_404_for_unknown_match(client, admin_headers):
    resp = client.post("/admin/matches/9999/result",
                       json={"home_score_final": 1, "away_score_final": 0},
                       headers=admin_headers)
    assert resp.status_code == 404


# ── Bonus validation ──────────────────────────────────────────────────────────

def test_validate_bonus(client, db, admin_headers, active_user):
    bp = BonusPrediction(user_id=active_user.id, question_type="Champion",
                         prediction_text="Argentina")
    db.add(bp)
    db.commit()

    resp = client.post(
        f"/admin/bonus-predictions/{active_user.id}/Champion/validate",
        json={"points_earned": 20},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["points_earned"] == 20


def test_validate_bonus_404_if_not_predicted(client, admin_headers, active_user):
    resp = client.post(
        f"/admin/bonus-predictions/{active_user.id}/Champion/validate",
        json={"points_earned": 20},
        headers=admin_headers,
    )
    assert resp.status_code == 404
