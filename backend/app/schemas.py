from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreated(BaseModel):
    id: int
    username: str

    model_config = {"from_attributes": True}


# ── Users ─────────────────────────────────────────────────────────────────────

class UserMe(BaseModel):
    id: int
    username: str
    is_admin: bool
    status: str
    total_points: int
    exact_scores: int
    rank: Optional[int] = None

    model_config = {"from_attributes": True}

    @field_validator("is_admin", mode="before")
    @classmethod
    def coerce_bool(cls, v: object) -> bool:
        return bool(v)


class RankingEntry(BaseModel):
    rank: int
    user_id: int
    username: str
    total_points: int
    exact_scores: int


# ── Matches ───────────────────────────────────────────────────────────────────

class PredictionInMatch(BaseModel):
    home_score_guess: int
    away_score_guess: int
    points_earned: Optional[int]


class MatchOut(BaseModel):
    id: int
    home_team: Optional[str]
    away_team: Optional[str]
    home_team_code: Optional[str]
    away_team_code: Optional[str]
    home_team_placeholder: Optional[str]
    away_team_placeholder: Optional[str]
    start_time: datetime
    phase: str
    group_name: Optional[str]
    matchday: Optional[int]
    venue: Optional[str]
    status: str  # computed: Open/Locked/Finished/Pending Teams
    home_score_final: Optional[int]
    away_score_final: Optional[int]
    my_prediction: Optional[PredictionInMatch] = None

    model_config = {"from_attributes": True}


class MatchCreate(BaseModel):
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    home_team_code: Optional[str] = None
    away_team_code: Optional[str] = None
    home_team_placeholder: Optional[str] = None
    away_team_placeholder: Optional[str] = None
    start_time: datetime
    phase: str
    group_name: Optional[str] = None
    matchday: Optional[int] = None
    venue: Optional[str] = None


class MatchUpdate(BaseModel):
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    home_team_code: Optional[str] = None
    away_team_code: Optional[str] = None
    home_team_placeholder: Optional[str] = None
    away_team_placeholder: Optional[str] = None
    start_time: Optional[datetime] = None
    venue: Optional[str] = None


# ── Predictions ───────────────────────────────────────────────────────────────

class PredictionCreate(BaseModel):
    match_id: int
    home_score_guess: int
    away_score_guess: int
    simulated_time: Optional[str] = None


class PredictionOut(BaseModel):
    id: int
    match_id: int
    home_score_guess: int
    away_score_guess: int
    points_earned: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FriendPrediction(BaseModel):
    username: str
    home_score_guess: int
    away_score_guess: int
    points_earned: Optional[int]


# ── Bonus ─────────────────────────────────────────────────────────────────────

class BonusQuestionOut(BaseModel):
    question_type: str
    question_text: str
    points_reward: int
    is_locked: bool
    my_prediction: Optional[str] = None


class BonusPredictionCreate(BaseModel):
    question_type: str
    prediction_text: str


class BonusPredictionOut(BaseModel):
    question_type: str
    prediction_text: str
    points_earned: Optional[int]

    model_config = {"from_attributes": True}


# ── Admin ─────────────────────────────────────────────────────────────────────

class MatchResult(BaseModel):
    home_score_final: int
    away_score_final: int


class ResultResponse(BaseModel):
    match_id: int
    home_score_final: int
    away_score_final: int
    predictions_updated: int


class BonusValidate(BaseModel):
    points_earned: int


class AdminUserOut(BaseModel):
    id: int
    username: str
    status: str
    total_points: int
    exact_scores: int
    created_at: datetime

    model_config = {"from_attributes": True}
