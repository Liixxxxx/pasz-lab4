from sqlalchemy import update

from app.models import Resource, User

PASSWORD = "Qwerty1!x"


def login_as(client, session_factory, login, clearance):
    client.post("/api/register", json={"login": login, "password": PASSWORD})
    with session_factory() as db:
        db.execute(update(User).where(User.login == login).values(clearance=clearance))
        db.commit()
    r = client.post("/api/login", json={"login": login, "password": PASSWORD})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def add_resource(session_factory, classification):
    with session_factory() as db:
        res = Resource(title=f"doc {classification}", content="text", classification=classification)
        db.add(res)
        db.commit()
        return res.id


def test_access_allowed(client, session_factory):
    headers = login_as(client, session_factory, "tania", "confidential")
    res_id = add_resource(session_factory, "internal")
    r = client.get(f"/api/resources/{res_id}", headers=headers)
    assert r.status_code == 200
    assert r.json()["content"] == "text"


def test_access_denied(client, session_factory):
    headers = login_as(client, session_factory, "tania", "internal")
    res_id = add_resource(session_factory, "secret")
    r = client.get(f"/api/resources/{res_id}", headers=headers)
    assert r.status_code == 403
    assert r.json() == {"detail": "недостаточный уровень допуска"}


def test_resource_list_flags(client, session_factory):
    headers = login_as(client, session_factory, "tania", "internal")
    for level in ("public", "internal", "confidential", "secret"):
        add_resource(session_factory, level)
    r = client.get("/api/resources", headers=headers)
    flags = {item["classification"]: item["allowed"] for item in r.json()}
    assert flags == {"public": True, "internal": True, "confidential": False, "secret": False}


def test_resources_require_login(client):
    r = client.get("/api/resources")
    assert r.status_code == 401


def test_login_wrong_password(client):
    client.post("/api/register", json={"login": "tania", "password": PASSWORD})
    r = client.post("/api/login", json={"login": "tania", "password": "Wrong1!pass"})
    assert r.status_code == 401
