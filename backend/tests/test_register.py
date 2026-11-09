from sqlalchemy import select

from app.models import User

GOOD = {"login": "tania", "password": "Qwerty1!x"}


def test_register_success(client):
    r = client.post("/api/register", json=GOOD)
    assert r.status_code == 201
    assert r.json() == {"message": "user создан"}


def test_register_duplicate_login(client):
    client.post("/api/register", json=GOOD)
    r = client.post("/api/register", json=GOOD)
    assert r.status_code == 409
    assert r.json() == {"detail": "логин уже занят"}


def test_register_weak_password(client):
    r = client.post("/api/register", json={"login": "tania", "password": "qwerty"})
    assert r.status_code == 422
    assert "пароль" in r.json()["detail"]


def test_password_is_hashed(client, session_factory):
    client.post("/api/register", json=GOOD)
    with session_factory() as db:
        user = db.scalar(select(User).where(User.login == "tania"))
    assert user.password_hash.startswith("$argon2id$")
    assert GOOD["password"] not in user.password_hash
