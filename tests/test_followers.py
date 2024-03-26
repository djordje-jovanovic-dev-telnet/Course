import pytest
from app import models


@pytest.fixture
def test_user(client):
    user_data = {"email": "jovica@gmail.com", "password": "1234"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user


# @pytest.fixture
# def test_users(session):
#     user_data_list = [
#         {"id": 1, "email": "djo@gmail.com", "password": "1234"},
#         {"id": 2, "email": "mik@gmail.com", "password": "1234"},
#         {"id": 3, "email": "rok@gmail.com", "password": "1234"},
#         {"id": 4, "email": "ste@gmail.com", "password": "1234"},
#         {"id": 5, "email": "jov@gmail.com", "password": "1234"},
#         {"id": 6, "email": "ziv@gmail.com", "password": "1234"},
#     ]
# def create_users_model(p):
#     return models.User(**p)

# user_map = map(create_users_model, user_data)
# users = list(user_map)
# session.add_all(users)
# session.commit()
# user = session.query(models.User).all()
# return user

# @pytest.fixture()
# def test_follow(session, test_follow_users_data):
#     new_follow = models.Follow(
#         follow_user_id=2, user_id=1
#     )
#     session.add(new_follow)
#     session.commit()
#     return new_follow


@pytest.fixture()
def test_follow_users_data(client):
    user_data = [
        {"email": "djo@gmail.com", "password": "1234"},
        {"email": "mik@gmail.com", "password": "1234"},
        {"email": "rok@gmail.com", "password": "1234"},
        {"email": "ste@gmail.com", "password": "1234"},
        {"email": "jov@gmail.com", "password": "1234"},
        {"email": "ziv@gmail.com", "password": "1234"},
        {"email": "kos@gmail.com", "password": "1234"},
        {"email": "joca@gmail.com", "password": "1234"},
    ]

    new_users = []

    for user_data in user_data:
        res = client.post("/users/", json=user_data)
        assert res.status_code == 201
        new_user = res.json()
        new_user["password"] = user_data["password"]
        new_users.append(new_user)

    return new_users


def test_self_follow(authorized_client, test_follow_users_data):
    res = authorized_client.post(
        "/follow/", json={"followed_user_id": test_follow_users_data[0]["id"], "dir": 1}
    )
    assert res.status_code == 403


def test_self_unfollow(authorized_client, test_follow_users_data):
    res = authorized_client.post(
        "/follow/", json={"followed_user_id": test_follow_users_data[0]["id"], "dir": 0}
    )
    assert res.status_code == 403


def test_user_follow_user(authorized_client, test_follow_users_data):
    res = authorized_client.post(
        "/follow/", json={"followed_user_id": test_follow_users_data[3]["id"], "dir": 1}
    )
    assert res.status_code == 201


def test_user_unfollow_user(authorized_client, test_follow_users_data):
    authorized_client.post(
        "/follow/", json={"followed_user_id": test_follow_users_data[3]["id"], "dir": 1}
    )
    res = authorized_client.post(
        "/follow/", json={"followed_user_id": test_follow_users_data[3]["id"], "dir": 0}
    )
    assert res.status_code == 201


def test_follow_already_followed(authorized_client, test_follow_users_data):
    authorized_client.post(
        "/follow/", json={"followed_user_id": test_follow_users_data[3]["id"], "dir": 1}
    )
    res = authorized_client.post(
        "/follow/", json={"followed_user_id": test_follow_users_data[3]["id"], "dir": 1}
    )
    assert res.status_code == 409


def test_unfollow_already_unfollowed(authorized_client, test_follow_users_data):
    authorized_client.post(
        "/follow/", json={"followed_user_id": test_follow_users_data[2]["id"], "dir": 1}
    )
    authorized_client.post(
        "/follow/", json={"followed_user_id": test_follow_users_data[2]["id"], "dir": 0}
    )
    res = authorized_client.post(
        "/follow/", json={"followed_user_id": test_follow_users_data[2]["id"], "dir": 0}
    )
    assert res.status_code == 409


def test_follow_non_existing_user(authorized_client):
    res = authorized_client.post("/follow/", json={"followed_user_id": 77, "dir": 1})
    assert res.status_code == 404


def test_unfollow_non_existing_user(authorized_client):
    res = authorized_client.post("/follow/", json={"followed_user_id": 77, "dir": 0})
    assert res.status_code == 404
