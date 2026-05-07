from app.auth import hash_password, verify_password, create_access_token
from jose import jwt
import os


def test_hash_and_verify_roundtrip():
    hashed = hash_password("mysecret")
    assert hashed != "mysecret"
    assert verify_password("mysecret", hashed)
    assert not verify_password("wrongpass", hashed)


def test_create_access_token_contains_sub():
    token = create_access_token({"sub": "42"})
    payload = jwt.decode(token, os.getenv("SECRET_KEY", "dev-secret-key-change-in-prod"), algorithms=["HS256"])
    assert payload["sub"] == "42"
    assert "exp" in payload


def test_register_creates_pending_user(client):
    resp = client.post("/auth/register", json={"username": "newuser", "password": "pass123"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "newuser"
    assert "id" in data


def test_register_duplicate_username(client, active_user):
    resp = client.post("/auth/register", json={"username": "testuser", "password": "other"})
    assert resp.status_code == 400
    assert "already registered" in resp.json()["detail"]


def test_login_success_active_user(client, active_user):
    resp = client.post("/auth/login", json={"username": "testuser", "password": "password123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()
    assert resp.json()["token_type"] == "bearer"


def test_login_fails_for_pending_user(client, pending_user):
    resp = client.post("/auth/login", json={"username": "pendinguser", "password": "password123"})
    assert resp.status_code == 401
    assert "pending" in resp.json()["detail"].lower()


def test_login_wrong_password(client, active_user):
    resp = client.post("/auth/login", json={"username": "testuser", "password": "wrongpass"})
    assert resp.status_code == 401


def test_get_me_returns_profile(client, auth_headers):
    resp = client.get("/users/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "testuser"
    assert data["total_points"] == 0
    assert data["is_admin"] is False


def test_get_me_unauthorized_without_token(client):
    resp = client.get("/users/me")
    assert resp.status_code == 401


# ── Ranking ───────────────────────────────────────────────────────────────────

def test_ranking_returns_only_active_users(client, db, auth_headers):
    from app.models import User
    from app.auth import hash_password

    # Add a pending and a rejected user — should not appear in ranking
    db.add(User(username="pending1", password_hash=hash_password("x"), status="Pending"))
    db.add(User(username="rejected1", password_hash=hash_password("x"), status="Rejected"))
    db.commit()

    resp = client.get("/users/ranking", headers=auth_headers)
    assert resp.status_code == 200
    usernames = [e["username"] for e in resp.json()]
    assert "testuser" in usernames
    assert "pending1" not in usernames
    assert "rejected1" not in usernames


def test_ranking_order_by_points_then_exact_then_name(client, db, auth_headers):
    from app.models import User
    from app.auth import hash_password

    db.add(User(username="aaa", password_hash=hash_password("x"), status="Active", total_points=10, exact_scores=2))
    db.add(User(username="bbb", password_hash=hash_password("x"), status="Active", total_points=10, exact_scores=3))
    db.add(User(username="ccc", password_hash=hash_password("x"), status="Active", total_points=15, exact_scores=0))
    db.commit()

    resp = client.get("/users/ranking", headers=auth_headers)
    assert resp.status_code == 200
    entries = resp.json()
    names = [e["username"] for e in entries]
    # ccc(15pts) > bbb(10pts,3ex) > aaa(10pts,2ex) > testuser(0pts)
    assert names.index("ccc") < names.index("bbb")
    assert names.index("bbb") < names.index("aaa")


def test_me_includes_rank(client, auth_headers):
    resp = client.get("/users/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["rank"] == 1  # only user in ranking
