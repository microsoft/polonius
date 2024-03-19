import pytest

#from flaskapp import models


@pytest.fixture
def client(app_with_db):
    return app_with_db.test_client()


def test_index(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Welcome to Project Polonius" in response.data
