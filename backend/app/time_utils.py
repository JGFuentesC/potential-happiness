import os
from datetime import datetime, timedelta
from typing import Optional

LOCK_WINDOW_MINUTES = 15


def get_reference_time(simulated_time: Optional[str] = None) -> datetime:
    if simulated_time and os.getenv("ENABLE_TIME_TRAVEL", "False") == "True":
        return datetime.fromisoformat(simulated_time)
    return datetime.utcnow()


def compute_match_status(
    db_status: str,
    start_time: datetime,
    home_team: Optional[str],
    away_team: Optional[str],
    home_team_placeholder: Optional[str],
    away_team_placeholder: Optional[str],
    ref_time: datetime,
) -> str:
    if db_status == "Finished":
        return "Finished"
    # Eliminatoria sin equipos asignados
    if home_team is None and away_team is None:
        return "Pending Teams"
    lock_threshold = start_time - timedelta(minutes=LOCK_WINDOW_MINUTES)
    if ref_time >= lock_threshold:
        return "Locked"
    return "Open"


def is_prediction_allowed(
    db_status: str,
    start_time: datetime,
    home_team: Optional[str],
    away_team: Optional[str],
    ref_time: datetime,
) -> bool:
    status = compute_match_status(
        db_status, start_time, home_team, away_team, None, None, ref_time
    )
    return status == "Open"


def is_bonus_locked(kickoff: datetime, ref_time: datetime) -> bool:
    return ref_time >= kickoff
