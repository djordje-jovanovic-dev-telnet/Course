from .database import client, session
from app import schemas


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
    
def test_login_user(client):
    res = client.post("/login", data={"username": "jovica@gmail.com", "password": "1234"})
    print(res.json())
    assert res.status_code == 200
    
