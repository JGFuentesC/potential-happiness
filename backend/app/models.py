from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    is_admin = Column(Integer, nullable=False, default=0)
    status = Column(String, nullable=False, default="Pending")  # Pending/Active/Rejected
    total_points = Column(Integer, nullable=False, default=0)
    exact_scores = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    predictions = relationship("Prediction", back_populates="user", cascade="all, delete")
    bonus_predictions = relationship("BonusPrediction", back_populates="user", cascade="all, delete")


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    home_team = Column(String, nullable=True)
    away_team = Column(String, nullable=True)
    home_team_code = Column(String, nullable=True)
    away_team_code = Column(String, nullable=True)
    home_team_placeholder = Column(String, nullable=True)
    away_team_placeholder = Column(String, nullable=True)
    start_time = Column(DateTime, nullable=False)
    phase = Column(String, nullable=False)  # Groups/R32/R16/QF/SF/ThirdPlace/Final
    group_name = Column(String, nullable=True)   # A-L, solo Groups
    matchday = Column(Integer, nullable=True)    # 1-3, solo Groups
    venue = Column(String, nullable=True)
    home_score_final = Column(Integer, nullable=True)
    away_score_final = Column(Integer, nullable=True)
    status = Column(String, nullable=False, default="Scheduled")  # Scheduled/Finished
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    predictions = relationship("Prediction", back_populates="match", cascade="all, delete")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    home_score_guess = Column(Integer, nullable=False)
    away_score_guess = Column(Integer, nullable=False)
    points_earned = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (UniqueConstraint("user_id", "match_id"),)

    user = relationship("User", back_populates="predictions")
    match = relationship("Match", back_populates="predictions")


class BonusPrediction(Base):
    __tablename__ = "bonus_predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question_type = Column(String, nullable=False)  # Champion/TopScorer
    prediction_text = Column(String, nullable=False)
    points_earned = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("user_id", "question_type"),)

    user = relationship("User", back_populates="bonus_predictions")
