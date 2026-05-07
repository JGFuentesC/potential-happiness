from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import BonusPrediction, Match, User
from app.auth import get_current_user
from app.schemas import BonusQuestionOut, BonusPredictionCreate, BonusPredictionOut
from app.time_utils import get_reference_time, is_bonus_locked

router = APIRouter()

BONUS_QUESTIONS = [
    {
        "question_type": "Champion",
        "question_text": "¿Quién será el Campeón del Mundial 2026?",
        "points_reward": 20,
    },
    {
        "question_type": "TopScorer",
        "question_text": "¿Quién ganará la Bota de Oro?",
        "points_reward": 15,
    },
]


def _get_kickoff(db: Session):
    first = db.query(Match).order_by(Match.start_time.asc()).first()
    return first.start_time if first else None


@router.get("/bonus-questions", response_model=list[BonusQuestionOut])
def list_bonus_questions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    ref_time = get_reference_time()
    kickoff = _get_kickoff(db)
    locked = is_bonus_locked(kickoff, ref_time) if kickoff else False

    my_preds = {
        bp.question_type: bp.prediction_text
        for bp in db.query(BonusPrediction).filter(BonusPrediction.user_id == current_user.id).all()
    }
    return [
        {
            **q,
            "is_locked": locked,
            "my_prediction": my_preds.get(q["question_type"]),
        }
        for q in BONUS_QUESTIONS
    ]


@router.post("/bonus-predictions", response_model=BonusPredictionOut)
def upsert_bonus(
    body: BonusPredictionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BonusPrediction:
    ref_time = get_reference_time()
    kickoff = _get_kickoff(db)
    if kickoff and is_bonus_locked(kickoff, ref_time):
        raise HTTPException(status_code=403, detail="Bonus predictions are locked.")

    valid_types = {q["question_type"] for q in BONUS_QUESTIONS}
    if body.question_type not in valid_types:
        raise HTTPException(status_code=400, detail="Invalid question type")

    bp = (
        db.query(BonusPrediction)
        .filter(BonusPrediction.user_id == current_user.id, BonusPrediction.question_type == body.question_type)
        .first()
    )
    if bp:
        bp.prediction_text = body.prediction_text
    else:
        bp = BonusPrediction(
            user_id=current_user.id,
            question_type=body.question_type,
            prediction_text=body.prediction_text,
        )
        db.add(bp)
    db.commit()
    db.refresh(bp)
    return bp
