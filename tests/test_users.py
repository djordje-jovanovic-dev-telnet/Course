from jose import jwt
from app import schemas
from app.config import settings
import pytest


def test_root(client):
    res = client.get("/")
    print(res.json().get("message"))
    assert res.json().get("message") == "Hey"
    assert res.status_code == 200


def test_create_user(client):
    res = client.post("/users/", json={"email": "jovica@gmail.com", "password": "1234"})
    new_user = schemas.UserOut(**res.json())
    assert new_user.email == "jovica@gmail.com"
    assert res.status_code == 201


def test_login_user(test_user, client):
    res = client.post(
        "/login",
        data={"username": test_user["email"], "password": test_user["password"]},
    )
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(
        login_res.access_token, settings.secret_key, algorithms=[settings.algorithm]
    )
    id_: str = payload.get("user_id")
    assert id_ == test_user["id"]
    assert login_res.token_type == "bearer"
    assert res.status_code == 200


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("wr@gmail.com", "1234", 403),
        ("jovica@gmail.com", "wrong", 403),
        ("wr@gmail.com", "wrong", 403),
        (None, "1234", 422),
        ("jovica@gmail.com", None, 422),
    ],
)
def test_incorrect_login(client, email, password, status_code):
    res = client.post("/login", data={"username": email, "password": password})
    assert res.status_code == status_code
