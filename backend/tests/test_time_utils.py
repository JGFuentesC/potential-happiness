import os
from datetime import datetime, timedelta

import pytest

from app.time_utils import (
    compute_match_status,
    get_reference_time,
    is_bonus_locked,
    is_prediction_allowed,
)

# ── get_reference_time ────────────────────────────────────────────────────────

def test_get_reference_time_returns_now_by_default(monkeypatch):
    monkeypatch.delenv("ENABLE_TIME_TRAVEL", raising=False)
    ref = get_reference_time()
    assert abs((ref - datetime.utcnow()).total_seconds()) < 2


def test_get_reference_time_ignores_simulated_when_flag_off(monkeypatch):
    monkeypatch.setenv("ENABLE_TIME_TRAVEL", "False")
    ref = get_reference_time("2020-01-01T00:00:00")
    assert ref.year != 2020


def test_get_reference_time_uses_simulated_when_flag_on(monkeypatch):
    monkeypatch.setenv("ENABLE_TIME_TRAVEL", "True")
    ref = get_reference_time("2020-06-15T10:30:00")
    assert ref == datetime(2020, 6, 15, 10, 30, 0)


# ── compute_match_status ──────────────────────────────────────────────────────

START = datetime(2026, 6, 11, 20, 0)


def test_status_finished():
    assert compute_match_status("Finished", START, "USA", "MEX", None, None, datetime.utcnow()) == "Finished"


def test_status_pending_teams_when_no_teams():
    ref = START - timedelta(hours=2)
    status = compute_match_status("Scheduled", START, None, None, "1° A", "2° B", ref)
    assert status == "Pending Teams"


def test_status_open_before_lock_window():
    ref = START - timedelta(minutes=20)
    status = compute_match_status("Scheduled", START, "USA", "MEX", None, None, ref)
    assert status == "Open"


def test_status_locked_at_lock_threshold():
    ref = START - timedelta(minutes=15)
    status = compute_match_status("Scheduled", START, "USA", "MEX", None, None, ref)
    assert status == "Locked"


def test_status_locked_after_lock_threshold():
    ref = START + timedelta(minutes=30)
    status = compute_match_status("Scheduled", START, "USA", "MEX", None, None, ref)
    assert status == "Locked"


def test_status_finished_overrides_time():
    # Even if ref_time is before lock, Finished wins
    ref = START - timedelta(days=1)
    status = compute_match_status("Finished", START, "USA", "MEX", None, None, ref)
    assert status == "Finished"


# ── is_prediction_allowed ─────────────────────────────────────────────────────

def test_prediction_allowed_when_open():
    ref = START - timedelta(minutes=20)
    assert is_prediction_allowed("Scheduled", START, "USA", "MEX", ref) is True


def test_prediction_not_allowed_when_locked():
    ref = START - timedelta(minutes=10)
    assert is_prediction_allowed("Scheduled", START, "USA", "MEX", ref) is False


def test_prediction_not_allowed_when_finished():
    ref = START + timedelta(hours=2)
    assert is_prediction_allowed("Finished", START, "USA", "MEX", ref) is False


def test_prediction_not_allowed_when_pending_teams():
    ref = START - timedelta(days=1)
    assert is_prediction_allowed("Scheduled", START, None, None, ref) is False


# ── is_bonus_locked ───────────────────────────────────────────────────────────

def test_bonus_not_locked_before_kickoff():
    kickoff = datetime(2026, 6, 11, 20, 0)
    ref = kickoff - timedelta(hours=1)
    assert is_bonus_locked(kickoff, ref) is False


def test_bonus_locked_at_kickoff():
    kickoff = datetime(2026, 6, 11, 20, 0)
    assert is_bonus_locked(kickoff, kickoff) is True


def test_bonus_locked_after_kickoff():
    kickoff = datetime(2026, 6, 11, 20, 0)
    ref = kickoff + timedelta(minutes=5)
    assert is_bonus_locked(kickoff, ref) is True
