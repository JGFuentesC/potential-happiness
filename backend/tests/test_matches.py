import os
from datetime import datetime, timedelta

import pytest

from app.models import Match


FUTURE = datetime.utcnow() + timedelta(days=30)
PAST = datetime.utcnow() - timedelta(days=1)


def _make_match(db, **kwargs) -> Match:
    defaults = dict(
        home_team="USA", away_team="MEX",
        home_team_code="us", away_team_code="mx",
        start_time=FUTURE, phase="Groups",
        group_name="A", matchday=1,
    )
    defaults.update(kwargs)
    m = Match(**defaults)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


# ── List matches ──────────────────────────────────────────────────────────────

def test_list_matches_requires_auth(client):
    resp = client.get("/matches")
    assert resp.status_code == 401


def test_list_matches_returns_all(client, db, auth_headers):
    _make_match(db, home_team="USA", away_team="MEX", group_name="A")
    _make_match(db, home_team="ARG", away_team="BRA", group_name="B")
    resp = client.get("/matches", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_list_matches_filter_by_phase(client, db, auth_headers):
    _make_match(db, phase="Groups", group_name="A")
    _make_match(db, phase="R32", group_name=None, matchday=None)
    resp = client.get("/matches?phase=Groups", headers=auth_headers)
    data = resp.json()
    assert len(data) == 1
    assert data[0]["phase"] == "Groups"


def test_list_matches_filter_by_group(client, db, auth_headers):
    _make_match(db, group_name="A")
    _make_match(db, group_name="B")
    resp = client.get("/matches?group_name=A", headers=auth_headers)
    data = resp.json()
    assert len(data) == 1
    assert data[0]["group_name"] == "A"


# ── Derived status ────────────────────────────────────────────────────────────

def test_match_status_open_when_far_future(client, db, auth_headers):
    _make_match(db, start_time=FUTURE)
    resp = client.get("/matches", headers=auth_headers)
    assert resp.json()[0]["status"] == "Open"


def test_match_status_locked_when_past_threshold(client, db, auth_headers):
    # start_time 5 min from now → within 15-min window → Locked
    soon = datetime.utcnow() + timedelta(minutes=5)
    _make_match(db, start_time=soon)
    resp = client.get("/matches", headers=auth_headers)
    assert resp.json()[0]["status"] == "Locked"


def test_match_status_finished(client, db, auth_headers):
    m = _make_match(db, start_time=PAST, status="Finished",
                    home_score_final=2, away_score_final=1)
    resp = client.get("/matches", headers=auth_headers)
    assert resp.json()[0]["status"] == "Finished"


def test_match_status_pending_teams_for_knockout(client, db, auth_headers):
    m = Match(
        home_team=None, away_team=None,
        home_team_placeholder="1° Grupo A",
        away_team_placeholder="2° Grupo B",
        start_time=FUTURE, phase="R32",
    )
    db.add(m)
    db.commit()
    resp = client.get("/matches", headers=auth_headers)
    assert resp.json()[0]["status"] == "Pending Teams"


# ── Time Travel ───────────────────────────────────────────────────────────────

def test_time_travel_makes_future_match_locked(client, db, auth_headers, monkeypatch):
    monkeypatch.setenv("ENABLE_TIME_TRAVEL", "True")
    start = datetime(2026, 6, 11, 20, 0)
    _make_match(db, start_time=start)
    # Simulated time: 10 min before start → within lock window
    sim = (start - timedelta(minutes=10)).isoformat()
    resp = client.get(f"/matches?simulated_time={sim}", headers=auth_headers)
    assert resp.json()[0]["status"] == "Locked"


def test_time_travel_disabled_ignores_param(client, db, auth_headers, monkeypatch):
    monkeypatch.setenv("ENABLE_TIME_TRAVEL", "False")
    _make_match(db, start_time=FUTURE)
    sim = "2020-01-01T00:00:00"
    resp = client.get(f"/matches?simulated_time={sim}", headers=auth_headers)
    assert resp.json()[0]["status"] == "Open"


# ── my_prediction embedded ────────────────────────────────────────────────────

def test_my_prediction_is_null_when_not_predicted(client, db, auth_headers):
    _make_match(db)
    resp = client.get("/matches", headers=auth_headers)
    assert resp.json()[0]["my_prediction"] is None


def test_my_prediction_is_included_when_predicted(client, db, auth_headers, active_user):
    from app.models import Prediction
    m = _make_match(db)
    db.add(Prediction(user_id=active_user.id, match_id=m.id,
                      home_score_guess=2, away_score_guess=1))
    db.commit()
    resp = client.get("/matches", headers=auth_headers)
    pred = resp.json()[0]["my_prediction"]
    assert pred is not None
    assert pred["home_score_guess"] == 2
    assert pred["away_score_guess"] == 1
