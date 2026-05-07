from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import auth, users, matches, predictions, bonus, admin

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Quiniela Mundial 2026", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(matches.router, prefix="/matches", tags=["matches"])
app.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
app.include_router(bonus.router, tags=["bonus"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
