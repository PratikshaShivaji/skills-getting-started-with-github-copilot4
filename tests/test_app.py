import copy
import pytest
from starlette.testclient import TestClient

import src.app as app_module
from src.app import app


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the activities dict to its original state after each test."""
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(original)


@pytest.fixture
def client():
    return TestClient(app)


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert expected_activity in data


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_signup_success(client):
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_already_registered(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # already in seed data

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_unknown_activity(client):
    # Arrange
    activity_name = "Underwater Basket Weaving"
    email = "anyone@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_unregister_success(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # already enrolled in seed data

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email not in app_module.activities[activity_name]["participants"]


def test_unregister_not_enrolled(client):
    # Arrange
    activity_name = "Chess Club"
    email = "nobody@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert "not signed up" in response.json()["detail"]


def test_unregister_unknown_activity(client):
    # Arrange
    activity_name = "Underwater Basket Weaving"
    email = "anyone@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]
