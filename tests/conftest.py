from fastapi.testclient import TestClient
from app.database import get_db, Base
from app.main import app
from app.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from app import models

from app.oauth2 import create_access_token

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}/{settings.database_name}_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

client = TestClient(app)


@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


# @pytest.fixture
# def test_user(client):
#     user_data = {"email": "jovica@gmail.com", "password": "1234"}
#     res = client.post("/users/", json=user_data)
#     assert res.status_code == 201
#     new_user = res.json()
#     new_user["password"] = user_data["password"]
#     return new_user


@pytest.fixture
def test_user_(client):
    user_data = {"email": "djordje@gmail.com", "password": "1234"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def test_user_(client):
    user_data = {"email": "djordje@gmail.com", "password": "1234"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def token(test_follow_users_data):
    return create_access_token({"user_id": test_follow_users_data[0]["id"]})


@pytest.fixture
def authorized_client(client, token):
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest.fixture
def test_posts(test_user, session, test_user_):
    posts_data = [
        {
            "title": "first title",
            "content": "first content",
            "owner_id": test_user["id"],
        },
        {
            "title": "second title",
            "content": "second content",
            "owner_id": test_user["id"],
        },
        {
            "title": "third title",
            "content": "third content",
            "owner_id": test_user["id"],
        },
        {
            "title": "forth title",
            "content": "forth content",
            "owner_id": test_user_["id"],
        },
        {
            "title": "fifth title",
            "content": "fifth content",
            "owner_id": test_user_["id"],
        },
    ]

    def create_post_model(p):
        return models.Post(**p)

    post_map = map(create_post_model, posts_data)
    posts = list(post_map)
    session.add_all(posts)
    session.commit()
    post = session.query(models.Post).all()
    return post
